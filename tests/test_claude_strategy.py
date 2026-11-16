import json
import unittest
from dataclasses import asdict

from src.claude_client import Completion
from src.claude_strategy import ClaudeStrategy
from src.data import load_dataset
from src.dialogue_pipeline import run_dialogue
from src.dialogue_types import Usage


def _ask(slot="Location", reference="t07"):
    return {
        "action": "Ask",
        "questions": [
            {"text": "Do you mean the station or the mall?", "slot": slot, "reference_turn_id": reference}
        ],
        "restaurant_id": None,
    }


def _recommend(restaurant_id):
    return {"action": "Recommend", "questions": [], "restaurant_id": restaurant_id}


class ScriptedClient:
    model = "test-model"

    def __init__(self, *responses):
        self.requests = []
        self._responses = iter(responses)

    def complete(self, system_prompt, user_payload, schema):
        self.requests.append(user_payload)
        response = next(self._responses)
        if isinstance(response, Completion):
            return response
        return Completion(json.dumps(response), Usage(150, 20, 1), "end_turn")


class ClaudeStrategyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset = load_dataset(["XX-AMB-01A", "XX-AMB-01B"])

    def _run(self, scenario_id, client, budget):
        return run_dialogue(
            self.dataset.scenarios[scenario_id],
            ClaudeStrategy(client),
            self.dataset.answer_service,
            budget,
        )

    def test_real_scenario_sends_only_public_context_and_then_delivered_answer(self):
        client = ScriptedClient(_ask(), _recommend("R01"))
        scenario_id = "XX-AMB-01A"
        run = self._run(scenario_id, client, budget=1)

        self.assertEqual(run["system_id"], "claude-dialogue:test-model")
        self.assertEqual(run["termination_reason"], "completed")
        self.assertEqual(run["final_recommendation"], {"restaurant_id": "R01"})
        self.assertEqual(run["usage"], asdict(Usage(300, 40, 2)))

        first, final = client.requests
        scenario = self.dataset.scenarios[scenario_id]
        self.assertEqual(first, {
            "turns": [asdict(turn) for turn in scenario.turns],
            "restaurant_database": [dict(row) for row in scenario.restaurants],
            "remaining_budget": 1,
            "allowed_actions": ["ASK", "RECOMMEND"],
        })
        self.assertEqual(final["turns"][:-2], first["turns"])
        self.assertEqual(final["turns"][-1], {
            "turn_id": "t09", "role": "user", "text": "Near the station.",
        })
        self.assertEqual(final["remaining_budget"], 0)
        self.assertEqual(final["allowed_actions"], ["RECOMMEND"])
        self.assertEqual(run["steps"][0]["action"]["questions"][0]["slot"], "location")

    def test_direct_recommendation_calls_model_once(self):
        client = ScriptedClient(_recommend("R03"))
        run = self._run("XX-AMB-01B", client, budget=2)
        self.assertEqual(run["termination_reason"], "completed")
        self.assertEqual(run["final_recommendation"], {"restaurant_id": "R03"})
        self.assertEqual(run["usage"]["model_calls"], 1)
        self.assertEqual(run["steps"][0]["delivered_questions"], [])
        self.assertEqual(run["steps"][0]["budget_after"], 2)

    def test_pipeline_keeps_budget_and_catalog_checks(self):
        over_budget = self._run("XX-AMB-01A", ScriptedClient(_ask()), budget=0)
        self.assertEqual(over_budget["termination_reason"], "budget_exceeded")
        self.assertEqual(over_budget["steps"][0]["action"]["type"], "ASK")
        self.assertEqual(over_budget["steps"][0]["delivered_questions"], [])

        bad_id = self._run("XX-AMB-01B", ScriptedClient(_recommend("UNKNOWN")), budget=2)
        self.assertEqual(bad_id["termination_reason"], "invalid_restaurant_id")
        self.assertIsNone(bad_id["final_recommendation"])

    def test_unusable_output_preserves_usage_and_diagnostic(self):
        for text, stop_reason in (
            ("not JSON", "end_turn"),
            (json.dumps(_ask(slot="parking")), "end_turn"),
            (json.dumps(_recommend("R03")), "max_tokens"),
            ("Cannot complete", "refusal"),
        ):
            with self.subTest(stop_reason=stop_reason, text=text):
                completion = Completion(text, Usage(90, 10, 1), stop_reason)
                run = self._run("XX-AMB-01B", ScriptedClient(completion), budget=2)
                self.assertEqual(run["termination_reason"], "invalid_action")
                self.assertEqual(run["steps"][0]["raw_output"], text)
                self.assertIn("error", run["steps"][0])
                self.assertEqual(run["usage"], asdict(completion.usage))


if __name__ == "__main__":
    unittest.main()
