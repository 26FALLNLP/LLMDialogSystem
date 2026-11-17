import copy
import json
from pathlib import Path
import unittest

from src.state_scoring import score_states


def load_gold(scenario_id):
    path = Path(__file__).resolve().parents[1] / "data" / "scenarios" / f"{scenario_id}.json"
    return json.loads(path.read_text(encoding="utf-8"))["evaluation_only"]


def make_run(snapshot, *, system_id="structured", turn="t07"):
    return {
        "system_id": system_id,
        "steps": [{"step_id": "s01", "context_turn_id": turn, "state_snapshot": snapshot}],
    }


class StateScoringTests(unittest.TestCase):
    def test_demo_scores_only_its_observable_slots(self):
        gold = load_gold("XX-AMB-01A")
        run = make_run({
            "cuisine": "japanese",
            "max_price": 25,
            "unresolved_turn": "t07",
            "candidate_sets": {"station": ["R01"], "mall": ["R02"]},
        }, system_id="demo-shared-candidate")
        run["steps"].append({"step_id": "s02", "context_turn_id": "t09"})
        score = score_states(run, gold)
        self.assertEqual((score["field_correct"], score["field_total"]), (3, 3))
        self.assertEqual(score["unannotated_steps"], 1)
        self.assertIsNone(score["exact_match"])

    def test_correct_hidden_guess_does_not_resolve_observable_ambiguity(self):
        gold = load_gold("XX-AMB-01A")
        snapshot = copy.deepcopy(gold["gold_dialogue_state"])
        snapshot["unresolved"] = []
        snapshot["active"]["location"] = gold["hidden_user_goal"]["location"]
        score = score_states(make_run(snapshot), gold)
        self.assertFalse(score["fields"]["location"]["correct"])
        self.assertFalse(score["exact_match"])

    def test_stale_union_and_unaccepted_suggestion_are_different_errors(self):
        revised = load_gold("XX-REV-01A")
        snapshot = copy.deepcopy(revised["gold_dialogue_state"])
        snapshot["active"]["cuisine"] = ["Italian", "Japanese"]
        snapshot["relation_links"] = [{
            **revised["gold_relation_links"][0], "source_turn": "t05", "target_turn": "t01",
        }]
        score = score_states(make_run(snapshot), revised)
        self.assertTrue(score["stale_requirement_error"])
        self.assertIsNone(score["unaccepted_suggestion_error"])
        self.assertEqual(score["relation_metrics"]["matched"], 1)

        unaccepted = load_gold("XX-SUG-03A")
        snapshot = copy.deepcopy(unaccepted["gold_dialogue_state"])
        snapshot["active"]["location"] = "mall"
        score = score_states(make_run(snapshot), unaccepted)
        self.assertTrue(score["unaccepted_suggestion_error"])
        self.assertIsNone(score["stale_requirement_error"])

    def test_missing_checkpoints_and_incomplete_snapshots_have_no_score(self):
        gold = load_gold("XX-AMB-01A")
        self.assertIsNone(score_states(make_run({"active": {}}), gold))
        self.assertIsNone(score_states(make_run(gold["gold_dialogue_state"], turn="t09"), gold))
        self.assertIsNone(score_states(make_run(None), gold))
