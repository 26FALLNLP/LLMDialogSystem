"""Cohen's kappa and the labeling-sheet round trip."""

import csv
import tempfile
import unittest
from pathlib import Path

from scripts.annotator_agreement import (ANNOTATION_DIR, COLUMNS, agreement, cohens_kappa, export_gold,
                                         read_key, read_labels)


class KappaTests(unittest.TestCase):
    def test_textbook_example(self):
        # 50 items: 20 yes/yes, 5 yes/no, 10 no/yes, 15 no/no -> p_o = .70, p_e = .50, kappa = .40
        a = ["yes"] * 20 + ["yes"] * 5 + ["no"] * 10 + ["no"] * 15
        b = ["yes"] * 20 + ["no"] * 5 + ["yes"] * 10 + ["no"] * 15
        self.assertAlmostEqual(cohens_kappa(a, b), 0.4)

    def test_perfect_and_undefined(self):
        self.assertEqual(cohens_kappa(["a", "b", "a"], ["a", "b", "a"]), 1.0)
        self.assertIsNone(cohens_kappa(["a", "a"], ["a", "a"]))
        with self.assertRaises(ValueError):
            cohens_kappa(["a"], ["a", "b"])


class SheetRoundTripTests(unittest.TestCase):
    def test_sheet_has_30_mixed_items_and_no_answers(self):
        key = read_key(ANNOTATION_DIR)
        self.assertEqual(len(key), 30)
        origins = [sid.startswith("BB-") for sid in key.values()]
        self.assertEqual(sum(origins), 15)
        sheet = (ANNOTATION_DIR / "labeling_sheet.md").read_text()
        for sid in key.values():
            self.assertNotIn(sid, sheet)
        for word in ("hidden", "should_ask: yes", "should_ask: no", "UNRESOLVED"):
            self.assertNotIn(word, sheet)
        with open(ANNOTATION_DIR / "labels_template.csv", newline="") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual([r["item"] for r in rows], sorted(key))
        self.assertTrue(all(not r["should_ask"] for r in rows))

    def test_gold_against_itself_and_a_disagreement(self):
        with tempfile.TemporaryDirectory() as tmp:
            gold = Path(tmp) / "gold.csv"
            export_gold(gold, ANNOTATION_DIR)
            rows = read_labels(gold)
            same = agreement(rows, rows)
            self.assertEqual(same["should_ask"]["kappa"], 1.0)
            self.assertEqual(same["active_constraints"]["kappa"], 1.0)
            # Second annotator flips one should_ask label.
            other = {k: dict(v) for k, v in rows.items()}
            first = sorted(other)[0]
            other[first]["should_ask"] = "no" if other[first]["should_ask"] == "yes" else "yes"
            flipped = Path(tmp) / "other.csv"
            with open(flipped, "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=COLUMNS)
                w.writeheader()
                w.writerows(other.values())
            result = agreement(rows, read_labels(flipped))
            self.assertLess(result["should_ask"]["kappa"], 1.0)
            self.assertAlmostEqual(result["should_ask"]["raw_agreement"], 29 / 30)


if __name__ == "__main__":
    unittest.main()
