"""Family-level dev/test split, and the guard: normal runs use dev; test needs --final-test."""

import json
import subprocess
import sys
import tempfile
import unittest
from collections import defaultdict
from pathlib import Path

from src.data import DATA_DIR, load_dataset
from src.make_split import all_scenarios, make_split, main as make_split_main
from src.splits import SplitError, load_split, select_scenarios

ROOT = Path(__file__).resolve().parent.parent


class SplitFileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.split = json.loads((DATA_DIR / "splits" / "split.json").read_text())
        cls.scenarios = all_scenarios()

    def test_split_covers_everything_once_and_matches_the_data(self):
        dev, test = set(self.split["dev"]), set(self.split["test"])
        self.assertFalse(dev & test)
        self.assertEqual(dev | test, set(self.scenarios))
        self.assertEqual(self.split["data_version"], load_dataset(sorted(self.scenarios)).data_version)

    def test_families_and_ambiguity_groups_stay_together(self):
        side = {i: "dev" for i in self.split["dev"]} | {i: "test" for i in self.split["test"]}
        by_family = defaultdict(set)
        for sid, sc in self.scenarios.items():
            by_family[sc["evaluation_only"]["template_family_id"]].add(side[sid])
        self.assertTrue(all(len(sides) == 1 for sides in by_family.values()))
        for manifest in [DATA_DIR / "dataset-manifest.json", *DATA_DIR.glob("drafts/*/dataset-manifest.json")]:
            for g in json.loads(manifest.read_text())["groups"]:
                self.assertEqual(len({side[s] for s in g["scenario_ids"]}), 1, g["group_id"])

    def test_split_is_reproducible_and_about_a_quarter_of_families(self):
        again = make_split(self.scenarios, self.split["seed"], self.split["dev_fraction"])
        self.assertEqual((again["dev"], again["test"]), (self.split["dev"], self.split["test"]))
        n_fam = len({sc["evaluation_only"]["template_family_id"] for sc in self.scenarios.values()})
        self.assertAlmostEqual(len(self.split["dev_families"]) / n_fam, 0.25, delta=0.05)

    def test_refuses_to_overwrite_without_force(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "split.json"
            out.write_text("{}")
            self.assertEqual(make_split_main(["--out", str(out)]), 2)
            self.assertEqual(out.read_text(), "{}")


class SplitGuardTests(unittest.TestCase):
    def test_all_means_dev_only(self):
        split = load_split()
        self.assertEqual(set(select_scenarios(None, run_all=True)), split.dev)
        self.assertEqual(set(select_scenarios(None, run_all=True, final_test=True)), split.test)
        main_only = select_scenarios(None, run_all=True, include_drafts=False)
        self.assertTrue(main_only and not any(i.startswith("BB-") for i in main_only))

    def test_test_scenario_needs_final_test(self):
        test_id = sorted(load_split().test)[0]
        with self.assertRaisesRegex(SplitError, "TEST split"):
            select_scenarios([test_id])
        self.assertEqual(select_scenarios([test_id], final_test=True), [test_id])
        with self.assertRaisesRegex(SplitError, "Not in any split"):
            select_scenarios(["NOT-A-SCENARIO"])

    def test_command_line_refuses_test_scenario_without_flag(self):
        test_id = sorted(i for i in load_split().test if i.startswith("XX-"))[0]
        result = subprocess.run([sys.executable, "-m", "src", "--scenario", test_id, "--output", "/dev/null"],
                                cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("--final-test", result.stderr)

    def test_demo_default_pair_is_in_dev(self):
        self.assertTrue({"XX-AMB-01A", "XX-AMB-01B"} <= load_split().dev)


if __name__ == "__main__":
    unittest.main()
