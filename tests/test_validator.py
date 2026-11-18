"""Tests for data/validate.py: two-question support, variant families,
suggestion traps and the dataset hint detector."""

import copy
import json
import unittest
from pathlib import Path

from data.validate import analyse, hint_report, load_scenarios, pair_checks

ROOT = Path(__file__).resolve().parent.parent
DB = json.loads((ROOT / "data" / "restaurants.json").read_text())
DRAFTS = ROOT / "data" / "drafts" / "bhavishya"


def _load(sid):
    for path, sc in load_scenarios(str(ROOT / "data")):
        if sc["scenario_id"] == sid:
            return copy.deepcopy(sc)
    raise KeyError(sid)


def _fails(sc):
    return [i for i in analyse(sc, DB)[1] if i[0] == "FAIL"]


class ValidatorTests(unittest.TestCase):
    def test_every_original_and_draft_scenario_passes(self):
        loaded = load_scenarios(str(ROOT / "data"))
        self.assertGreaterEqual(len(loaded), 36 + 138)
        for path, sc in loaded:
            self.assertEqual(_fails(sc), [], path)
        families = pair_checks([sc for _, sc in loaded])
        self.assertEqual([i for issues in families.values() for i in issues if i[0] == "FAIL"], [])

    def test_two_question_scenario_needs_exactly_two_questions(self):
        sc = _load("BB-TWOQ-01")
        computed, _ = analyse(sc, DB)
        self.assertEqual(computed["questions_needed"], 2)
        self.assertEqual(len(computed["interpretation_sets"]), 4)
        sc["evaluation_only"]["gold_decision"]["questions_needed"] = 1
        self.assertIn("questions_needed", [i[1] for i in _fails(sc)])

    def test_single_ambiguity_needs_one_question_and_b_variant_none(self):
        self.assertEqual(analyse(_load("BB-LOC-01A"), DB)[0]["questions_needed"], 1)
        self.assertEqual(analyse(_load("BB-LOC-01B"), DB)[0]["questions_needed"], 0)

    def test_swap_and_paraphrase_variants_must_come_in_pairs(self):
        members = [_load(s) for s in ("BB-LOC-01A", "BB-LOC-01B", "BB-LOC-01A-SW", "BB-LOC-01B-SW")]
        self.assertEqual(pair_checks(members), {})
        broken = pair_checks(members[:3])  # B_swap missing
        self.assertIn("FAIL", [i[0] for i in broken["BB-LOC-01"]])

    def test_suggestion_trap_must_exclude_the_correct_restaurants(self):
        sc = _load("BB-SUG-01A")
        self.assertEqual(_fails(sc), [])
        # Pretend the bot suggested the same cuisine: accepting it would not be wrong any more.
        ev = sc["evaluation_only"]
        ev["gold_dialogue_state"]["proposed_not_accepted"][0]["value"] = ev["hidden_user_goal"]["cuisine"]
        self.assertIn("suggestion_trap", [i[1] for i in _fails(sc)])

    def test_hint_detector_flags_the_known_guessable_originals(self):
        originals = [sc for _, sc in load_scenarios(str(ROOT / "data" / "scenarios"))]
        _, per, dataset = hint_report(originals, DB)
        self.assertEqual(sorted(per), ["XX-AMB-03A", "XX-AMB-04A"])
        self.assertIn("hint_last_mentioned", [d[1] for d in dataset])

    def test_hint_detector_flags_same_option_and_recency_bias(self):
        base = _load("BB-LOC-01A")  # station first, mall second
        scs = []
        for k in range(4):
            sc = copy.deepcopy(base)
            sc["scenario_id"] = f"T-{k}"
            sc["evaluation_only"]["hidden_user_goal"]["location"] = "mall"  # always last-mentioned, always mall
            scs.append(sc)
        _, _, dataset = hint_report(scs, DB)
        checks = {d[1] for d in dataset}
        self.assertIn("hint_last_mentioned", checks)
        self.assertIn("hint_same_option", checks)

    def test_drafts_are_balanced(self):
        drafts = [sc for _, sc in load_scenarios(str(DRAFTS))]
        lines, per, dataset = hint_report(drafts, DB)
        self.assertEqual(dataset, [], "\n".join(lines))
        self.assertEqual(dict(per), {})


if __name__ == "__main__":
    unittest.main()
