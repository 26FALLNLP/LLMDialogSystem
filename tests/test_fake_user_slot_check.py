"""The scripted user must not hand out the hidden answer to empty questions."""

import json
import unittest

from src.answer_service import AnswerReply, asks_about
from src.data import DATA_DIR, load_dataset
from src.dialogue_types import Question


class FakeUserSlotCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ids = sorted(p.stem for p in (DATA_DIR / "scenarios").glob("*.json"))
        cls.dataset = load_dataset(cls.ids)

    def test_ok_question_labelled_location_no_longer_leaks(self):
        for scenario_id in self.ids:
            with self.subTest(scenario_id=scenario_id):
                fallback = json.loads((DATA_DIR / "scenarios" / f"{scenario_id}.json").read_text())[
                    "evaluation_only"]["predefined_clarification_answers"]["_unsupported"]
                reply = self.dataset.answer_service.answer(scenario_id, Question("ok?", "location", None))
                self.assertEqual(reply, AnswerReply(fallback, "fallback"))

    def test_real_location_questions_still_get_the_answer(self):
        service = self.dataset.answer_service
        for text in ("Do you mean the station or the mall?", "Which area do you mean?",
                     "Where would you like to eat?", "Which side of town?"):
            with self.subTest(text=text):
                self.assertEqual(service.answer("XX-AMB-01A", Question(text, "location", "t07")),
                                 AnswerReply("Near the station.", "answered"))

    def test_question_must_match_its_own_slot(self):
        service = self.dataset.answer_service
        # A budget question mislabelled as location gets the fallback, not the location.
        self.assertEqual(service.answer("XX-AMB-01A", Question("What's your budget?", "location")).status,
                         "fallback")
        expected = json.loads((DATA_DIR / "scenarios" / "XX-AMB-03A.json").read_text())[
            "evaluation_only"]["predefined_clarification_answers"]["cuisine"]
        self.assertEqual(service.answer("XX-AMB-03A", Question("Which cuisine did they mention?", "cuisine")),
                         AnswerReply(expected, "answered"))

    def test_cue_words(self):
        self.assertTrue(asks_about("max_price", "How much per person?"))
        self.assertTrue(asks_about("max_price", "Under $30?"))
        self.assertTrue(asks_about("dinner", "Is this for lunch or dinner?"))
        self.assertTrue(asks_about("vegetarian", "Any dietary needs?"))
        self.assertFalse(asks_about("location", "ok?"))
        self.assertFalse(asks_about("cuisine", "Sure?"))
        self.assertFalse(asks_about("other", "Where?"))


if __name__ == "__main__":
    unittest.main()
