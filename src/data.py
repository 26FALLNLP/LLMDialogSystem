"""Load the restaurant catalog and scenario inputs from the NLP data snapshot."""

import hashlib
import json
import re
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType

from .answer_service import AnswerService
from .dialogue_types import Restaurant, Turn

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CATALOG_NAME = "restaurants.json"
RESTAURANT_FIELDS = {
    "restaurant_id": str,
    "name": str,
    "cuisine": str,
    "price_per_person": int,
    "near_station": bool,
    "near_mall": bool,
    "vegetarian_options": bool,
    "open_for_dinner": bool,
}


def scenario_path(scenario_id: str, data_dir: Path = DATA_DIR) -> Path:
    """Where a scenario file lives: <data_dir>/scenarios/<id>.json, or else exactly
    one match in <data_dir>/drafts/*/scenarios/ (drafts load only when asked for by ID)."""
    data_dir = Path(data_dir)
    main = data_dir / "scenarios" / f"{scenario_id}.json"
    if main.exists():
        return main
    drafts = sorted(data_dir.glob(f"drafts/*/scenarios/{scenario_id}.json"))
    if len(drafts) > 1:
        raise ValueError(f"Scenario ID {scenario_id!r} appears in more than one drafts folder")
    return drafts[0] if drafts else main


@dataclass(frozen=True, slots=True)
class Scenario:
    scenario_id: str
    turns: tuple[Turn, ...]
    restaurants: tuple[Restaurant, ...]
    data_version: str
    database_version: str


@dataclass(frozen=True, slots=True)
class Dataset:
    scenarios: dict[str, Scenario]
    answer_service: AnswerService
    data_version: str
    database_version: str


def load_dataset(scenario_ids: Sequence[str], data_dir: Path = DATA_DIR) -> Dataset:
    """Read selected scenarios and expose only the two views needed by the runner."""
    if not scenario_ids or len(set(scenario_ids)) != len(scenario_ids):
        raise ValueError("Provide one or more distinct scenario IDs")
    data_dir = Path(data_dir)
    db_path = data_dir / CATALOG_NAME
    db_bytes = db_path.read_bytes()
    restaurants = _load_restaurants(db_bytes, db_path)
    database_version = f"sha256:{hashlib.sha256(db_bytes).hexdigest()}"

    turns_by_id = {}
    answers_by_id = {}
    data_hash = hashlib.sha256()
    for scenario_id in sorted(scenario_ids):
        if not re.fullmatch(r"[A-Za-z0-9_-]+", scenario_id):
            raise ValueError(f"Invalid scenario ID: {scenario_id!r}")
        path = scenario_path(scenario_id, data_dir)
        raw = path.read_bytes()
        data_hash.update(raw)
        data_hash.update(b"\0")
        record = json.loads(raw)
        if not isinstance(record, dict) or record.get("scenario_id") != scenario_id:
            raise ValueError(f"{path}: expected scenario_id={scenario_id!r}")
        visible = record.get("model_visible")
        if not isinstance(visible, dict) or visible.get("restaurant_database") != CATALOG_NAME:
            raise ValueError(f"{path}: expected model_visible to reference {CATALOG_NAME}")
        turns_by_id[scenario_id] = _load_turns(visible.get("dialogue_prefix"), path)

        evaluation = record.get("evaluation_only")
        answers_by_id[scenario_id] = (
            evaluation.get("predefined_clarification_answers")
            if isinstance(evaluation, dict)
            else None
        )

    data_version = f"sha256:{data_hash.hexdigest()}"
    return Dataset(
        scenarios={
            scenario_id: Scenario(
                scenario_id=scenario_id,
                turns=turns_by_id[scenario_id],
                restaurants=restaurants,
                data_version=data_version,
                database_version=database_version,
            )
            for scenario_id in scenario_ids
        },
        answer_service=AnswerService(answers_by_id),
        data_version=data_version,
        database_version=database_version,
    )


def _load_restaurants(raw: bytes, path: Path) -> tuple[Restaurant, ...]:
    rows = json.loads(raw)
    if not isinstance(rows, list) or not rows:
        raise ValueError(f"{path}: expected a nonempty restaurant list")
    ids = set()
    restaurants = []
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, dict) or set(row) != RESTAURANT_FIELDS.keys() or any(
            type(row[field]) is not kind for field, kind in RESTAURANT_FIELDS.items()
        ):
            raise ValueError(f"{path}: restaurant row {index} has invalid fields or types")
        restaurant_id = row["restaurant_id"]
        if not restaurant_id.strip() or restaurant_id in ids:
            raise ValueError(
                f"{path}: restaurant row {index} has a blank or duplicate restaurant ID"
            )
        ids.add(restaurant_id)
        restaurants.append(MappingProxyType(row))
    return tuple(restaurants)


def _load_turns(rows: object, path: Path) -> tuple[Turn, ...]:
    if not isinstance(rows, list) or not rows:
        raise ValueError(f"{path}: expected a nonempty dialogue_prefix")
    turns = []
    for number, row in enumerate(rows, start=1):
        if (
            not isinstance(row, dict)
            or type(row.get("turn")) is not int
            or row["turn"] != number
            or row.get("speaker") not in ("user", "assistant")
            or not isinstance(row.get("text"), str)
            or not row["text"].strip()
        ):
            raise ValueError(f"{path}: invalid dialogue turn {number}")
        turns.append(Turn(turn_id=f"t{number:02d}", role=row["speaker"], text=row["text"]))
    if turns[-1].role != "user":
        raise ValueError(f"{path}: the dialogue prefix must end with a user turn")
    return tuple(turns)
