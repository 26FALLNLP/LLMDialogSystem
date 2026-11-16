"""Run one dialogue and retain both the transcript and the decisions behind it."""

from collections.abc import Mapping
from dataclasses import asdict

from .answer_service import AnswerService
from .data import Scenario
from .dialogue_types import (
    Ask,
    Decision,
    DialogueContext,
    ModelRequestError,
    Question,
    Recommend,
    Strategy,
    Turn,
    Usage,
)


def _add_usage(total: dict[str, int | None], current: Usage) -> None:
    for key, value in asdict(current).items():
        previous = total[key]
        total[key] = None if value is None or previous is None else previous + value


def run_dialogue(
    scenario: Scenario,
    strategy: Strategy,
    answer_service: AnswerService,
    budget: int,
    *,
    repeat: int = 1,
    strategy_config: Mapping[str, str | int | bool] | None = None,
) -> dict:
    if type(budget) is not int or budget not in (0, 1, 2):
        raise ValueError("The clarification budget must be 0, 1, or 2.")

    turns = list(scenario.turns)
    steps = []
    usage = asdict(Usage())
    remaining = budget
    questions_delivered = 0
    final_recommendation = None
    restaurant_ids = {restaurant["restaurant_id"] for restaurant in scenario.restaurants}

    while True:
        step = {
            "step_id": f"s{len(steps) + 1:02}",
            "context_turn_id": turns[-1].turn_id,
            "budget_before": remaining,
            "budget_after": remaining,
            "action": None,
            "delivered_questions": [],
        }
        steps.append(step)
        context = DialogueContext(
            turns=tuple(turns),
            restaurant_database=scenario.restaurants,
            remaining_budget=remaining,
            allowed_actions=("ASK", "RECOMMEND") if remaining else ("RECOMMEND",),
        )
        try:
            decision = strategy.decide(context)
        except ModelRequestError as exc:
            termination = "model_error"
            step["error"] = str(exc)
            _add_usage(usage, exc.usage)
            break
        except Exception as exc:
            termination = "model_error"
            step["error"] = f"{type(exc).__name__}: {exc}"
            usage = asdict(Usage(None, None, None))
            break

        if not isinstance(decision, Decision):
            termination = "invalid_action"
            step["error"] = "The strategy must return a Decision."
            break

        _add_usage(usage, decision.usage)
        if decision.state_snapshot is not None:
            step["state_snapshot"] = decision.state_snapshot
        if decision.raw_output is not None:
            step["raw_output"] = decision.raw_output

        action = decision.action
        if isinstance(action, Recommend):
            recommendation = {"restaurant_id": action.restaurant_id}
            if action.confidence is not None:
                recommendation["confidence"] = action.confidence
            step["action"] = {"type": "RECOMMEND", **recommendation}
            if not isinstance(action.restaurant_id, str) or not action.restaurant_id.strip():
                termination = "invalid_action"
                step["error"] = "A recommendation must supply one restaurant ID."
            elif action.confidence is not None and (
                type(action.confidence) is not int or not 1 <= action.confidence <= 10
            ):
                termination = "invalid_action"
                step["error"] = "Confidence must be an integer from 1 to 10."
            elif action.restaurant_id not in restaurant_ids:
                termination = "invalid_restaurant_id"
            else:
                final_recommendation = recommendation
                text = f"RECOMMEND: {action.restaurant_id}"
                if action.confidence is not None:
                    text += f" | CONFIDENCE: {action.confidence}"
                turns.append(Turn(f"t{len(turns) + 1:02}", "assistant", text))
                termination = "completed"
            break

        if not isinstance(action, Ask) or not action.questions or not all(
            isinstance(question, Question) for question in action.questions
        ):
            termination = "invalid_action"
            step["error"] = decision.error or "Expected ASK with questions or RECOMMEND."
            break

        question_records = [
            {"question_id": f"q{index:02}", **asdict(question)}
            for index, question in enumerate(action.questions, start=questions_delivered + 1)
        ]
        step["action"] = {"type": "ASK", "questions": question_records}
        visible_ids = {turn.turn_id for turn in turns}
        if any(
            not isinstance(question.text, str)
            or not question.text.strip()
            or not isinstance(question.slot, str)
            or not question.slot.strip()
            or (
                question.reference_turn_id is not None
                and (
                    not isinstance(question.reference_turn_id, str)
                    or question.reference_turn_id not in visible_ids
                )
            )
            for question in action.questions
        ):
            termination = "invalid_action"
            step["error"] = "Every question needs text, a slot, and a valid turn reference if supplied."
            break

        if len(action.questions) > remaining:
            termination = "budget_exceeded"
            break

        try:
            replies = [
                answer_service.answer(scenario.scenario_id, question)
                for question in action.questions
            ]
        except Exception as exc:
            termination = "answer_error"
            step["error"] = f"{type(exc).__name__}: {exc}"
            break

        turns.extend(
            (
                Turn(f"t{len(turns) + 1:02}", "assistant", " ".join(q.text for q in action.questions)),
                Turn(f"t{len(turns) + 2:02}", "user", " ".join(reply.text for reply in replies)),
            )
        )
        step["delivered_questions"] = [
            {"question_id": item["question_id"], "question": item, "reply": asdict(reply)}
            for item, reply in zip(question_records, replies, strict=True)
        ]
        remaining -= len(replies)
        questions_delivered += len(replies)
        step["budget_after"] = remaining

    return {
        "schema_version": 1,
        "run_id": f"{scenario.scenario_id}-{strategy.system_id}-b{budget}-r{repeat}",
        "scenario_id": scenario.scenario_id,
        "system_id": strategy.system_id,
        "budget": budget,
        "repeat": repeat,
        "config": {
            **(strategy_config or {}),
            "data_version": scenario.data_version,
            "database_version": scenario.database_version,
        },
        "turns": [asdict(turn) for turn in turns],
        "steps": steps,
        "final_recommendation": final_recommendation,
        "termination_reason": termination,
        "usage": usage,
    }
