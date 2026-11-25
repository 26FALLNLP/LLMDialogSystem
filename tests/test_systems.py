"""S2-S5 with FAKE model replies (no API calls), run through the real pipeline,
scripted user and scorer."""

import json
import unittest

from src.claude_client import Completion
from src.claude_strategy import PROMPT_VARIANTS
from src.data import load_dataset, scenario_path
from src.dialogue_pipeline import run_dialogue
from src.dialogue_types import Ask, ModelRequestError, Recommend, Usage
from src.scoring_service import score
from src.systems import SYSTEMS, build_strategy
from src.systems.state import apply_rule, build_state
from src.systems.strategies import MEMORY_NO_LINKS_SCHEMA, MEMORY_WITH_LINKS_SCHEMA

IDS = ("XX-AMB-01A", "XX-AMB-01B", "XX-AMB-12A", "XX-SUG-05")


def prop(pid, slot, value, turn, status="acknowledged", speaker="user", options=()):
    return {"id": pid, "slot": slot, "value": value, "options": list(options), "content": f"{slot}={value}",
            "speaker": speaker, "source_turn": turn, "status": status,
            "active": status == "acknowledged", "evidence_turn": turn}


# What a perfect extractor would have stored after each turn, per scenario.
PLANS = {
    "XX-AMB-01A": {
        "t01": [prop("p1", "cuisine", "Japanese", "t01")],
        "t03": [prop("p2", "max_price", 25, "t03")],
        "t07": [prop("p3", "location", None, "t07", "unresolved", options=("station", "mall"))],
        "t09": [prop("p4", "location", "station", "t09")],
    },
    "XX-AMB-01B": {
        "t01": [prop("p1", "cuisine", "Japanese", "t01")],
        "t03": [prop("p2", "max_price", 30, "t03")],
        "t07": [prop("p3", "location", None, "t07", "unresolved", options=("station", "mall"))],
    },
    "XX-AMB-12A": {
        "t03": [prop("p1", "dinner", True, "t03")],
        "t05": [prop("p2", "max_price", 28, "t05")],
        "t07": [prop("p3", "cuisine", None, "t07", "unresolved", options=("Japanese", "Korean")),
                prop("p4", "location", None, "t07", "unresolved", options=("station", "mall"))],
        "t09": [prop("p5", "cuisine", "Japanese", "t09")],
        "t11": [prop("p6", "location", "station", "t11")],
    },
}
CLARIFY = {("XX-AMB-01A", "t09"): ("t07", "location"), ("XX-AMB-12A", "t09"): ("t07", "cuisine"),
           ("XX-AMB-12A", "t11"): ("t07", "location")}


class FakeClient:
    """Answers like Claude would, chosen by the requested schema. Records every call."""

    model = "fake-model"

    def __init__(self, scenario_id, action=None, links=True, fail_on_call=None, bad_json_on_call=None):
        self.scenario_id, self.action, self.links = scenario_id, action, links
        self.fail_on_call, self.bad_json_on_call = fail_on_call, bad_json_on_call
        self.calls = []

    def complete(self, system_prompt, payload, schema):
        self.calls.append({"prompt": system_prompt, "payload": payload, "schema": schema})
        n = len(self.calls)
        if n == self.fail_on_call:
            raise ModelRequestError("HTTP 529", Usage(None, None, 1))
        usage = Usage(100, 20, 1)
        if n == self.bad_json_on_call:
            return Completion("not json", usage, "end_turn")
        keys = set(schema["properties"])
        if keys == {"summary"}:
            return Completion(json.dumps({"summary": "User wants Japanese food, budget given; area unclear."}),
                              usage, "end_turn")
        if "propositions" in keys:
            return Completion(json.dumps(self.memory(payload, "relation_links" in keys)), usage, "end_turn")
        return Completion(json.dumps(self.action(payload)), usage, "end_turn")

    def memory(self, payload, with_links):
        newest = payload["newest_turn_id"]
        props = list(payload["memory"]["propositions"])
        props += PLANS.get(self.scenario_id, {}).get(newest, [])
        links = list(payload["memory"].get("relation_links", []))
        if (self.scenario_id, newest) in CLARIFY:
            target, slot = CLARIFY[(self.scenario_id, newest)]
            if with_links and self.links:
                links.append({"source_turn": newest, "target_turn": target, "relation": "clarify", "slot": slot})
            else:  # no links: the model itself marks the settled reference superseded
                props = [dict(p, status="superseded") if p["source_turn"] == target and p["slot"] == slot else p
                         for p in props]
        return {"propositions": props, **({"relation_links": links} if with_links else {})}


class SystemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset = load_dataset(list(IDS))
        cls.gold = {i: {**json.loads(scenario_path(i).read_text())["evaluation_only"], "scenario_id": i} for i in IDS}

    def run_system(self, name, scenario_id, budget, client, variant="rule_given"):
        scenario = self.dataset.scenarios[scenario_id]
        record = run_dialogue(scenario, build_strategy(name, client, variant), self.dataset.answer_service, budget)
        return record, score(record, self.gold[scenario_id], scenario.restaurants)

    # ---------------------------------------------------------------- S3
    def test_s3_extracts_every_turn_asks_the_rule_question_then_recommends(self):
        client = FakeClient("XX-AMB-01A")
        record, result = self.run_system("s3", "XX-AMB-01A", 1, client)
        self.assertEqual(record["termination_reason"], "completed")
        first, second = record["steps"]
        self.assertEqual(first["action"]["type"], "ASK")
        question = first["action"]["questions"][0]
        self.assertEqual(question["slot"], "location")
        self.assertIn("station", question["text"])
        self.assertEqual(first["delivered_questions"][0]["reply"]["status"], "answered")
        self.assertEqual(second["action"], {"type": "RECOMMEND", "restaurant_id": "R01"})
        self.assertEqual(len(client.calls), 7 + 2)                  # one extraction call per turn
        self.assertEqual(record["usage"]["model_calls"], 9)
        self.assertTrue(result["task_success"])
        self.assertEqual(result["question_scores"][0]["judgment"], "useful")
        self.assertTrue(result["state_metrics"]["exact_match"])     # state snapshot scored at the checkpoint
        self.assertEqual(len(first["state_snapshot"]["per_turn"]), 7)

    def test_s3_recommends_a_shared_restaurant_without_asking(self):
        record, result = self.run_system("s3", "XX-AMB-01B", 1, FakeClient("XX-AMB-01B"))
        self.assertEqual(record["steps"][0]["action"], {"type": "RECOMMEND", "restaurant_id": "R03"})
        self.assertEqual(result["question_counts"]["delivered"], 0)
        self.assertTrue(result["task_success"])

    def test_s3_with_no_budget_makes_a_best_guess(self):
        record, _ = self.run_system("s3", "XX-AMB-01A", 0, FakeClient("XX-AMB-01A"))
        self.assertEqual(record["steps"][0]["action"]["type"], "RECOMMEND")
        self.assertEqual(record["steps"][0]["state_snapshot"]["rule_trace"]["rule"], "best_guess")

    def test_s3_two_question_scenario_asks_both(self):
        record, result = self.run_system("s3", "XX-AMB-12A", 2, FakeClient("XX-AMB-12A"))
        asked = [s["action"]["questions"][0]["slot"] for s in record["steps"] if s["action"]["type"] == "ASK"]
        self.assertEqual(sorted(asked), ["cuisine", "location"])
        self.assertTrue(result["task_success"])
        self.assertEqual([q["judgment"] for q in result["question_scores"]], ["useful", "useful"])

    # ---------------------------------------------------------------- S4
    def test_s4_never_asks_for_or_stores_relation_links(self):
        self.assertNotIn("relation_links", json.dumps(MEMORY_NO_LINKS_SCHEMA))
        self.assertIn("relation_links", json.dumps(MEMORY_WITH_LINKS_SCHEMA))
        client = FakeClient("XX-AMB-01A")
        record, result = self.run_system("s4", "XX-AMB-01A", 1, client)
        for call in client.calls:
            self.assertNotIn("relation_links", json.dumps(call["schema"]))
            self.assertNotIn("relation_links", call["payload"]["memory"])
            self.assertNotIn("relation", call["prompt"].split("Lunch")[0].lower().replace("relations", ""))
        for step in record["steps"]:
            self.assertNotIn("relation_links", step["state_snapshot"])
        self.assertTrue(result["task_success"])                      # status-based update still works
        self.assertNotEqual(build_strategy("s4", client).system_id, build_strategy("s3", client).system_id)

    # ---------------------------------------------------------------- code that applies links
    def test_links_drive_revisions_and_confirmations_in_s3_only(self):
        catalog = self.dataset.scenarios["XX-AMB-01A"].restaurants
        props = [prop("p1", "cuisine", "Italian", "t01"), prop("p2", "cuisine", "Japanese", "t05", "acknowledged"),
                 prop("p3", "max_price", 30, "t03", "acknowledged", speaker="assistant")]
        # S3: the assistant's price proposal counts only with a confirm link.
        no_confirm = build_state(props, [{"source_turn": "t05", "target_turn": "t01", "relation": "revise",
                                          "slot": "cuisine"}], catalog)
        self.assertEqual(no_confirm["active"], {"cuisine": "Japanese"})
        self.assertEqual(no_confirm["proposed_not_accepted"][0]["value"], 30)
        self.assertIn({"slot": "cuisine", "turn": 1, "value": "Italian"}, no_confirm["superseded"])
        confirmed = build_state(props, [{"source_turn": "t04", "target_turn": "t03", "relation": "confirm",
                                         "slot": "max_price"}], catalog)
        self.assertEqual(confirmed["active"]["max_price"], 30)
        # S4 (links=None): the statuses decide; nothing is ever demoted or promoted by a link.
        s4 = build_state(props, None, catalog)
        self.assertEqual(s4["active"]["max_price"], 30)
        self.assertNotIn("relation_links", s4)

    def test_rule_recommends_shared_candidate_else_asks_else_guesses(self):
        catalog = self.dataset.scenarios["XX-AMB-01A"].restaurants
        state = {"active": {"cuisine": "Japanese", "max_price": 30}, "superseded": [], "proposed_not_accepted": [],
                 "unresolved": [{"slot": "location", "turn": 7, "interpretations": [{"location": "station"},
                                                                                   {"location": "mall"}]}]}
        self.assertEqual(apply_rule(state, catalog, 1)[0], Recommend("R03"))
        state["active"]["max_price"] = 25
        self.assertIsInstance(apply_rule(state, catalog, 1)[0], Ask)
        self.assertIsInstance(apply_rule(state, catalog, 0)[0], Recommend)

    # ---------------------------------------------------------------- S2
    def test_s2_writes_a_summary_then_decides_with_the_s1_prompt(self):
        client = FakeClient("XX-AMB-01B", action=lambda p: {"action": "RECOMMEND", "questions": [],
                                                            "restaurant_id": "R03"})
        record, result = self.run_system("s2", "XX-AMB-01B", 1, client)
        self.assertEqual(len(client.calls), 2)
        self.assertEqual(set(client.calls[0]["schema"]["properties"]), {"summary"})
        self.assertIn("summary", client.calls[1]["payload"])
        self.assertTrue(client.calls[1]["prompt"].startswith(PROMPT_VARIANTS["rule_given"][1]))
        self.assertIn("summary", record["steps"][0]["state_snapshot"])
        self.assertTrue(result["task_success"])
        plain = FakeClient("XX-AMB-01B", action=lambda p: {"action": "RECOMMEND", "questions": [],
                                                           "restaurant_id": "R03"})
        self.run_system("s2", "XX-AMB-01B", 1, plain, "plain")
        self.assertTrue(plain.calls[1]["prompt"].startswith(PROMPT_VARIANTS["plain"][1]))

    # ---------------------------------------------------------------- S5
    def test_s5_uses_s3_memory_but_the_model_decides(self):
        def ask_then_recommend(payload):
            if payload["remaining_budget"]:
                return {"action": "ASK", "restaurant_id": None, "questions": [
                    {"text": "Near the station or the mall?", "slot": "location", "reference_turn_id": "t07"}]}
            return {"action": "RECOMMEND", "questions": [], "restaurant_id": "R01"}
        client = FakeClient("XX-AMB-01A", action=ask_then_recommend)
        record, result = self.run_system("s5", "XX-AMB-01A", 1, client)
        decisions = [c for c in client.calls if "propositions" not in c["schema"]["properties"]]
        self.assertEqual(len(decisions), 2)
        self.assertIn("memory", decisions[0]["payload"])
        self.assertIn("relation_links", decisions[0]["payload"]["memory"])
        self.assertEqual(decisions[0]["payload"]["state"]["unresolved"][0]["slot"], "location")
        self.assertTrue(result["task_success"])

    # ---------------------------------------------------------------- failures
    def test_unusable_reply_and_api_error_keep_usage(self):
        record, result = self.run_system("s3", "XX-AMB-01A", 1, FakeClient("XX-AMB-01A", bad_json_on_call=3))
        self.assertEqual(record["termination_reason"], "invalid_action")
        self.assertEqual(record["usage"]["model_calls"], 3)
        self.assertFalse(result["task_success"])
        record, _ = self.run_system("s3", "XX-AMB-01A", 1, FakeClient("XX-AMB-01A", fail_on_call=4))
        self.assertEqual(record["termination_reason"], "model_error")
        self.assertEqual(record["usage"]["model_calls"], 4)

    def test_every_system_is_registered_and_can_ask(self):
        self.assertEqual(sorted(SYSTEMS), ["s1", "s2", "s3", "s4", "s5"])
        for name in SYSTEMS:
            self.assertTrue(build_strategy(name, FakeClient("XX-AMB-01A")).system_id.endswith("fake-model"))


if __name__ == "__main__":
    unittest.main()
