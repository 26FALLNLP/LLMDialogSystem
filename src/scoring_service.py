"""Score one finished dialogue against private annotations and the restaurant catalog."""

from collections.abc import Sequence
from dataclasses import dataclass
from itertools import product
import re

from .dialogue_types import Restaurant
from .state_scoring import score_states


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


def _question_target(question: dict) -> tuple[str, int | None]:
    return question["slot"], _turn_number(question.get("reference_turn_id"))


@dataclass(frozen=True)
class _Checkpoint:
    turn: int
    shared_candidates: set[str]
    needed_targets: set[tuple[str, int]]

    @property
    def expected_action(self) -> str | None:
        if self.shared_candidates:
            return "RECOMMEND"
        return "ASK" if self.needed_targets else None

    def matches(self, step: dict) -> bool:
        return _turn_number(step.get("context_turn_id")) == self.turn


def _initial_checkpoint(
    gold: dict,
    database: Sequence[Restaurant],
    resolved: dict | None = None,
    context_turn: int | None = None,
) -> _Checkpoint | None:
    state = gold.get("gold_dialogue_state")
    if not state or (turn := _turn_number(state.get("at_turn"))) is None:
        return None
    active = state.get("active")
    unresolved = state.get("unresolved")
    if active is None or unresolved is None:
        return None
    interpretations = [item.get("interpretations") for item in unresolved]
    if not all(interpretations):
        return None
    resolved = resolved or {}
    combined_goals = (
        {**active, **{slot: value for option in options for slot, value in option.items()}}
        for options in product(*interpretations)
    )
    candidate_sets = [
        {restaurant["restaurant_id"] for restaurant in database if not constraint_violations(restaurant, goal)}
        for goal in combined_goals if all(goal.get(slot) == value for slot, value in resolved.items())
    ]
    if not candidate_sets:
        return None
    shared = set.intersection(*candidate_sets)
    decision = gold.get("gold_decision") or {}
    targets = decision.get("necessary_questions") if decision.get("score_followup_clarifications") else None
    if targets is None:
        targets = [decision.get("necessary_question")]
    needed_targets = set()
    if not shared and decision.get("should_ask") is True:
        answer_table = gold.get("predefined_clarification_answers") or {}
        for target in targets:
            if not isinstance(target, str):
                continue
            slot, _, reference = target.partition("@")
            target_turn = _turn_number(reference)
            if target_turn is not None and answer_table.get(slot) and slot not in resolved:
                needed_targets.add((slot, target_turn))
    return _Checkpoint(context_turn or turn, shared, needed_targets)


def _judge_question(
    target: tuple[str, int | None],
    status: str,
    checkpoint: _Checkpoint | None,
    duplicate: bool,
) -> tuple[str, str]:
    if duplicate:
        return "unnecessary", "duplicate_target"
    if status == "fallback":
        return "unnecessary", "fallback_reply"
    if checkpoint is None or checkpoint.expected_action is None:
        return "unjudged", "missing_checkpoint_annotation"
    if checkpoint.shared_candidates:
        return "unnecessary", "shared_candidate_exists"
    if target in checkpoint.needed_targets:
        return "useful", "clarifies_needed_target"
    return "unnecessary", "not_needed_target"


def _score_questions(
    steps: list[dict], checkpoint: _Checkpoint | None, gold: dict, database: Sequence[Restaurant],
) -> tuple[list[dict], _Checkpoint | None]:
    scores = []
    answered = set()
    resolved = {}
    followups = (gold.get("gold_decision") or {}).get("score_followup_clarifications") is True
    unresolved_slots = {
        item["slot"] for item in (gold.get("gold_dialogue_state") or {}).get("unresolved", [])
    }
    answer_table = gold.get("predefined_clarification_answers") or {}
    final_checkpoint = None
    for step in steps:
        targets_in_step = set()
        step_checkpoint = checkpoint if checkpoint and checkpoint.matches(step) else None
        if followups and checkpoint is not None:
            step_checkpoint = _initial_checkpoint(
                gold, database, resolved, _turn_number(step.get("context_turn_id")),
            )
        final_checkpoint = step_checkpoint
        for delivery in step["delivered_questions"]:
            question = delivery["question"]
            target = _question_target(question)
            reply_status = delivery["reply"]["status"]
            judgment, reason = _judge_question(
                target, reply_status, step_checkpoint, target in answered or target in targets_in_step
            )
            targets_in_step.add(target)
            if reply_status == "answered":
                answered.add(target)
            scores.append({
                "step_id": step["step_id"],
                "question_id": delivery["question_id"],
                "slot": question["slot"],
                "reference_turn_id": question.get("reference_turn_id"),
                "reply_status": reply_status,
                "judgment": judgment,
                "reason": reason,
            })
            slot = question["slot"]
            if (
                followups and reply_status == "answered" and slot in unresolved_slots
                and delivery["reply"].get("text") == answer_table.get(slot)
                and slot in gold["hidden_user_goal"]
            ):
                resolved[slot] = gold["hidden_user_goal"][slot]
    return scores, final_checkpoint


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
        return (
            len(delivered) == 1
            and _question_target(delivered[0]["question"]) in checkpoint.needed_targets
            and delivered[0]["reply"]["status"] == "answered"
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
    if checkpoint.needed_targets:
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

    question_scores, final_checkpoint = _score_questions(steps, checkpoint, gold, database)
    missed, missed_reason = _missed_clarification(steps[-1], valid_recommendation, final_checkpoint)
    initial_shared = None
    if valid_recommendation and (steps[0].get("action") or {}).get("type") == "RECOMMEND":
        if checkpoint is not None and checkpoint.matches(steps[0]):
            initial_shared = restaurant_id in checkpoint.shared_candidates

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
        "question_scores": question_scores,
        "missed_useful_clarification": missed,
        "missed_clarification_reason": missed_reason,
        "state_metrics": score_states(run_record, gold),
        "usage": {field: run_record.get("usage", {}).get(field) for field in ("input_tokens", "output_tokens", "model_calls")},
    }
