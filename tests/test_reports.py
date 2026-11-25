"""The docs/ reports: hedged-suggestion finder and cost scopes (no API calls)."""

import unittest

from scripts import make_reports
from scripts.run_experiments import CORE_SYSTEMS, estimate
from src.splits import load_split


class ReportTests(unittest.TestCase):
    def test_hedge_finder(self):
        rows = make_reports.hedges(make_reports.ROOT / "data" / "drafts" / "bhavishya" / "scenarios")
        hedged = sorted(r["id"] for r in rows if r["kind"] == "hedge")
        self.assertEqual(hedged, [f"BB-SUG-0{i}A" for i in range(1, 8)])
        self.assertEqual([r["id"] for r in rows if r["kind"] != "hedge"], ["BB-SUG-08A"])
        self.assertTrue(all(not r["gold_ask"] for r in rows))   # current labels: keep original, no question

    def test_budget_one_and_no_drafts_scopes_are_cheaper(self):
        dev = sorted(load_split().dev)
        full = estimate(dev, CORE_SYSTEMS, 1)
        one = estimate(dev, CORE_SYSTEMS, 1, budgets=(1,))
        main_only = estimate([i for i in dev if not i.startswith("BB-")], CORE_SYSTEMS, 1)
        for system in CORE_SYSTEMS:
            self.assertLess(one[system]["calls"], full[system]["calls"])
            self.assertLess(main_only[system]["calls"], full[system]["calls"])
        self.assertEqual(one["s1"]["calls"], 2 * len(dev))     # budget 1: at most 2 decisions per scenario


if __name__ == "__main__":
    unittest.main()
