"""Score one finished dialogue against private annotations and the restaurant catalog."""

from collections.abc import Sequence
from dataclasses import dataclass
from itertools import product
import re

from .dialogue_types import Restaurant
from .state_scoring import score_states


# v2: a question is useful only if it asks about something that is still
# unclear (an unresolved slot not yet answered) while no safe recommendation
# exists; questions are judged at every step, not only the first one, so
# two-question scenarios and wasted follow-up questions are scored.
SCORER_VERSION = "v2"
CONSTRAINT_SLOTS = {"cuisine", "exclude_cuisine", "max_price", "location", "vegetarian", "dinner"}


def _cuisines(value: str | list[str] | None) -> list[str]:
    if value is None:
        return []
    return [value] if isinstance(value, str) else value


def constraint_violations(restaurant: Restaurant, goal: dict) -> list[str]:
    """Apply the hard constraints used by the NLP.zip benchmark."""
    extra = goal.keys() - CONSTRAINT_SLOTS
    if extra:
        raise ValueError(f"Unknown constraint slots: {', '.join(sorted(extra))}")

    cuisine = goal.get("cuisine")
    max_price = goal.get("max_price")
    location = goal.get("location")
    if location not in (None, "station", "mall"):
        raise ValueError(f"Unknown location in annotation: {location!r}")

    violations = []
    if cuisine is not None and restaurant["cuisine"] not in _cuisines(cuisine):
        violations.append("cuisine")
    if restaurant["cuisine"] in _cuisines(goal.get("exclude_cuisine")):
        violations.append("exclude_cuisine")
    if max_price is not None and restaurant["price_per_person"] > max_price:
        violations.append("max_price")
    if location is not None and not restaurant[f"near_{location}"]:
        violations.append("location")
    if goal.get("vegetarian") and not restaurant["vegetarian_options"]:
        violations.append("vegetarian")
    if goal.get("dinner") and not restaurant["open_for_dinner"]:
        violations.append("dinner")
    return violations


def _turn_number(turn: object) -> int | None:
    if type(turn) is int and turn > 0:
        return turn
    if isinstance(turn, str) and re.fullmatch(r"t[0-9]+", turn):
        return int(turn[1:]) or None
    return None


@dataclass(frozen=True)
class _Checkpoint:
    """The annotated decision point at the end of the fixed dialogue prefix."""

    turn: int
    active: dict
    unresolved: tuple
    hidden: dict
    needed_slots: frozenset
    database: tuple

    def shared_after(self, answered: frozenset | set = frozenset()) -> set[str]:
        """Restaurants valid under every remaining reading, once the slots in
        `answered` have been clarified (the scripted user reveals the hidden value)."""
        options = []
        for item in self.unresolved:
            interpretations = item["interpretations"]
            if item["slot"] in answered:
                matching = [i for i in interpretations
                            if all(self.hidden.get(k) == v for k, v in i.items())]
                interpretations = matching or interpretations
            options.append(interpretations)
        sets = []
        for choice in product(*options):
            goal = dict(self.active)
            for interpretation in choice:
                goal.update(interpretation)
            sets.append({r["restaurant_id"] for r in self.database if not constraint_violations(r, goal)})
        return set.intersection(*sets) if sets else set()

    @property
    def shared_candidates(self) -> set[str]:
        return self.shared_after()

    @property
    def expected_action(self) -> str | None:
        if self.shared_candidates:
            return "RECOMMEND"
        return "ASK" if self.needed_slots else None

    def matches(self, step: dict) -> bool:
        return _turn_number(step.get("context_turn_id")) == self.turn


def _initial_checkpoint(gold: dict, database: Sequence[Restaurant]) -> _Checkpoint | None:
    state = gold.get("gold_dialogue_state")
    if not state or (turn := _turn_number(state.get("at_turn"))) is None:
        return None
    active = state.get("active")
    unresolved = state.get("unresolved")
    if active is None or unresolved is None:
        return None
    if not all(item.get("interpretations") for item in unresolved):
        return None
    checkpoint = _Checkpoint(turn, dict(active), tuple(unresolved), dict(gold.get("hidden_user_goal") or {}),
                             frozenset(), tuple(database))
    decision = gold.get("gold_decision") or {}
    needed = frozenset()
    if not checkpoint.shared_candidates and decision.get("should_ask") is True:
        named = [q for q in (decision.get("necessary_questions") or [decision.get("necessary_question")])
                 if isinstance(q, str)]
        named_slots = {q.partition("@")[0] for q in named}
        answer_table = gold.get("predefined_clarification_answers") or {}
        needed = frozenset(
            item["slot"] for item in unresolved
            if (not named_slots or item["slot"] in named_slots) and answer_table.get(item["slot"])
        )
    return _Checkpoint(turn, dict(active), tuple(unresolved), checkpoint.hidden, needed, tuple(database))


def _judge_question(
    slot: str,
    status: str,
    checkpoint: _Checkpoint | None,
    shared_now: set[str] | None,
    answered: set[str],
    duplicate: bool,
) -> tuple[str, str]:
    """Right-question rule: useful only if it asks about a still-unclear slot."""
    if duplicate:
        return "unnecessary", "duplicate_target"
    if status == "fallback":
        return "unnecessary", "fallback_reply"
    if checkpoint is None or checkpoint.expected_action is None:
        return "unjudged", "missing_checkpoint_annotation"
    if shared_now:
        return "unnecessary", "shared_candidate_exists"
    if slot in checkpoint.needed_slots and slot not in answered:
        return "useful", "clarifies_needed_target"
    return "unnecessary", "not_needed_target"


def _score_questions(steps: list[dict], checkpoint: _Checkpoint | None) -> list[dict]:
    scores = []
    answered: set[str] = set()
    # Judge every step once the run started at the annotated checkpoint; the
    # pipeline only appends question/answer turns after the fixed prefix.
    started = checkpoint is not None and bool(steps) and checkpoint.matches(steps[0])
    for step in steps:
        step_checkpoint = checkpoint if started else None
        shared_now = checkpoint.shared_after(answered) if step_checkpoint else None
        slots_in_step: set[str] = set()
        newly_answered = set()
        for delivery in step["delivered_questions"]:
            question = delivery["question"]
            slot = question["slot"]
            reply_status = delivery["reply"]["status"]
            judgment, reason = _judge_question(
                slot, reply_status, step_checkpoint, shared_now, answered,
                slot in answered or slot in slots_in_step,
            )
            slots_in_step.add(slot)
            if reply_status == "answered":
                newly_answered.add(slot)
            scores.append({
                "step_id": step["step_id"],
                "question_id": delivery["question_id"],
                "slot": slot,
                "reference_turn_id": question.get("reference_turn_id"),
                "reply_status": reply_status,
                "judgment": judgment,
                "reason": reason,
            })
        answered |= newly_answered
    return scores


def _initial_action_matches(step: dict, checkpoint: _Checkpoint | None) -> bool | None:
    action = step.get("action")
    if not action or checkpoint is None or not checkpoint.matches(step):
        return None
    expected = checkpoint.expected_action
    if expected is None or (expected == "ASK" and step["budget_before"] == 0):
        return None
    if action["type"] != expected:
        return False
    if expected == "ASK":
        delivered = step["delivered_questions"]
        slots = [d["question"]["slot"] for d in delivered]
        return (
            bool(delivered)
            and len(set(slots)) == len(slots)
            and all(slot in checkpoint.needed_slots for slot in slots)
            and all(d["reply"]["status"] == "answered" for d in delivered)
        )
    return True


def _missed_clarification(
    final_step: dict,
    valid_recommendation: bool,
    checkpoint: _Checkpoint | None,
) -> tuple[bool | None, str]:
    if not valid_recommendation:
        return None, "no_valid_recommendation"
    if not final_step["budget_before"]:
        return None, "budget_exhausted"
    if checkpoint is None or not checkpoint.matches(final_step) or checkpoint.expected_action is None:
        return None, "missing_checkpoint_annotation"
    if checkpoint.needed_slots:
        return True, "needed_clarification_skipped"
    return False, "shared_candidate_available"


def score(run_record: dict, gold: dict, database: Sequence[Restaurant]) -> dict:
    """Score a run offline. A pipeline failure remains a scored task failure."""
    if run_record["scenario_id"] != gold["scenario_id"]:
        raise ValueError(f"Annotation scenario does not match run {run_record['run_id']}")
    if not database or not run_record["steps"]:
        raise ValueError("Scoring requires a restaurant catalog and at least one recorded decision")

    steps = run_record["steps"]
    checkpoint = _initial_checkpoint(gold, database)
    recommendation = run_record["final_recommendation"] or {}
    restaurant_id = recommendation.get("restaurant_id")
    restaurant = next((row for row in database if row["restaurant_id"] == restaurant_id), None)
    valid_recommendation = run_record["termination_reason"] == "completed" and restaurant is not None
    goal = gold["hidden_user_goal"]
    violations = constraint_violations(restaurant, goal) if valid_recommendation else None

    question_scores = _score_questions(steps, checkpoint)
    missed, missed_reason = _missed_clarification(steps[-1], valid_recommendation, checkpoint)
    initial_shared = None
    if valid_recommendation and (steps[0].get("action") or {}).get("type") == "RECOMMEND":
        if checkpoint is not None and checkpoint.matches(steps[0]):
            initial_shared = restaurant_id in checkpoint.shared_candidates
    useful_slots = {q["slot"] for q in question_scores if q["judgment"] == "useful"}

    return {
        "run_id": run_record["run_id"],
        "scenario_id": run_record["scenario_id"],
        "template_family_id": gold["template_family_id"],
        "scenario_type": gold["scenario_type"],
        "system_id": run_record["system_id"],
        "budget": run_record["budget"],
        "repeat": run_record["repeat"],
        "scorer_version": SCORER_VERSION,
        "termination_reason": run_record["termination_reason"],
        "task_success": valid_recommendation and violations == [],
        "restaurant_id": restaurant_id,
        "confidence": recommendation.get("confidence"),
        "violated_constraints": violations,
        "expected_initial_action": checkpoint.expected_action if checkpoint else None,
        "initial_action_matches": _initial_action_matches(steps[0], checkpoint),
        "initial_recommendation_shared": initial_shared,
        "question_counts": {
            "attempted": sum(
                len(action["questions"])
                for step in steps
                if (action := step.get("action")) and action["type"] == "ASK"
            ),
            "delivered": len(question_scores),
            "judged": sum(item["judgment"] != "unjudged" for item in question_scores),
            "unnecessary": sum(item["judgment"] == "unnecessary" for item in question_scores),
        },
        "useful_questions": sum(item["judgment"] == "useful" for item in question_scores),
        "questions_needed": (gold.get("computed_by_validator") or {}).get("questions_needed"),
        "needed_slots": sorted(checkpoint.needed_slots) if checkpoint else [],
        "all_needed_slots_clarified": (
            None if not checkpoint or not checkpoint.needed_slots
            else checkpoint.needed_slots <= useful_slots
        ),
        "question_scores": question_scores,
        "missed_useful_clarification": missed,
        "missed_clarification_reason": missed_reason,
        "state_metrics": score_states(run_record, gold),
        "usage": {field: run_record.get("usage", {}).get(field) for field in ("input_tokens", "output_tokens", "model_calls")},
    }
