"""State scoring treats gold "rejected" as the same as "not accepted" (XX-SUG-05)."""

import copy
import json
import unittest

from src.data import scenario_path
from src.state_scoring import score_states


class StatusSynonymTests(unittest.TestCase):
    def setUp(self):
        self.gold = json.loads(scenario_path("XX-SUG-05").read_text())["evaluation_only"]
        self.assertEqual(self.gold["gold_dialogue_state"]["proposed_not_accepted"][0]["status"], "rejected")

    def score(self, status):
        snapshot = copy.deepcopy(self.gold["gold_dialogue_state"])
        snapshot.pop("at_turn")
        snapshot["proposed_not_accepted"][0]["status"] = status
        record = {"system_id": "s3-memory-links:test", "steps": [
            {"step_id": "s01", "context_turn_id": "t07", "state_snapshot": snapshot}]}
        return score_states(record, self.gold)

    def test_not_accepted_matches_gold_rejected(self):
        result = self.score("not accepted")
        self.assertTrue(result["fields"]["cuisine"]["correct"])
        self.assertTrue(result["exact_match"])
        self.assertTrue(self.score("rejected")["exact_match"])

    def test_other_statuses_still_differ(self):
        result = self.score("accepted")
        self.assertFalse(result["fields"]["cuisine"]["correct"])
        self.assertFalse(result["exact_match"])


if __name__ == "__main__":
    unittest.main()
