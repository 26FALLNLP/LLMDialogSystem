"""Data passed between the pipeline and a dialogue strategy."""

from dataclasses import dataclass
from typing import Mapping, Protocol


Restaurant = Mapping[str, str | int | bool]


@dataclass(frozen=True)
class Turn:
    turn_id: str
    role: str
    text: str


@dataclass(frozen=True)
class Question:
    text: str
    slot: str
    reference_turn_id: str | None = None


@dataclass(frozen=True)
class Ask:
    questions: tuple[Question, ...]


@dataclass(frozen=True)
class Recommend:
    restaurant_id: str
    confidence: int | None = None


@dataclass(frozen=True)
class Usage:
    input_tokens: int | None = 0
    output_tokens: int | None = 0
    model_calls: int | None = 0


class ModelRequestError(RuntimeError):
    """A model request failed, with usage known to the adapter."""

    def __init__(self, message: str, usage: Usage) -> None:
        super().__init__(message)
        self.usage = usage


@dataclass(frozen=True)
class Decision:
    action: Ask | Recommend | None
    state_snapshot: dict | None = None
    error: str | None = None
    usage: Usage = Usage()
    raw_output: str | None = None


@dataclass(frozen=True)
class DialogueContext:
    turns: tuple[Turn, ...]
    restaurant_database: tuple[Restaurant, ...]
    remaining_budget: int
    allowed_actions: tuple[str, ...]


class Strategy(Protocol):
    system_id: str

    def decide(self, context: DialogueContext) -> Decision: ...
