"""Serve deterministic answers from scenario-specific lookup tables."""

from collections.abc import Collection, Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType
from typing import Literal, TypeGuard

from .dialogue_types import Question


@dataclass(frozen=True, slots=True)
class AnswerReply:
    text: str
    status: Literal["answered", "fallback"]


AnswerKey = str | tuple[str, str | None]


@dataclass(frozen=True, slots=True)
class _AnswerTable:
    replies: Mapping[AnswerKey, str]
    fallback_text: str
    reference_scoped: bool


class AnswerService:
    """Use the archived slot tables or explicit turn-scoped tables."""

    def __init__(self, tables: Mapping[str, object]) -> None:
        self._tables: dict[str, _AnswerTable] = {}
        for scenario_id, raw_table in tables.items():
            if not _has_text(scenario_id):
                raise ValueError("Answer tables require a nonempty scenario_id")
            if not isinstance(raw_table, Mapping):
                raise ValueError(f"{scenario_id}: expected a slot-based answer table")
            fallback = raw_table.get("_unsupported")
            if not _has_text(fallback):
                raise ValueError(f"{scenario_id}: expected a nonempty _unsupported reply")

            answers: dict[AnswerKey, str] = {}
            for slot, reply in raw_table.items():
                if not _has_text(reply):
                    raise ValueError(f"{scenario_id}: empty or invalid reply for {slot!r}")
                if slot in ("_unsupported", "_multi_question"):
                    continue
                if not _valid_slot(slot):
                    raise ValueError(f"{scenario_id}: invalid answer slot {slot!r}")
                answers[slot] = reply
            self._tables[scenario_id] = _AnswerTable(
                MappingProxyType(answers), fallback, reference_scoped=False
            )

    @classmethod
    def from_exact_tables(
        cls,
        tables: Sequence[Mapping[str, object]],
        *,
        turn_ids_by_scenario: Mapping[str, Collection[str]],
    ) -> "AnswerService":
        """Load explicit slot/turn keys validated against each fixed dialogue prefix."""
        service = cls({})
        for table in tables:
            if not isinstance(table, Mapping):
                raise ValueError("Expected an exact answer table object")
            scenario_id = table.get("scenario_id")
            if not _has_text(scenario_id):
                raise ValueError("Answer tables require a nonempty scenario_id")
            if scenario_id in service._tables:
                raise ValueError(f"{scenario_id}: duplicate answer table")
            if scenario_id not in turn_ids_by_scenario:
                raise ValueError(f"{scenario_id}: no fixed prefix turn IDs supplied")

            fallback = table.get("fallback_text")
            rows = table.get("answers")
            if not _has_text(fallback) or not isinstance(rows, list):
                raise ValueError(f"{scenario_id}: expected answers and a nonempty fallback_text")

            visible_turn_ids = turn_ids_by_scenario[scenario_id]
            answers: dict[AnswerKey, str] = {}
            for row in rows:
                if not isinstance(row, Mapping) or "reference_turn_id" not in row:
                    raise ValueError(f"{scenario_id}: each answer requires a reference_turn_id")
                slot, reference, reply = row.get("slot"), row["reference_turn_id"], row.get("text")
                if not _valid_slot(slot) or not _has_text(reply):
                    raise ValueError(f"{scenario_id}: invalid slot or empty reply in exact table")
                if reference is not None and (
                    not isinstance(reference, str) or reference not in visible_turn_ids
                ):
                    raise ValueError(f"{scenario_id}: unknown prefix turn {reference!r}")
                key = (slot, reference)
                if key in answers:
                    raise ValueError(f"{scenario_id}: duplicate answer key {key!r}")
                answers[key] = reply
            service._tables[scenario_id] = _AnswerTable(
                MappingProxyType(answers), fallback, reference_scoped=True
            )
        return service

    def answer(self, scenario_id: str, question: Question) -> AnswerReply:
        table = self._tables[scenario_id]
        key: AnswerKey = (
            (question.slot, question.reference_turn_id) if table.reference_scoped else question.slot
        )
        reply = table.replies.get(key)
        if reply is None:
            return AnswerReply(text=table.fallback_text, status="fallback")
        return AnswerReply(text=reply, status="answered")


def _has_text(value: object) -> TypeGuard[str]:
    return isinstance(value, str) and bool(value.strip())


def _valid_slot(value: object) -> TypeGuard[str]:
    return _has_text(value) and value == value.strip() and not value.startswith("_") and value != "other"
