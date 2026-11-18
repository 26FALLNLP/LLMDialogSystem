"""Rule-given vs plain Claude prompt."""

import json
import unittest

from src.claude_client import Completion
from src.claude_strategy import (PLAIN_SYSTEM_PROMPT, PROMPT_VARIANTS, PROMPT_VERSION, SYSTEM_PROMPT,
                                 ClaudeStrategy)
from src.dialogue_types import DialogueContext, Turn, Usage


class RecordingClient:
    model = "test-model"

    def __init__(self):
        self.system_prompts = []

    def complete(self, system_prompt, payload, schema):
        self.system_prompts.append(system_prompt)
        return Completion(json.dumps({"action": "RECOMMEND", "questions": [], "restaurant_id": "R01"}),
                          Usage(10, 5, 1), "end_turn")


CONTEXT = DialogueContext((Turn("t01", "user", "Hi"),), ({"restaurant_id": "R01"},), 1, ("ASK", "RECOMMEND"))

ASK_RULE = "Recommend a single restaurant\nthat satisfies every interpretation"
SUGGESTION_RULE = "Activate an assistant\nsuggestion only if the user accepts it"


class PromptVariantTests(unittest.TestCase):
    def test_rule_given_is_the_original_prompt(self):
        self.assertEqual(PROMPT_VARIANTS["rule_given"], (PROMPT_VERSION, SYSTEM_PROMPT))
        self.assertIn(ASK_RULE, SYSTEM_PROMPT)
        self.assertIn(SUGGESTION_RULE, SYSTEM_PROMPT)

    def test_plain_prompt_leaves_out_the_rules_but_keeps_the_format(self):
        self.assertNotIn(ASK_RULE, PLAIN_SYSTEM_PROMPT)
        self.assertNotIn(SUGGESTION_RULE, PLAIN_SYSTEM_PROMPT)
        self.assertNotIn("interpretation", PLAIN_SYSTEM_PROMPT)
        self.assertNotIn("agreement", PLAIN_SYSTEM_PROMPT)
        output_format = SYSTEM_PROMPT.split("\n\n")[-1]
        self.assertTrue(output_format.startswith("Return one structured action."))
        self.assertTrue(PLAIN_SYSTEM_PROMPT.endswith(output_format))

    def test_strategy_sends_the_chosen_prompt_and_labels_the_system(self):
        for variant, expected_prompt, system_id in (
            ("rule_given", SYSTEM_PROMPT, "claude-dialogue:test-model"),
            ("plain", PLAIN_SYSTEM_PROMPT, "claude-dialogue-plain:test-model"),
        ):
            with self.subTest(variant=variant):
                client = RecordingClient()
                strategy = ClaudeStrategy(client, variant)
                strategy.decide(CONTEXT)
                self.assertEqual(client.system_prompts, [expected_prompt])
                self.assertEqual(strategy.system_id, system_id)
        self.assertEqual(ClaudeStrategy(RecordingClient()).prompt_variant, "rule_given")
        with self.assertRaises(ValueError):
            ClaudeStrategy(RecordingClient(), "other")


if __name__ == "__main__":
    unittest.main()
