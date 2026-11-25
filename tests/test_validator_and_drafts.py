"""Validator on main's format, and the converted BB- drafts."""

import copy
import json
import unittest
from collections import Counter
from itertools import combinations
from pathlib import Path

from data.validate import analyse, group_checks, hint_report, load_scenarios, validate
from src.data import DATA_DIR, load_dataset, scenario_path
from src.scoring_service import constraint_violations

DRAFTS = DATA_DIR / "drafts" / "bhavishya"
DB = json.loads((DATA_DIR / "restaurants.json").read_text())


def fails(per):
    return [(p, i) for p, issues in per.items() for i in issues if i[0] == "FAIL"]


class ValidatorOnMainTests(unittest.TestCase):
    def test_main_48_pass_with_their_manifest(self):
        loaded, per, dataset, _, _ = validate([str(DATA_DIR / "scenarios")], DB,
                                               [str(DATA_DIR / "dataset-manifest.json")])
        self.assertEqual(len(loaded), 48)
        self.assertEqual(fails(per), [])
        self.assertEqual([d for d in dataset if d[0] == "FAIL"], [])

    def test_group_checks_catch_unbalanced_or_overlapping_targets(self):
        a = json.loads(scenario_path("XX-AMB-01A").read_text())
        c = json.loads(scenario_path("XX-AMB-01C").read_text())
        self.assertEqual(group_checks([a, c], DB)[0], {})
        same = copy.deepcopy(c)
        same["scenario_id"] = "XX-AMB-01C-copy"
        same["evaluation_only"]["hidden_user_goal"] = a["evaluation_only"]["hidden_user_goal"]
        issues, _ = group_checks([a, same], DB)
        self.assertTrue(any("not balanced" in i[2] for i in issues["XX-AMB-01A"]))
        self.assertTrue(any("overlaps" in i[2] for i in issues["XX-AMB-01A"]))

    def test_two_question_form_with_null_necessary_question_is_accepted(self):
        sc = json.loads(scenario_path("XX-AMB-12A").read_text())
        _, issues = analyse(sc, DB)
        self.assertEqual([i for i in issues if i[0] == "FAIL"], [])
        sc["evaluation_only"]["gold_decision"]["necessary_questions"] = []
        self.assertIn("answers", [i[1] for i in analyse(sc, DB)[1] if i[0] == "FAIL"])

    def test_stored_candidate_sets_must_match_the_database(self):
        sc = json.loads(scenario_path("XX-AMB-06A").read_text())
        sc["evaluation_only"]["computed_by_validator"]["success_set"] = ["R40"]
        self.assertIn("computed", [i[1] for i in analyse(sc, DB)[1] if i[0] == "FAIL"])

    def test_hint_detector_still_flags_the_known_originals(self):
        originals = [sc for _, sc in load_scenarios(str(DATA_DIR / "archive" / "nlp-v1" / "scenarios"))]
        _, per, _ = hint_report(originals, DB)
        self.assertEqual(sorted(per), ["XX-AMB-03A", "XX-AMB-04A"])


class DraftDatasetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((DRAFTS / "dataset-manifest.json").read_text())
        cls.records = {p.stem: json.loads(p.read_text()) for p in (DRAFTS / "scenarios").glob("*.json")}

    def candidates(self, goal):
        return {r["restaurant_id"] for r in DB if not constraint_violations(r, goal)}

    def test_drafts_and_combined_dataset_pass_the_validator(self):
        for dirs, manifests in (
            ([DRAFTS / "scenarios"], [DRAFTS / "dataset-manifest.json"]),
            ([DATA_DIR / "scenarios", DRAFTS / "scenarios"],
             [DATA_DIR / "dataset-manifest.json", DRAFTS / "dataset-manifest.json"]),
        ):
            _, per, dataset, _, _ = validate([str(d) for d in dirs], DB, [str(m) for m in manifests])
            self.assertEqual(fails(per), [])
            self.assertEqual([d for d in dataset if d[0] == "FAIL"], [])

    def test_drafts_have_no_hint_warnings_and_are_balanced(self):
        _, per, dataset = hint_report(list(self.records.values()), DB)
        self.assertEqual(dict(per), {})
        self.assertEqual(dataset, [])

    def test_manifest_matches_files_and_groups_hide_the_target(self):
        ids = [s for g in self.manifest["groups"] for s in g["scenario_ids"]]
        self.assertEqual(sorted(ids), sorted(self.records))
        self.assertEqual(self.manifest["scenario_count"], len(ids))
        dataset = load_dataset(ids)
        self.assertEqual(self.manifest["data_version"], dataset.data_version)
        for g in self.manifest["groups"]:
            recs = [self.records[s] for s in g["scenario_ids"]]
            for r in recs[1:]:
                self.assertEqual(r["model_visible"], recs[0]["model_visible"])
            for a, b in combinations(recs, 2):
                self.assertFalse(self.candidates(a["evaluation_only"]["hidden_user_goal"])
                                 & self.candidates(b["evaluation_only"]["hidden_user_goal"]))

    def test_original_draft_labels_are_kept(self):
        """Each converted group contains its source draft's hidden goal unchanged."""
        for g in self.manifest["groups"]:
            originals = [s for s in g["scenario_ids"]
                         if self.records[s]["evaluation_only"]["draft_info"]["original_hidden_goal"]]
            self.assertEqual(len(originals), 1, g["group_id"])

    def test_ids_text_source_and_no_overlap_with_main(self):
        main_ids = {p.stem for p in (DATA_DIR / "scenarios").glob("*.json")}
        for sid, r in self.records.items():
            self.assertTrue(sid.startswith("BB-"))
            self.assertIn("Qwen", r["text_source"])
            self.assertNotIn(sid, main_ids)

    def test_draft_chat_text_has_no_stray_spaces(self):
        for sid, r in self.records.items():
            for t in r["model_visible"]["dialogue_prefix"]:
                self.assertEqual(t["text"], " ".join(t["text"].split()), f"{sid} turn {t['turn']}")

    def test_ok_question_does_not_leak_in_drafts(self):
        from src.dialogue_types import Question
        ids = sorted(self.records)
        service = load_dataset(ids).answer_service
        for sid in ids:
            self.assertEqual(service.answer(sid, Question("ok?", "location")).status, "fallback")


if __name__ == "__main__":
    unittest.main()
