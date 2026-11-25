"""Spending cap: $0 blocks every API run; a raised cap stops mid-run at the limit;
the spend total persists across runs. The network is mocked - nothing is sent."""

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from src import __main__ as runner
from src.budget import DISABLED_MESSAGE, BudgetError, SpendGuard, load_cap
from src.claude_client import ClaudeClient

ROOT = Path(__file__).resolve().parent.parent
ACTION = json.dumps({"action": "RECOMMEND", "questions": [], "restaurant_id": "R01"})
ENVELOPE = json.dumps({"content": [{"type": "text", "text": ACTION}], "stop_reason": "end_turn",
                       "usage": {"input_tokens": 1000, "output_tokens": 200}}).encode()
COST_PER_CALL = 1000 / 1e6 * 4.00 + 200 / 1e6 * 20.00   # Opus 5.5 prices: $0.008


def fake_connection():
    response = mock.Mock(status=200)
    response.read.return_value = ENVELOPE
    connection = mock.Mock()
    connection.getresponse.return_value = response
    return connection


class BudgetGuardTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.config = Path(self.tmp.name) / "budget.yaml"
        self.log = Path(self.tmp.name) / "spend_log.json"
        self.env = mock.patch.dict(os.environ, {"BUDGET_CONFIG": str(self.config), "SPEND_LOG": str(self.log),
                                                "ANTHROPIC_API_KEY": "fake-key-for-tests"})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def set_cap(self, usd):
        self.config.write_text(f"# test\nmax_usd: {usd}\n")

    def run_cli(self, *args):
        connections = []

        def make(*a, **k):
            connections.append(fake_connection())
            return connections[-1]

        with mock.patch("src.claude_client.http.client.HTTPSConnection", side_effect=make), \
                mock.patch.object(sys, "argv", ["src", *args]), \
                contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()) as err:
            try:
                code = runner.main()
            except SystemExit as exc:
                code = exc.code
        return code, len(connections), out.getvalue() + err.getvalue()

    # ------------------------------------------------------------------ cap 0
    def test_project_cap_is_zero(self):
        self.assertEqual(load_cap(ROOT / "configs" / "budget.yaml"), 0)

    def test_zero_cap_blocks_every_system_even_with_a_key(self):
        self.set_cap(0)
        for system in ("claude", "s1", "s2", "s3", "s4", "s5"):
            with self.subTest(system=system):
                code, calls, text = self.run_cli("--strategy", system, "--scenario", "XX-AMB-01A",
                                                 "--output", str(Path(self.tmp.name) / "x.jsonl"))
                self.assertEqual((code, calls), (2, 0))
                self.assertIn(DISABLED_MESSAGE, text)
        self.assertFalse(self.log.exists())

    def test_zero_cap_blocks_the_client_before_any_connection(self):
        self.set_cap(0)
        with mock.patch("src.claude_client.http.client.HTTPSConnection",
                        side_effect=AssertionError("network used")):
            client = ClaudeClient("fake-key-for-tests")
            with self.assertRaisesRegex(BudgetError, r"budget cap is \$0"):
                client.complete("prompt", {}, {"type": "object", "properties": {}})
        self.assertTrue(client.budget_refused)

    def test_experiment_script_refuses_with_yes_run_api_but_dry_run_works(self):
        from scripts import run_experiments
        self.set_cap(0)
        with mock.patch("subprocess.run", side_effect=AssertionError("ran")), \
                contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertIsNone(run_experiments.main(["--yes-run-api"]))
            self.assertIn(DISABLED_MESSAGE, out.getvalue())
            self.assertIsNotNone(run_experiments.main([]))      # dry run still gives estimates
        result = subprocess.run([sys.executable, "scripts/run_experiments.py", "--yes-run-api"], cwd=ROOT,
                                capture_output=True, text=True, env={**os.environ})
        self.assertIn(DISABLED_MESSAGE, result.stdout)
        self.assertFalse(list((ROOT / "results").glob("dev-*")))

    # ------------------------------------------------------------------ raised cap
    def worst_case_per_call(self):
        """Measure the pre-call worst case for each scenario of the run (big cap, mocked network)."""
        worst = []

        class Recorder(SpendGuard):
            def before_call(inner, model, request_chars, max_tokens):
                worst.append(inner.worst_case(model, request_chars, max_tokens))

        self.set_cap(1000)
        with mock.patch("src.__main__.ClaudeClient",
                        side_effect=lambda *a, **k: ClaudeClient(*a, **k, spend_guard=Recorder(1000, self.log))):
            self.run_cli("--strategy", "s1", "--all", "--no-drafts", "--budget", "0",
                         "--output", str(Path(self.tmp.name) / "probe.jsonl"))
        self.log.unlink(missing_ok=True)
        return max(worst), min(worst)

    def test_raised_cap_stops_mid_run_and_spend_persists(self):
        # Before each call the guard reserves the worst case (all 2048 output tokens + a pessimistic
        # input count); afterwards it logs the real cost ($0.008 here). Choose a cap that leaves
        # room for exactly 3 calls.
        high, low = self.worst_case_per_call()
        self.assertLess(high - low, COST_PER_CALL)
        self.set_cap(round(2 * COST_PER_CALL + high + 0.0005, 6))
        out = Path(self.tmp.name) / "run1.jsonl"
        code, calls, text = self.run_cli("--strategy", "s1", "--all", "--no-drafts", "--budget", "0",
                                         "--output", str(out))
        self.assertEqual(code, 3)
        self.assertEqual(calls, 3)
        self.assertIn("spending cap", text)
        self.assertEqual(len(out.read_text().splitlines()), 3)
        log = json.loads(self.log.read_text())
        self.assertEqual(log["calls"], 3)
        self.assertAlmostEqual(log["total_usd"], 3 * COST_PER_CALL)
        # Second run: the earlier spend is remembered, so no call fits any more.
        code, calls, _ = self.run_cli("--strategy", "s1", "--all", "--no-drafts", "--budget", "0",
                                      "--output", str(Path(self.tmp.name) / "run2.jsonl"))
        self.assertEqual((code, calls), (3, 0))
        self.assertAlmostEqual(SpendGuard.from_config().spent(), 3 * COST_PER_CALL)

    def test_unknown_model_price_is_refused(self):
        self.set_cap(5)
        with self.assertRaisesRegex(BudgetError, "No price known"):
            SpendGuard.from_config().before_call("some-other-model", 1000, 100)


if __name__ == "__main__":
    unittest.main()
