import json
import unittest
from unittest.mock import patch

from src.claude_client import API_VERSION, DEFAULT_MODEL, EFFORT, ClaudeClient
from src.dialogue_types import ModelRequestError, Usage


class ClaudeClientTests(unittest.TestCase):
    def test_malformed_key_is_rejected_without_exposing_it(self):
        for key in ("", "test-key\r\nHeader: value", "test-key ", "\ttest-key"):
            with self.assertRaisesRegex(ValueError, "ANTHROPIC_API_KEY") as error:
                ClaudeClient(key)
            self.assertNotIn("test-key", str(error.exception))

    def test_structured_request_and_cached_usage(self):
        schema = {"type": "object", "additionalProperties": False}
        payload = {"remaining_budget": 1, "turns": [{"text": "Café near there?"}]}
        with patch("src.claude_client.http.client.HTTPSConnection") as make_connection:
            connection = make_connection.return_value
            response = connection.getresponse.return_value
            response.status = 200
            response.read.return_value = json.dumps({
                "content": [
                    {"type": "thinking", "thinking": "Ignore this block"},
                    {"type": "text", "text": '{"type":'},
                    {"type": "text", "text": '"ASK"}'},
                ],
                "stop_reason": "end_turn",
                "usage": {
                    "input_tokens": 10, "output_tokens": 5,
                    "cache_creation_input_tokens": 8, "cache_read_input_tokens": 7,
                },
            }).encode()
            completion = ClaudeClient("test-key").complete("system prompt", payload, schema)

        make_connection.assert_called_once_with("api.anthropic.com", timeout=60)
        connection.request.assert_called_once()
        args, kwargs = connection.request.call_args
        self.assertEqual(args, ("POST", "/v1/messages"))
        self.assertEqual(kwargs["headers"], {
            "x-api-key": "test-key",
            "anthropic-version": API_VERSION,
            "Content-Type": "application/json",
        })
        body = json.loads(kwargs["body"])
        self.assertEqual(body, {
            "model": DEFAULT_MODEL,
            "max_tokens": 2048,
            "system": "system prompt",
            "messages": [{"role": "user", "content": json.dumps(payload, ensure_ascii=False)}],
            "output_config": {"effort": EFFORT, "format": {"type": "json_schema", "schema": schema}},
        })
        self.assertEqual(completion.text, '{"type":"ASK"}')
        self.assertEqual(completion.stop_reason, "end_turn")
        self.assertEqual(completion.usage, Usage(25, 5, 1))
        connection.close.assert_called_once()

    def test_non_200_is_counted_without_following_redirect_or_reading_error_body(self):
        for status in (302, 401, 429):
            with self.subTest(status=status):
                with patch("src.claude_client.http.client.HTTPSConnection") as make_connection:
                    connection = make_connection.return_value
                    response = connection.getresponse.return_value
                    response.status = status
                    response.read.return_value = b"private diagnostic including test-key"
                    with self.assertRaisesRegex(ModelRequestError, f"HTTP {status}") as error:
                        ClaudeClient("test-key").complete("prompt", {}, {})
                    self.assertNotIn("test-key", str(error.exception))
                    self.assertEqual(error.exception.usage, Usage(None, None, 1))
                    make_connection.assert_called_once()
                    connection.request.assert_called_once()
                    response.read.assert_not_called()
                    connection.close.assert_called_once()

    def test_truncated_structured_response_still_returns_tokens_and_stop_reason(self):
        with patch("src.claude_client.http.client.HTTPSConnection") as make_connection:
            response = make_connection.return_value.getresponse.return_value
            response.status = 200
            response.read.return_value = b'{"content": [], "stop_reason": "max_tokens", "usage": {"input_tokens": 8, "output_tokens": 13}}'
            completion = ClaudeClient("test-key").complete("prompt", {}, {})
        self.assertEqual(completion.text, "")
        self.assertEqual(completion.stop_reason, "max_tokens")
        self.assertEqual(completion.usage, Usage(8, 13, 1))

    def test_timeout_is_sanitized_and_connection_is_closed(self):
        with patch("src.claude_client.http.client.HTTPSConnection") as make_connection:
            connection = make_connection.return_value
            connection.request.side_effect = TimeoutError("private diagnostic including test-key")
            with self.assertRaisesRegex(ModelRequestError, "timed out") as error:
                ClaudeClient("test-key").complete("prompt", {}, {})
            self.assertNotIn("test-key", str(error.exception))
            self.assertEqual(error.exception.usage, Usage(None, None, 1))
            connection.request.assert_called_once()
            connection.close.assert_called_once()

    def test_invalid_response_envelope_retains_known_usage(self):
        with patch("src.claude_client.http.client.HTTPSConnection") as make_connection:
            response = make_connection.return_value.getresponse.return_value
            response.status = 200
            response.read.return_value = b'{"content": null, "usage": {"input_tokens": 8, "output_tokens": 13}}'
            with self.assertRaisesRegex(ModelRequestError, "invalid response envelope") as error:
                ClaudeClient("test-key").complete("prompt", {}, {})
        self.assertEqual(error.exception.usage, Usage(8, 13, 1))
