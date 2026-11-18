"""Normal runs use the dev split; the test split needs --final-test."""

import json
import subprocess
import sys
import unittest
from pathlib import Path

from src.data import DATA_DIR, load_dataset
from src.splits import SplitError, load_split, select_scenarios

ROOT = Path(__file__).resolve().parent.parent


class SplitGuardTests(unittest.TestCase):
    def setUp(self):
        frozen = json.loads((DATA_DIR / "splits" / "split.json").read_text())
        self.dev, self.test = frozen["dev"], frozen["test"]

    def test_all_means_dev_only(self):
        self.assertEqual(select_scenarios(None, run_all=True), sorted(self.dev))
        self.assertEqual(select_scenarios(None, run_all=True, final_test=True), sorted(self.test))

    def test_test_scenario_needs_final_test(self):
        with self.assertRaisesRegex(SplitError, "TEST split"):
            select_scenarios(["XX-AMB-02A"])
        self.assertEqual(select_scenarios(["XX-AMB-02A"], final_test=True), ["XX-AMB-02A"])
        self.assertEqual(select_scenarios(["XX-AMB-04A"]), ["XX-AMB-04A"])

    def test_draft_test_scenarios_are_guarded_too(self):
        split = load_split()
        draft_test = sorted(i for i in split.test if i.startswith("BB-"))
        draft_dev = sorted(i for i in split.dev if i.startswith("BB-"))
        self.assertTrue(draft_test and draft_dev)
        with self.assertRaises(SplitError):
            select_scenarios([draft_test[0]])
        with_drafts = select_scenarios(None, run_all=True, include_drafts=True)
        self.assertTrue(set(draft_dev) <= set(with_drafts))
        self.assertFalse(set(with_drafts) & set(split.test))
        load_dataset(with_drafts)  # every dev ID, original or draft, loads

    def test_unknown_scenario_is_refused(self):
        with self.assertRaisesRegex(SplitError, "Not in any split"):
            select_scenarios(["NOT-A-SCENARIO"])

    def test_frozen_split_is_unchanged(self):
        frozen = json.loads((DATA_DIR / "splits" / "split.json").read_text())
        self.assertEqual((frozen["n_dev"], frozen["n_test"]), (7, 29))
        self.assertEqual(len(set(frozen["dev"]) | set(frozen["test"])), 36)

    def test_command_line_refuses_test_scenario_without_flag(self):
        result = subprocess.run(
            [sys.executable, "-m", "src", "--scenario", "XX-AMB-02A", "--output", "/dev/null"],
            cwd=ROOT, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("--final-test", result.stderr)


if __name__ == "__main__":
    unittest.main()
