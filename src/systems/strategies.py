"""Systems S2-S5. S1 is src/claude_strategy.ClaudeStrategy (unchanged).

All systems get the same DialogueContext (conversation, catalog, remaining
budget, allowed actions), use the same Claude client and the same ASK /
RECOMMEND actions, and return a Decision with usage, raw model output and a
state snapshot, so the existing pipeline, scripted user and scorer apply.

  S2 SummaryStrategy        model writes a plain-text summary, then decides (S1 prompt)
  S3 MemoryLinksStrategy    model updates a structured memory WITH relation links after
                            every turn; ordinary code builds the state and applies the rule
  S4 MemoryNoLinksStrategy  own pipeline: memory WITHOUT relation links (none are ever
                            asked for or stored); code builds the state from statuses
  S5 MemoryLinksAskStrategy S3's memory and links, but the model decides (S1 prompt)
"""

import json
from dataclasses import asdict
from pathlib import Path

from ..claude_strategy import ACTION_SCHEMA, PROMPT_VARIANTS, _parse_action
from ..dialogue_types import Decision, DialogueContext, ModelRequestError, Usage
from .state import RELATIONS, SLOTS, STATUSES, add_usage, apply_rule, build_state

PROMPTS = Path(__file__).resolve().parent / "prompts"
SUMMARY_PROMPT = (PROMPTS / "s2_summary.txt").read_text(encoding="utf-8")
EXTRACT_WITH_LINKS_PROMPT = (PROMPTS / "s3_extract_with_links.txt").read_text(encoding="utf-8")
EXTRACT_NO_LINKS_PROMPT = (PROMPTS / "s4_extract_no_links.txt").read_text(encoding="utf-8")
SUMMARY_NOTE = ("\n\nThe input also contains \"summary\": a plain-text summary of the conversation "
                "that you wrote just before this step.")
MEMORY_NOTE = ("\n\nThe input also contains \"memory\": requirements extracted from the conversation "
               "(propositions with a status, and relation links between turns), and \"state\": the "
               "active, unresolved, superseded and unaccepted requirements derived from that memory.")

_TURN_REF = {"anyOf": [{"type": "string"}, {"type": "null"}]}
_VALUE = {"anyOf": [{"type": "string"}, {"type": "number"}, {"type": "boolean"},
                    {"type": "array", "items": {"type": "string"}}, {"type": "null"}]}
_OPTION = {"anyOf": [{"type": "string"}, {"type": "number"}, {"type": "boolean"}]}
PROPOSITION_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "slot": {"type": "string", "enum": list(SLOTS)},
        "value": _VALUE,
        "options": {"type": "array", "items": _OPTION},
        "content": {"type": "string"},
        "speaker": {"type": "string", "enum": ["user", "assistant"]},
        "source_turn": {"type": "string"},
        "status": {"type": "string", "enum": list(STATUSES)},
        "active": {"type": "boolean"},
        "evidence_turn": _TURN_REF,
    },
    "required": ["id", "slot", "value", "options", "content", "speaker", "source_turn", "status",
                 "active", "evidence_turn"],
    "additionalProperties": False,
}
LINK_SCHEMA = {
    "type": "object",
    "properties": {
        "source_turn": {"type": "string"},
        "target_turn": {"type": "string"},
        "relation": {"type": "string", "enum": list(RELATIONS)},
        "slot": {"type": "string", "enum": list(SLOTS)},
    },
    "required": ["source_turn", "target_turn", "relation", "slot"],
    "additionalProperties": False,
}
MEMORY_WITH_LINKS_SCHEMA = {
    "type": "object",
    "properties": {"propositions": {"type": "array", "items": PROPOSITION_SCHEMA},
                   "relation_links": {"type": "array", "items": LINK_SCHEMA}},
    "required": ["propositions", "relation_links"],
    "additionalProperties": False,
}
MEMORY_NO_LINKS_SCHEMA = {
    "type": "object",
    "properties": {"propositions": {"type": "array", "items": PROPOSITION_SCHEMA}},
    "required": ["propositions"],
    "additionalProperties": False,
}
SUMMARY_SCHEMA = {
    "type": "object",
    "properties": {"summary": {"type": "string"}},
    "required": ["summary"],
    "additionalProperties": False,
}


class _StepFailed(Exception):
    def __init__(self, message, usage, raws):
        super().__init__(message)
        self.usage, self.raws = usage, raws


def _call(client, prompt, payload, schema, usage, raws):
    """One model call; returns (parsed JSON, usage so far). Errors keep the usage."""
    try:
        completion = client.complete(prompt, payload, schema)
    except ModelRequestError as exc:
        raise ModelRequestError(str(exc), add_usage(usage, exc.usage)) from None
    usage = add_usage(usage, completion.usage)
    raws.append(completion.text)
    if completion.stop_reason != "end_turn":
        raise _StepFailed(f"Claude returned an incomplete reply (stop_reason={completion.stop_reason!r}).",
                          usage, raws)
    try:
        data = json.loads(completion.text)
    except json.JSONDecodeError:
        raise _StepFailed("Claude did not return JSON.", usage, raws) from None
    if not isinstance(data, dict) or set(data) != set(schema["properties"]):
        raise _StepFailed("Claude's reply does not match the requested fields.", usage, raws)
    return data, usage


def _public_payload(context: DialogueContext) -> dict:
    return {
        "turns": [asdict(turn) for turn in context.turns],
        "restaurant_database": [dict(row) for row in context.restaurant_database],
        "remaining_budget": context.remaining_budget,
        "allowed_actions": list(context.allowed_actions),
    }


def _variant_suffix(prompt_variant):
    if prompt_variant not in PROMPT_VARIANTS:
        raise ValueError(f"Unknown prompt variant {prompt_variant!r}; choose {sorted(PROMPT_VARIANTS)}")
    return "" if prompt_variant == "rule_given" else "-plain"


# ----------------------------------------------------------------- S2
class SummaryStrategy:
    """S2: the model writes a plain-text summary first, then decides with the S1 prompt."""

    def __init__(self, client, prompt_variant: str = "rule_given") -> None:
        self._client = client
        self.system_id = f"s2-summary{_variant_suffix(prompt_variant)}:{client.model}"
        self.prompt_version = "s2-summary-v1+" + PROMPT_VARIANTS[prompt_variant][0]
        self._decision_prompt = PROMPT_VARIANTS[prompt_variant][1] + SUMMARY_NOTE

    def decide(self, context: DialogueContext) -> Decision:
        usage, raws = Usage(0, 0, 0), []
        try:
            summary, usage = _call(self._client, SUMMARY_PROMPT,
                                   {"turns": [asdict(t) for t in context.turns]}, SUMMARY_SCHEMA, usage, raws)
            snapshot = {"summary": summary["summary"]}
            payload = {**_public_payload(context), "summary": summary["summary"]}
            try:
                completion = self._client.complete(self._decision_prompt, payload, ACTION_SCHEMA)
            except ModelRequestError as exc:
                raise ModelRequestError(str(exc), add_usage(usage, exc.usage)) from None
            usage = add_usage(usage, completion.usage)
            raws.append(completion.text)
            if completion.stop_reason != "end_turn":
                raise _StepFailed(f"Claude returned an incomplete action (stop_reason={completion.stop_reason!r}).",
                                  usage, raws)
            try:
                action = _parse_action(completion.text)
            except ValueError as exc:
                raise _StepFailed(str(exc), usage, raws) from None
        except _StepFailed as exc:
            return Decision(None, error=str(exc), usage=exc.usage, raw_output=json.dumps(exc.raws))
        return Decision(action, state_snapshot=snapshot, usage=usage, raw_output=json.dumps(raws))


# ----------------------------------------------------------------- memory pipelines
class _Memory:
    """Turn-by-turn memory: one extraction call per new turn."""

    def __init__(self, prompt, schema, with_links):
        self.prompt, self.schema, self.with_links = prompt, schema, with_links
        self.memory = {"propositions": [], **({"relation_links": []} if with_links else {})}
        self.seen: list[tuple[str, str, str]] = []
        self.per_turn: list[dict] = []

    def update(self, client, context, usage, raws):
        turns = [(t.turn_id, t.role, t.text) for t in context.turns]
        if turns[:len(self.seen)] != self.seen:  # a different dialogue: start again
            self.__init__(self.prompt, self.schema, self.with_links)
        for index in range(len(self.seen), len(turns)):
            payload = {"memory": self.memory,
                       "conversation": [asdict(t) for t in context.turns[:index + 1]],
                       "newest_turn_id": context.turns[index].turn_id}
            data, usage = _call(client, self.prompt, payload, self.schema, usage, raws)
            self.memory = data
            self.seen.append(turns[index])
            state = build_state(data["propositions"], data.get("relation_links") if self.with_links else None,
                                context.restaurant_database)
            self.per_turn.append({"turn_id": context.turns[index].turn_id, **state})
        return usage


class MemoryLinksStrategy:
    """S3 (proposed): memory with relation links; ordinary code applies revisions,
    builds the constraints, filters the catalog per meaning and applies the rule."""

    system_name = "s3-memory-links"

    def __init__(self, client, prompt_variant: str = "rule_given") -> None:
        self._client = client
        self._memory = _Memory(EXTRACT_WITH_LINKS_PROMPT, MEMORY_WITH_LINKS_SCHEMA, with_links=True)
        self.system_id = f"{self.system_name}:{client.model}"
        self.prompt_version = "s3-extract-links-v1"

    def _state(self, context, usage, raws):
        usage = self._memory.update(self._client, context, usage, raws)
        memory = self._memory.memory
        state = build_state(memory["propositions"], memory.get("relation_links", []), context.restaurant_database)
        return state, usage

    def _snapshot(self, state, trace=None):
        return {**state, "propositions": self._memory.memory["propositions"],
                "per_turn": list(self._memory.per_turn), **({"rule_trace": trace} if trace else {})}

    def decide(self, context: DialogueContext) -> Decision:
        usage, raws = Usage(0, 0, 0), []
        try:
            state, usage = self._state(context, usage, raws)
        except _StepFailed as exc:
            return Decision(None, error=str(exc), usage=exc.usage, raw_output=json.dumps(exc.raws))
        action, trace = apply_rule(state, context.restaurant_database, context.remaining_budget)
        return Decision(action, state_snapshot=self._snapshot(state, trace), usage=usage,
                        raw_output=json.dumps(raws))


class MemoryNoLinksStrategy:
    """S4 (ablation): its own pipeline. The extraction prompt and schema contain no
    relation links, so none are ever produced or stored; the state is built from
    the propositions' statuses alone. Same rule as S3."""

    def __init__(self, client, prompt_variant: str = "rule_given") -> None:
        self._client = client
        self._memory = _Memory(EXTRACT_NO_LINKS_PROMPT, MEMORY_NO_LINKS_SCHEMA, with_links=False)
        self.system_id = f"s4-memory-nolinks:{client.model}"
        self.prompt_version = "s4-extract-nolinks-v1"

    def decide(self, context: DialogueContext) -> Decision:
        usage, raws = Usage(0, 0, 0), []
        try:
            usage = self._memory.update(self._client, context, usage, raws)
        except _StepFailed as exc:
            return Decision(None, error=str(exc), usage=exc.usage, raw_output=json.dumps(exc.raws))
        state = build_state(self._memory.memory["propositions"], None, context.restaurant_database)
        action, trace = apply_rule(state, context.restaurant_database, context.remaining_budget)
        snapshot = {**state, "propositions": self._memory.memory["propositions"],
                    "per_turn": list(self._memory.per_turn), "rule_trace": trace}
        return Decision(action, state_snapshot=snapshot, usage=usage, raw_output=json.dumps(raws))


class MemoryLinksAskStrategy(MemoryLinksStrategy):
    """S5 (optional): S3's memory and links, but the model decides ASK/RECOMMEND
    with the S1 prompt instead of the coded rule."""

    def __init__(self, client, prompt_variant: str = "rule_given") -> None:
        super().__init__(client)
        self.system_id = f"s5-memory-links-llm-ask{_variant_suffix(prompt_variant)}:{client.model}"
        self.prompt_version = "s3-extract-links-v1+" + PROMPT_VARIANTS[prompt_variant][0]
        self._decision_prompt = PROMPT_VARIANTS[prompt_variant][1] + MEMORY_NOTE

    def decide(self, context: DialogueContext) -> Decision:
        usage, raws = Usage(0, 0, 0), []
        try:
            state, usage = self._state(context, usage, raws)
            payload = {**_public_payload(context), "memory": self._memory.memory, "state": state}
            try:
                completion = self._client.complete(self._decision_prompt, payload, ACTION_SCHEMA)
            except ModelRequestError as exc:
                raise ModelRequestError(str(exc), add_usage(usage, exc.usage)) from None
            usage = add_usage(usage, completion.usage)
            raws.append(completion.text)
            if completion.stop_reason != "end_turn":
                raise _StepFailed(f"Claude returned an incomplete action (stop_reason={completion.stop_reason!r}).",
                                  usage, raws)
            try:
                action = _parse_action(completion.text)
            except ValueError as exc:
                raise _StepFailed(str(exc), usage, raws) from None
        except _StepFailed as exc:
            return Decision(None, error=str(exc), usage=exc.usage, raw_output=json.dumps(exc.raws))
        return Decision(action, state_snapshot=self._snapshot(state), usage=usage, raw_output=json.dumps(raws))
