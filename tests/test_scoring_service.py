"""Check scoring decisions against the actual contrastive scenarios."""

import json
import unittest

from src.data import DATA_DIR, load_dataset
from src.dialogue_pipeline import run_dialogue
from src.dialogue_types import Ask, Decision, Question, Recommend
from src.scoring_service import score


class FixedStrategy:
    system_id = "scorer-test"

    def __init__(self, *actions):
        self.actions = iter(actions)

    def decide(self, context):
        return Decision(next(self.actions))


class ScoringTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ids = ("XX-AMB-01A", "XX-AMB-01B", "XX-SUG-05")
        cls.dataset = load_dataset(ids)
        cls.gold = {}
        for scenario_id in ids:
            fixture = DATA_DIR / "scenarios" / f"{scenario_id}.json"
            cls.gold[scenario_id] = {
                **json.loads(fixture.read_bytes())["evaluation_only"],
                "scenario_id": scenario_id,
            }

    def score_actions(self, scenario_id, budget, *actions):
        scenario = self.dataset.scenarios[scenario_id]
        record = run_dialogue(scenario, FixedStrategy(*actions), self.dataset.answer_service, budget)
        return score(record, self.gold[scenario_id], scenario.restaurants)

    def test_successful_guess_can_still_miss_a_useful_question(self):
        result = self.score_actions("XX-AMB-01A", 1, Recommend("R01"))
        self.assertTrue(result["task_success"])
        self.assertTrue(result["missed_useful_clarification"])
        self.assertFalse(result["initial_action_matches"])
        self.assertFalse(result["initial_recommendation_shared"])

        zero_budget = self.score_actions("XX-AMB-01A", 0, Recommend("R01"))
        self.assertIsNone(zero_budget["missed_useful_clarification"])
        self.assertIsNone(zero_budget["initial_action_matches"])
        self.assertEqual(zero_budget["expected_initial_action"], "ASK")

    def test_answered_question_is_useful_only_for_the_case_that_needs_it(self):
        question = Ask((Question("Station or mall?", "location", "t07"),))
        should_ask = self.score_actions("XX-AMB-01A", 1, question, Recommend("R01"))
        self.assertTrue(should_ask["initial_action_matches"])
        self.assertEqual(should_ask["question_scores"][0]["judgment"], "useful")

        should_recommend = self.score_actions("XX-AMB-01B", 1, question, Recommend("R01"))
        self.assertTrue(should_recommend["task_success"])
        self.assertFalse(should_recommend["initial_action_matches"])
        self.assertEqual(should_recommend["question_scores"][0]["reason"], "shared_candidate_exists")

    def test_rejected_compound_questions_are_never_counted_as_delivered(self):
        questions = Ask((Question("Station or mall?", "location"), Question("Cuisine?", "cuisine")))
        result = self.score_actions("XX-AMB-01A", 1, questions)
        self.assertEqual(result["termination_reason"], "budget_exceeded")
        self.assertEqual(
            result["question_counts"],
            {"attempted": 2, "delivered": 0, "judged": 0, "unnecessary": 0},
        )
        self.assertFalse(result["task_success"])

    def test_new_target_after_initial_checkpoint_is_unjudged(self):
        question = Ask((Question("Station or mall?", "location", "t07"),))
        second_question = Ask((Question("What budget?", "max_price"),))
        result = self.score_actions("XX-AMB-01A", 2, question, second_question, Recommend("R01"))
        self.assertEqual([q["judgment"] for q in result["question_scores"]], ["useful", "unjudged"])
        self.assertEqual(result["question_counts"]["judged"], 1)

    def test_recommendation_uses_all_hard_constraints(self):
        excluded = next(
            row["restaurant_id"] for row in self.dataset.scenarios["XX-SUG-05"].restaurants
            if row["cuisine"] == "Indian"
        )
        result = self.score_actions("XX-SUG-05", 1, Recommend(excluded))
        self.assertFalse(result["task_success"])
        self.assertIn("exclude_cuisine", result["violated_constraints"])
