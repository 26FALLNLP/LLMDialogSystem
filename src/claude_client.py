"""Minimal HTTPS transport for Claude's structured Messages API."""

import http.client
import json
import math
from dataclasses import dataclass

from .dialogue_types import ModelRequestError, Usage


DEFAULT_MODEL = "claude-opus-5-5"
API_VERSION = "2026-10-21"
EFFORT = "low"

_HOST = "api.anthropic.com"
_MESSAGES_PATH = "/v1/messages"


@dataclass(frozen=True)
class Completion:
    text: str
    usage: Usage
    stop_reason: str | None


class ClaudeClient:
    """Make one direct HTTPS request per decision without following redirects."""

    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_MODEL,
        *,
        max_tokens: int = 2048,
        timeout: float = 60,
    ) -> None:
        if not isinstance(api_key, str) or not api_key or any(not 33 <= ord(char) <= 126 for char in api_key):
            raise ValueError("ANTHROPIC_API_KEY must be a nonempty API key without whitespace.")
        if not isinstance(model, str) or not model.strip():
            raise ValueError("A Claude model ID is required.")
        if type(max_tokens) is not int or max_tokens <= 0:
            raise ValueError("max_tokens must be a positive integer.")
        if not math.isfinite(timeout) or timeout <= 0:
            raise ValueError("The Claude request timeout must be finite and positive.")
        self._api_key = api_key
        self.model = model.strip()
        self.max_tokens = max_tokens
        self.timeout = timeout

    def complete(self, system_prompt: str, user_payload: dict, schema: dict) -> Completion:
        body = json.dumps({
            "model": self.model,
            "max_tokens": self.max_tokens,
            "system": system_prompt,
            "messages": [{"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)}],
            "output_config": {"effort": EFFORT, "format": {"type": "json_schema", "schema": schema}},
        }, ensure_ascii=False).encode("utf-8")
        unknown_usage = Usage(input_tokens=None, output_tokens=None, model_calls=1)
        connection = http.client.HTTPSConnection(_HOST, timeout=self.timeout)
        try:
            connection.request("POST", _MESSAGES_PATH, body=body, headers={
                "Authorization": f"Bearer {self._api_key}",
                "anthropic-version": API_VERSION,
                "Content-Type": "application/json",
            })
            response = connection.getresponse()
            if response.status != 200:
                raise ModelRequestError(f"Claude Messages API returned HTTP {response.status}.", unknown_usage)
            data = response.read()
        except TimeoutError:
            raise ModelRequestError("Claude Messages API request timed out.", unknown_usage) from None
        except (OSError, http.client.HTTPException):
            raise ModelRequestError("Claude Messages API request failed before a complete response.", unknown_usage) from None
        finally:
            connection.close()

        try:
            envelope = json.loads(data)
        except (json.JSONDecodeError, UnicodeDecodeError):
            raise ModelRequestError("Claude Messages API returned invalid JSON.", unknown_usage) from None
        if not isinstance(envelope, dict):
            raise ModelRequestError("Claude Messages API returned an invalid response envelope.", unknown_usage)

        usage = _read_usage(envelope.get("usage"))
        content = envelope.get("content")
        stop_reason = envelope.get("stop_reason")
        if not isinstance(content, list) or (stop_reason is not None and not isinstance(stop_reason, str)):
            raise ModelRequestError("Claude Messages API returned an invalid response envelope.", usage)
        texts = []
        for block in content:
            if not isinstance(block, dict):
                raise ModelRequestError("Claude Messages API returned an invalid content block.", usage)
            if block.get("type") == "text":
                if not isinstance(block.get("text"), str):
                    raise ModelRequestError("Claude Messages API returned an invalid text block.", usage)
                texts.append(block["text"])

        return Completion("".join(texts), usage, stop_reason)


def _read_usage(raw: object) -> Usage:
    if not isinstance(raw, dict):
        return Usage(input_tokens=None, output_tokens=None, model_calls=1)
    input_counts = (
        raw.get("input_tokens"),
        raw.get("cache_creation_input_tokens", 0),
        raw.get("cache_read_input_tokens", 0),
    )
    output = raw.get("output_tokens")
    return Usage(
        input_tokens=sum(input_counts) if all(_is_count(count) for count in input_counts) else None,
        output_tokens=output if _is_count(output) else None,
        model_calls=1,
    )


def _is_count(value: object) -> bool:
    return type(value) is int and value >= 0
