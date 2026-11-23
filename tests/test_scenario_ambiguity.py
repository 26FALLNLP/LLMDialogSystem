"""Protect ambiguous histories and their private clarification annotations."""

import json
import unittest
from collections import Counter, defaultdict
from itertools import combinations, product

from src.data import DATA_DIR, load_dataset
from src.dialogue_pipeline import run_dialogue
from src.dialogue_types import Ask, Decision, Question, Recommend
from src.scoring_service import constraint_violations, score


def best_correct(worlds, slots, question_budget):
    """Count correct worlds with an optimal choice and independent-slot questions."""
    restaurant_counts = Counter(
        restaurant_id for world in worlds for restaurant_id in world["candidates"]
    )
    best = max(restaurant_counts.values(), default=0)
    if question_budget == 0:
        return best
    for slot in slots:
        partitions = defaultdict(list)
        for world in worlds:
            partitions[world["answers"][slot]].append(world)
        remaining_slots = tuple(value for value in slots if value != slot)
        after_question = sum(
            best_correct(partition, remaining_slots, question_budget - 1)
            for partition in partitions.values()
        )
        best = max(best, after_question)
    return best


class ScriptedClarification:
    system_id = "ambiguity-fixture-test"

    def __init__(self, question, restaurant_id):
        self.actions = iter((Ask((question,)), Recommend(restaurant_id)))

    def decide(self, context):
        return Decision(next(self.actions))


class ScenarioAmbiguityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = {
            path.stem: json.loads(path.read_text(encoding="utf-8"))
            for path in (DATA_DIR / "scenarios").glob("*.json")
        }
        cls.dataset = load_dataset(sorted(cls.records))
        cls.catalog = json.loads((DATA_DIR / "restaurants.json").read_text(encoding="utf-8"))
        cls.manifest = json.loads((DATA_DIR / "dataset-manifest.json").read_text(encoding="utf-8"))

    def candidates(self, goal):
        return {
            row["restaurant_id"] for row in self.catalog
            if not constraint_violations(row, goal)
        }

    def test_candidate_annotations_match_the_catalog(self):
        self.assertEqual(len(self.records), 48)
        for scenario_id, record in self.records.items():
            with self.subTest(scenario_id=scenario_id):
                gold = record["evaluation_only"]
                computed = gold["computed_by_validator"]
                success = self.candidates(gold["hidden_user_goal"])
                self.assertTrue(success)
                self.assertEqual(set(computed["success_set"]), success)
                state = gold["gold_dialogue_state"]
                active = state["active"]
                shared = self.candidates(active)
                interpretations = computed.get("interpretation_sets", [])
                if state["unresolved"]:
                    options = [item["interpretations"] for item in state["unresolved"]]
                    expected = [
                        {key: value for option in choices for key, value in option.items()}
                        for choices in product(*options)
                    ]
                    self.assertEqual(
                        [item["interpretation"] for item in interpretations], expected,
                    )
                for interpretation in interpretations:
                    candidates = self.candidates({**active, **interpretation["interpretation"]})
                    self.assertTrue(candidates)
                    self.assertEqual(set(interpretation["candidates"]), candidates)
                    shared &= candidates
                if interpretations:
                    self.assertEqual(set(computed["shared_candidates"]), shared)
                self.assertEqual(set(computed["valid_without_clarification"]), shared)
                self.assertEqual(gold["gold_decision"]["should_ask"], not bool(shared))

    def test_manifest_groups_are_balanced_and_hide_the_target(self):
        manifest_ids = [
            scenario_id for group in self.manifest["groups"]
            for scenario_id in group["scenario_ids"]
        ]
        self.assertEqual(len(manifest_ids), len(set(manifest_ids)))
        self.assertEqual(set(manifest_ids), set(self.records))
        self.assertEqual(self.manifest["scenario_count"], len(self.records))
        self.assertEqual(self.manifest["catalog_count"], len(self.catalog))
        self.assertEqual(self.manifest["data_version"], self.dataset.data_version)
        self.assertEqual(self.manifest["database_version"], self.dataset.database_version)

        for group in self.manifest["groups"]:
            with self.subTest(group=group["group_id"]):
                records = [self.records[scenario_id] for scenario_id in group["scenario_ids"]]
                first = records[0]
                for record in records[1:]:
                    self.assertEqual(record["model_visible"], first["model_visible"])
                    self.assertEqual(
                        record["evaluation_only"]["gold_dialogue_state"],
                        first["evaluation_only"]["gold_dialogue_state"],
                    )
                for left, right in combinations(records, 2):
                    self.assertFalse(
                        self.candidates(left["evaluation_only"]["hidden_user_goal"])
                        & self.candidates(right["evaluation_only"]["hidden_user_goal"])
                    )
                for slot in group["required_slots"]:
                    values = Counter(
                        record["evaluation_only"]["hidden_user_goal"][slot] for record in records
                    )
                    self.assertGreater(len(values), 1)
                    self.assertEqual(len(set(values.values())), 1)

    def test_question_budget_expectations_follow_from_candidate_sets(self):
        totals = {budget: 0 for budget in (0, 1, 2)}
        composition = Counter()
        for group in self.manifest["groups"]:
            worlds = []
            for scenario_id in group["scenario_ids"]:
                gold = self.records[scenario_id]["evaluation_only"]
                worlds.append({
                    "candidates": self.candidates(gold["hidden_user_goal"]),
                    "answers": gold["predefined_clarification_answers"],
                })
            possible_correct = {
                budget: best_correct(worlds, tuple(group["required_slots"]), budget)
                for budget in (0, 1, 2)
            }
            minimum_budget = next(
                budget for budget, correct in possible_correct.items() if correct == len(worlds)
            )
            composition[minimum_budget] += len(worlds)
            for budget, correct in possible_correct.items():
                totals[budget] += correct
        self.assertEqual(dict(composition), {0: 8, 1: 32, 2: 8})
        self.assertEqual(self.manifest["composition"], {
            "zero_question": composition[0],
            "one_question": composition[1],
            "two_question": composition[2],
        })
        self.assertEqual(totals, {0: 20, 1: 44, 2: 48})
        self.assertEqual(
            self.manifest["idealized_expected_correct"],
            {str(budget): correct for budget, correct in totals.items()},
        )

    def test_hidden_target_twins_have_identical_public_inputs(self):
        for family in ("01", "02", "03", "04"):
            left_id, right_id = f"XX-AMB-{family}A", f"XX-AMB-{family}C"
            with self.subTest(family=family):
                left, right = self.records[left_id], self.records[right_id]
                self.assertEqual(left["model_visible"], right["model_visible"])
                self.assertEqual(self.dataset.scenarios[left_id].turns, self.dataset.scenarios[right_id].turns)
                self.assertEqual(self.dataset.scenarios[left_id].restaurants, self.dataset.scenarios[right_id].restaurants)
                left_gold, right_gold = left["evaluation_only"], right["evaluation_only"]
                self.assertEqual(left_gold["gold_dialogue_state"], right_gold["gold_dialogue_state"])
                self.assertEqual(left_gold["ambiguity_pair_id"], right_gold["ambiguity_pair_id"])
                slot = left_gold["gold_dialogue_state"]["unresolved"][0]["slot"]
                changed = {
                    key for key in left_gold["hidden_user_goal"]
                    if left_gold["hidden_user_goal"][key] != right_gold["hidden_user_goal"][key]
                }
                self.assertEqual(changed, {slot})
                self.assertNotEqual(
                    left_gold["predefined_clarification_answers"][slot],
                    right_gold["predefined_clarification_answers"][slot],
                )
                self.assertFalse(self.candidates(left_gold["hidden_user_goal"]) & self.candidates(right_gold["hidden_user_goal"]))

    def test_clarification_delivers_the_private_answer_and_scores_as_useful(self):
        for family in ("01", "02", "03", "04"):
            for variant in ("A", "C"):
                scenario_id = f"XX-AMB-{family}{variant}"
                with self.subTest(scenario_id=scenario_id):
                    gold = self.records[scenario_id]["evaluation_only"]
                    slot = gold["gold_dialogue_state"]["unresolved"][0]["slot"]
                    question = Question(f"Which {slot} did you mean?", slot, "t07")
                    recommendation = min(self.candidates(gold["hidden_user_goal"]))
                    scenario = self.dataset.scenarios[scenario_id]
                    run = run_dialogue(
                        scenario, ScriptedClarification(question, recommendation),
                        self.dataset.answer_service, 1,
                    )
                    result = score(run, {**gold, "scenario_id": scenario_id}, scenario.restaurants)
                    self.assertEqual(run["termination_reason"], "completed")
                    self.assertEqual(run["turns"][-2]["text"], gold["predefined_clarification_answers"][slot])
                    self.assertTrue(result["task_success"])
                    self.assertTrue(result["initial_action_matches"])
                    self.assertEqual(result["question_counts"]["delivered"], 1)
                    self.assertEqual(result["question_scores"][0]["judgment"], "useful")
