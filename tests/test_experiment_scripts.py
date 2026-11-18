"""Experiment scripts: dry run by default, never touch the API or the test split."""

import contextlib
import io
import unittest
from unittest import mock

from scripts import guessability, run_main_experiment
from scripts.experiment_common import gold, should_ask_dev_ids
from src.splits import load_split


class ExperimentScriptTests(unittest.TestCase):
    def quiet(self, fn, argv):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            result = fn(argv)
        return result, out.getvalue()

    def test_guessability_dry_run_uses_only_dev_should_ask_and_makes_no_call(self):
        with mock.patch("src.claude_client.ClaudeClient", side_effect=AssertionError("API used")):
            result, text = self.quiet(guessability.main, ["--repeats", "3"])
        test = load_split().test
        self.assertTrue(result["ids"])
        for sid in result["ids"]:
            self.assertTrue(gold(sid)["gold_decision"]["should_ask"], sid)
            self.assertNotIn(sid, test)
        self.assertEqual(result["calls"], len(result["ids"]) * 3 * 2)
        self.assertIn("DRY RUN", text)
        self.assertIn("$", text)

    def test_main_experiment_dry_run_is_dev_only_and_prints_commands(self):
        with mock.patch("subprocess.run", side_effect=AssertionError("ran")):
            result, text = self.quiet(run_main_experiment.main, [])
        self.assertFalse(set(result["ids"]) & load_split().test)
        self.assertEqual(result["calls"], len(result["ids"]) * 2 * (1 + 2 + 3))
        self.assertEqual(len(result["commands"]), 2 * 3 + 1)
        for cmd in result["commands"][:-1]:
            self.assertIn("--all", cmd)
            self.assertNotIn("--final-test", cmd)
        self.assertIn("DRY RUN", text)

    def test_twin_analysis_patterns(self):
        ids = should_ask_dev_ids()
        pair = next(i for i in ids if gold(i)["variant"] == "A" and f"{i}-SW" in ids)
        results = [{"scenario_id": pair, "variant": "plain", "correct": True},
                   {"scenario_id": f"{pair}-SW", "variant": "plain", "correct": False}]
        report = guessability.analyse(results)["plain"]
        self.assertEqual(report["accuracy"], 0.5)
        self.assertEqual(list(report["twin_pairs"].values())[0]["pattern"], "one right")


if __name__ == "__main__":
    unittest.main()
