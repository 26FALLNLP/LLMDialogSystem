"""Right-question metric (scorer v2): a question counts as useful only if it asks
about the thing that is actually unclear; anything else is wasted."""

import json
import unittest

from src.data import load_dataset, scenario_path
from src.dialogue_pipeline import run_dialogue
from src.dialogue_types import Ask, Decision, Question, Recommend
from src.score_summary import summarize
from src.scoring_service import score

LOCATION_Q = Question("Do you mean the station or the mall?", "location", None)
CUISINE_Q = Question("Which cuisine did she pick?", "cuisine", None)
BUDGET_Q = Question("What's your budget per person?", "max_price", None)


class Fixed:
    system_id = "right-question-test"

    def __init__(self, *actions):
        self.actions = iter(actions)

    def decide(self, context):
        return Decision(next(self.actions))


class RightQuestionMetricTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ids = ("XX-AMB-01A", "BB-TWOQ-01", "BB-LOC-01A")
        cls.dataset = load_dataset(cls.ids)
        cls.gold = {i: {**json.loads(scenario_path(i).read_text())["evaluation_only"], "scenario_id": i}
                    for i in cls.ids}

    def run_and_score(self, scenario_id, budget, *actions):
        scenario = self.dataset.scenarios[scenario_id]
        record = run_dialogue(scenario, Fixed(*actions), self.dataset.answer_service, budget)
        return score(record, self.gold[scenario_id], scenario.restaurants)

    def correct(self, scenario_id):
        return Recommend(self.gold[scenario_id]["computed_by_validator"]["success_set"][0])

    def judgments(self, result):
        return [(q["slot"], q["judgment"], q["reason"]) for q in result["question_scores"]]

    def test_asking_about_the_unclear_slot_is_useful_even_without_a_turn_reference(self):
        result = self.run_and_score("XX-AMB-01A", 1, Ask((LOCATION_Q,)), self.correct("XX-AMB-01A"))
        self.assertEqual(self.judgments(result), [("location", "useful", "clarifies_needed_target")])
        self.assertTrue(result["initial_action_matches"])
        self.assertTrue(result["all_needed_slots_clarified"])

    def test_asking_about_something_already_clear_is_wasted(self):
        result = self.run_and_score("XX-AMB-01A", 1, Ask((Question("Which kind of food?", "cuisine"),)),
                                    self.correct("XX-AMB-01A"))
        self.assertEqual(self.judgments(result), [("cuisine", "unnecessary", "not_needed_target")])
        self.assertFalse(result["initial_action_matches"])
        self.assertFalse(result["all_needed_slots_clarified"])

    def test_empty_question_with_the_right_label_is_wasted(self):
        result = self.run_and_score("BB-LOC-01A", 1, Ask((Question("ok?", "location"),)), self.correct("BB-LOC-01A"))
        self.assertEqual(self.judgments(result), [("location", "unnecessary", "fallback_reply")])

    def test_two_question_scenario_needs_both_questions(self):
        result = self.run_and_score("BB-TWOQ-01", 2, Ask((CUISINE_Q,)), Ask((LOCATION_Q,)), self.correct("BB-TWOQ-01"))
        self.assertEqual([j[1] for j in self.judgments(result)], ["useful", "useful"])
        self.assertEqual(result["questions_needed"], 2)
        self.assertTrue(result["all_needed_slots_clarified"])
        self.assertTrue(result["task_success"])

    def test_two_question_scenario_second_question_on_wrong_slot_is_wasted(self):
        result = self.run_and_score("BB-TWOQ-01", 2, Ask((CUISINE_Q,)), Ask((BUDGET_Q,)), self.correct("BB-TWOQ-01"))
        self.assertEqual(self.judgments(result)[1], ("max_price", "unnecessary", "not_needed_target"))
        self.assertFalse(result["all_needed_slots_clarified"])

    def test_repeating_an_answered_question_is_wasted(self):
        result = self.run_and_score("BB-TWOQ-01", 2, Ask((CUISINE_Q,)), Ask((CUISINE_Q,)), self.correct("BB-TWOQ-01"))
        self.assertEqual(self.judgments(result)[1], ("cuisine", "unnecessary", "duplicate_target"))

    def test_summary_reports_right_question_rate(self):
        rows = [
            {**self.run_and_score("BB-TWOQ-01", 2, Ask((CUISINE_Q,)), Ask((BUDGET_Q,)), self.correct("BB-TWOQ-01")),
             "data_version": "x", "database_version": "y"},
            {**self.run_and_score("XX-AMB-01A", 1, Ask((LOCATION_Q,)), self.correct("XX-AMB-01A")),
             "data_version": "x", "database_version": "y"},
        ]
        rate = summarize(rows, bootstrap_samples=2)["overall"]["right_question_rate"]
        self.assertEqual((rate["numerator"], rate["denominator"]), (2, 3))


if __name__ == "__main__":
    unittest.main()
