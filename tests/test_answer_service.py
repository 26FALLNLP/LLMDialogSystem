import unittest

from src.answer_service import AnswerReply, AnswerService
from src.data import load_dataset
from src.dialogue_types import Question


class AnswerServiceTests(unittest.TestCase):
    def test_archived_scenarios_use_their_own_fixed_answers(self):
        dataset = load_dataset(["XX-AMB-01A", "XX-AMB-01B"])
        service = dataset.answer_service
        location = Question("Station or mall?", "location", "t07")
        paraphrase = Question("Where exactly?", "location", "t08")
        self.assertEqual(
            service.answer("XX-AMB-01A", location),
            AnswerReply("Near the station.", "answered"),
        )
        self.assertEqual(
            service.answer("XX-AMB-01A", location),
            service.answer("XX-AMB-01A", paraphrase),
        )
        budget = Question("How much per person?", "max_price")
        self.assertIn("$25", service.answer("XX-AMB-01A", budget).text)
        self.assertIn("$30", service.answer("XX-AMB-01B", budget).text)

    def test_unsupported_question_uses_fixed_fallback(self):
        service = AnswerService(
            {"case": {"_unsupported": "Unknown.", "_multi_question": "One at a time."}}
        )
        for slot in ("other", "_unsupported", "_multi_question"):
            with self.subTest(slot=slot):
                self.assertEqual(
                    service.answer("case", Question("Question", slot)),
                    AnswerReply("Unknown.", "fallback"),
                )
        with self.assertRaises(KeyError):
            service.answer("unknown-case", Question("Where?", "location"))
        with self.assertRaisesRegex(ValueError, "_unsupported"):
            AnswerService({"case": {"location": "At the station."}})

    def test_exact_reference_and_generic_answer_are_distinct(self):
        service = AnswerService.from_exact_tables(
            [
                {
                    "scenario_id": "case",
                    "fallback_text": "Unknown.",
                    "answers": [
                        {"slot": "location", "reference_turn_id": "t07", "text": "By the station."},
                        {"slot": "location", "reference_turn_id": None, "text": "Anywhere."},
                    ],
                }
            ],
            turn_ids_by_scenario={"case": {"t06", "t07"}},
        )
        cases = {
            "t07": AnswerReply("By the station.", "answered"),
            None: AnswerReply("Anywhere.", "answered"),
            "t06": AnswerReply("Unknown.", "fallback"),
        }
        for ref, expected in cases.items():
            with self.subTest(ref=ref):
                self.assertEqual(service.answer("case", Question("Where?", "location", ref)), expected)

    def test_exact_tables_reject_duplicate_keys_and_unknown_prefix_turns(self):
        entry = {"slot": "location", "reference_turn_id": "t07", "text": "By the station."}
        table = {"scenario_id": "case", "fallback_text": "Unknown.", "answers": [entry, entry]}
        with self.assertRaisesRegex(ValueError, "duplicate answer key"):
            AnswerService.from_exact_tables([table], turn_ids_by_scenario={"case": {"t07"}})
        with self.assertRaisesRegex(ValueError, "unknown prefix turn"):
            AnswerService.from_exact_tables([table], turn_ids_by_scenario={"case": {"t06"}})


if __name__ == "__main__":
    unittest.main()
