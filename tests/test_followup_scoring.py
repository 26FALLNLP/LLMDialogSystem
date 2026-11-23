"""Check annotation-driven scoring after independent clarification answers."""

import copy
import unittest

from src.answer_service import AnswerService
from src.data import Scenario, load_dataset
from src.dialogue_pipeline import run_dialogue
from src.dialogue_types import Ask, Decision, Question, Recommend, Turn
from src.scoring_service import score


class FixedActions:
    system_id = "followup-scoring-test"

    def __init__(self, actions):
        self.actions = iter(actions)

    def decide(self, context):
        return Decision(next(self.actions))


class FollowupScoringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = load_dataset(["XX-AMB-01A"]).scenarios["XX-AMB-01A"].restaurants

    def run_actions(self, budget, actions, *, max_price=28):
        replies = {
            "cuisine": "Japanese.",
            "location": "Near the mall.",
            "_unsupported": "I don't have a preference on that.",
        }
        scenario = Scenario(
            scenario_id="two-targets",
            turns=tuple(
                Turn(f"t{number:02}", "user" if number % 2 else "assistant", text)
                for number, text in enumerate((
                    "Japanese and Korean both came up.", "I can look near the station or the mall.",
                    "It is for dinner.", "Any budget?",
                    f"Up to ${max_price} per person.", "All right.",
                    "Find that kind of food near the area I meant.",
                ), start=1)
            ),
            restaurants=self.catalog,
            data_version="test", database_version="test",
        )
        gold = {
            "scenario_id": scenario.scenario_id,
            "template_family_id": "two-targets", "scenario_type": "ambiguous_reference",
            "hidden_user_goal": {"cuisine": "Japanese", "location": "mall", "dinner": True, "max_price": max_price},
            "predefined_clarification_answers": replies,
            "gold_dialogue_state": {
                "at_turn": 7,
                "active": {"dinner": True, "max_price": max_price},
                "unresolved": [
                    {"slot": "cuisine", "turn": 7, "interpretations": [{"cuisine": "Japanese"}, {"cuisine": "Korean"}]},
                    {"slot": "location", "turn": 7, "interpretations": [{"location": "station"}, {"location": "mall"}]},
                ],
                "superseded": [], "proposed_not_accepted": [],
            },
            "gold_decision": {
                "should_ask": True,
                "necessary_question": None,
                "necessary_questions": ["cuisine@t7", "location@t7"],
                "score_followup_clarifications": True,
            },
        }
        run = run_dialogue(scenario, FixedActions(actions), AnswerService({scenario.scenario_id: replies}), budget)
        return run, gold

    def ask(self, slot):
        return Ask((Question(f"Which {slot} did you mean?", slot, "t07"),))

    def test_either_question_order_resolves_both_targets(self):
        for order in (("cuisine", "location"), ("location", "cuisine")):
            with self.subTest(order=order):
                run, gold = self.run_actions(2, [self.ask(slot) for slot in order] + [Recommend("R02")])
                result = score(run, gold, self.catalog)
                self.assertTrue(result["task_success"])
                self.assertTrue(result["initial_action_matches"])
                self.assertEqual([q["judgment"] for q in result["question_scores"]], ["useful", "useful"])
                self.assertEqual(result["question_counts"]["judged"], 2)

    def test_budget_one_exhaustion_and_skipping_an_available_question_are_distinct(self):
        exhausted, gold = self.run_actions(1, [self.ask("cuisine"), Recommend("R02")])
        result = score(exhausted, gold, self.catalog)
        self.assertTrue(result["task_success"])
        self.assertIsNone(result["missed_useful_clarification"])
        self.assertEqual(result["missed_clarification_reason"], "budget_exhausted")

        skipped, gold = self.run_actions(2, [self.ask("cuisine"), Recommend("R02")])
        result = score(skipped, gold, self.catalog)
        self.assertTrue(result["missed_useful_clarification"])
        self.assertEqual(result["missed_clarification_reason"], "needed_clarification_skipped")

    def test_repeated_target_is_unnecessary(self):
        run, gold = self.run_actions(2, [self.ask("cuisine"), self.ask("cuisine"), Recommend("R02")])
        result = score(run, gold, self.catalog)
        self.assertEqual(result["question_scores"][1]["judgment"], "unnecessary")
        self.assertEqual(result["question_scores"][1]["reason"], "duplicate_target")

    def test_fallback_does_not_resolve_an_ambiguity(self):
        run, gold = self.run_actions(2, [self.ask("cuisine"), self.ask("cuisine"), Recommend("R02")])
        run["steps"][0]["delivered_questions"][0]["reply"]["status"] = "fallback"
        result = score(run, gold, self.catalog)
        self.assertEqual(result["question_scores"][0]["reason"], "fallback_reply")
        self.assertEqual(result["question_scores"][1]["judgment"], "useful")

    def test_shared_candidate_after_first_answer_makes_second_question_unnecessary(self):
        run, gold = self.run_actions(
            2, [self.ask("cuisine"), self.ask("location"), Recommend("R03")], max_price=30,
        )
        result = score(run, gold, self.catalog)
        self.assertTrue(result["task_success"])
        self.assertEqual(result["question_scores"][1]["reason"], "shared_candidate_exists")

        stopped, gold = self.run_actions(2, [self.ask("cuisine"), Recommend("R03")], max_price=30)
        result = score(stopped, gold, self.catalog)
        self.assertFalse(result["missed_useful_clarification"])
        self.assertEqual(result["missed_clarification_reason"], "shared_candidate_available")

    def test_questions_in_one_action_share_the_pre_action_checkpoint(self):
        questions = Ask((
            Question("Which cuisine did you mean?", "cuisine", "t07"),
            Question("Which location did you mean?", "location", "t07"),
        ))
        run, gold = self.run_actions(2, [questions, Recommend("R03")], max_price=30)
        result = score(run, gold, self.catalog)
        self.assertTrue(result["task_success"])
        self.assertEqual([q["judgment"] for q in result["question_scores"]], ["useful", "useful"])
        self.assertEqual(result["question_counts"]["delivered"], 2)

    def test_followup_scoring_requires_explicit_annotation(self):
        run, gold = self.run_actions(2, [self.ask("cuisine"), self.ask("location"), Recommend("R02")])
        legacy = copy.deepcopy(gold)
        legacy["gold_decision"] = {"should_ask": True, "necessary_question": "cuisine@t7"}
        result = score(run, legacy, self.catalog)
        self.assertEqual([q["judgment"] for q in result["question_scores"]], ["useful", "unjudged"])


if __name__ == "__main__":
    unittest.main()
