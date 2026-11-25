"""Experiment scripts: dry run by default (no API, no subprocess), and the
results report (tables, figures, family-bootstrap CIs) on synthetic scores."""

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import make_results, run_experiments
from src.splits import load_split


def fake_row(system, budget, family, success, unnecessary=0, judged=1, exact=True):
    return {"system_id": system, "budget": budget, "template_family_id": family, "task_success": success,
            "question_counts": {"unnecessary": unnecessary, "judged": judged},
            "state_metrics": {"field_correct": 5 if exact else 4, "field_total": 6, "exact_match": exact}}


class ExperimentScriptTests(unittest.TestCase):
    def test_dry_run_estimates_dev_and_test_and_calls_nothing(self):
        with mock.patch("subprocess.run", side_effect=AssertionError("ran")), \
                mock.patch("src.claude_client.ClaudeClient", side_effect=AssertionError("API")), \
                contextlib.redirect_stdout(io.StringIO()) as out:
            est = run_experiments.main([])
        split = load_split()
        self.assertEqual(est["DEV run"]["ids"], sorted(split.dev))
        self.assertEqual(est["final TEST run"]["ids"], sorted(split.test))
        n_dev = len(split.dev)
        self.assertEqual(est["DEV run"]["per_system"]["s1"]["calls"], n_dev * (1 + 2 + 3))
        self.assertEqual(est["DEV run"]["per_system"]["s2"]["calls"], 2 * n_dev * (1 + 2 + 3))
        self.assertGreater(est["DEV run"]["per_system"]["s3"]["calls"], est["DEV run"]["per_system"]["s1"]["calls"])
        self.assertNotIn("s5", est["DEV run"]["per_system"])
        text = out.getvalue()
        self.assertIn("DRY RUN", text)
        self.assertNotIn("--final-test", text.split("Commands for the DEV run:")[1])

    def test_final_test_commands_carry_the_flag(self):
        cmds, _, _ = run_experiments.commands(Path("results/x"), ("s1", "s3"), "m", True, "rule_given")
        self.assertTrue(all("--final-test" in c for c in cmds))
        self.assertEqual(len(cmds), 2 * 3)

    def test_results_report_tables_figures_and_family_cis(self):
        rows = []
        for f in range(10):
            rows.append(fake_row("s1", 0, f"F{f}", f < 5))
            rows.append(fake_row("s3", 0, f"F{f}", f < 9, unnecessary=0))
        with tempfile.TemporaryDirectory() as tmp:
            scores = Path(tmp) / "scores.jsonl"
            scores.write_text("".join(json.dumps(r) + "\n" for r in rows))
            summary = make_results.write_results(scores)
            self.assertTrue((Path(tmp) / "tables" / "summary.csv").exists())
            for name in ("success_by_budget", "unnecessary_question_rate", "state_field_accuracy"):
                self.assertTrue((Path(tmp) / "figures" / f"{name}.svg").read_text().startswith("<svg"))
        by_system = {r["system_id"]: r for r in summary}
        self.assertEqual(by_system["s1"]["task_success"], 0.5)
        self.assertEqual(by_system["s3"]["task_success"], 0.9)
        low, high = by_system["s1"]["task_success_ci_low"], by_system["s1"]["task_success_ci_high"]
        self.assertTrue(0 <= low <= 0.5 <= high <= 1)
        self.assertEqual(by_system["s1"]["families"], 10)


if __name__ == "__main__":
    unittest.main()
