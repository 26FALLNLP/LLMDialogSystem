"""Compare observable dialogue state at the dataset's annotated checkpoint."""

from collections.abc import Mapping


SLOTS = ("cuisine", "exclude_cuisine", "max_price", "location", "vegetarian", "dinner")
_DEMO_SLOTS = ("cuisine", "max_price", "location")
_HISTORY = ("unresolved", "superseded", "proposed_not_accepted")
_SECTIONS = ("active", *_HISTORY)


def _turn_number(turn: object) -> int | None:
    if type(turn) is int and turn > 0:
        return turn
    if isinstance(turn, str) and (number := turn.removeprefix("t")).isascii() and number.isdecimal():
        return int(number) or None
    return None


def _value(slot: str, value: object):
    if slot not in (*SLOTS, "meal"):
        raise ValueError(f"Unknown state slot: {slot!r}")
    if value is None:
        return None
    if slot in ("cuisine", "exclude_cuisine"):
        values = value if isinstance(value, (list, tuple)) else [value]
        if all(isinstance(item, str) and item.strip() for item in values):
            return tuple(sorted({item.strip().casefold() for item in values})) or None
    elif slot == "max_price" and type(value) is int and value >= 0:
        return value
    elif slot in ("vegetarian", "dinner") and type(value) is bool:
        return value
    elif slot in ("location", "meal") and isinstance(value, str) and value.strip():
        return value.strip().casefold()
    raise ValueError(f"Invalid state value for {slot}: {value!r}")


def _ordered(items) -> list:
    return sorted(set(items), key=repr)


def _state_view(state: Mapping) -> dict:
    """Canonicalize a complete structured snapshot, ignoring expression wording."""
    if not isinstance(state.get("active"), Mapping) or any(
        not isinstance(state.get(section), (list, tuple)) for section in _HISTORY
    ):
        raise ValueError("Expected active constraints and the three state annotation lists.")
    view = {section: {} for section in _SECTIONS}
    for slot, value in state["active"].items():
        if (normalized := _value(slot, value)) is not None:
            view["active"][slot] = normalized
    for section in _HISTORY:
        for item in state[section]:
            slot = item["slot"]
            _value(slot, None)
            turn = _turn_number(item["turn"])
            if turn is None:
                raise ValueError(f"Invalid {section} turn reference.")
            if section == "unresolved":
                interpretations = item["interpretations"]
                if not interpretations or any(slot not in option for option in interpretations):
                    raise ValueError(f"Missing interpretations for {slot}.")
                options = _ordered(
                    tuple(sorted((key, _value(key, val)) for key, val in option.items()))
                    for option in interpretations
                )
                detail = (turn, tuple(options))
            elif section == "superseded":
                detail = (turn, _value(slot, item["value"]))
            else:
                status = item["status"].strip().casefold()
                detail = (turn, _value(slot, item["value"]), status)
            view[section].setdefault(slot, []).append(detail)
        for slot, entries in view[section].items():
            view[section][slot] = _ordered(entries)
    return view


def _demo_view(snapshot: Mapping) -> dict:
    """Only candidate-set keys express this demo's predicted location options."""
    locations = snapshot["candidate_sets"]
    if not isinstance(locations, Mapping) or not locations or set(locations) - {"station", "mall"}:
        raise ValueError("Expected one or more known demo locations.")
    active = {slot: snapshot[slot] for slot in _DEMO_SLOTS if slot != "location"}
    unresolved = []
    if (reference := snapshot["unresolved_turn"]) is not None:
        if len(locations) < 2:
            raise ValueError("An unresolved demo location must have multiple interpretations.")
        unresolved.append({
            "slot": "location",
            "turn": reference,
            "interpretations": [{"location": location} for location in locations],
        })
    elif len(locations) == 1:
        active["location"] = next(iter(locations))
    else:
        raise ValueError("A resolved demo location must name one location.")
    return _state_view(dict(active=active, unresolved=unresolved, superseded=[], proposed_not_accepted=[]))


def _erroneously_active(
    view: dict, expected: dict, assessed_slots: tuple[str, ...], section: str
) -> bool | None:
    annotated = expected[section]
    observed = False
    for slot, entries in annotated.items():
        if slot not in assessed_slots:
            continue
        observed = True
        predicted = view["active"].get(slot)
        correct = expected["active"].get(slot)
        for _, old_value, *_ in entries:
            if old_value is None:
                continue
            if slot in ("cuisine", "exclude_cuisine"):
                if (set(old_value) & set(predicted or ())) - set(correct or ()):
                    return True
            elif predicted == old_value and correct != old_value:
                return True
    return False if observed and set(annotated) <= set(assessed_slots) else None


def _links(links) -> set:
    if not isinstance(links, (list, tuple)):
        raise ValueError("Expected a sequence of relation links.")
    keys = set()
    for link in links:
        source = _turn_number(link["source_turn"])
        target = _turn_number(link["target_turn"])
        if source is None or target is None:
            raise ValueError("A relation link must have valid turn references.")
        keys.add((source, target, str(link["relation"]).strip().casefold(), link["slot"]))
    return keys


def score_states(run_record: dict, gold: dict) -> dict | None:
    """Score the fixed-prefix checkpoint without consulting the hidden user goal."""
    gold_state = gold.get("gold_dialogue_state")
    if not isinstance(gold_state, Mapping) or (checkpoint := _turn_number(gold_state.get("at_turn"))) is None:
        return None
    steps = run_record.get("steps", ())
    step = next((item for item in steps if _turn_number(item.get("context_turn_id")) == checkpoint), None)
    snapshot = step.get("state_snapshot") if step is not None else None
    if not isinstance(snapshot, Mapping):
        return None
    expected = _state_view(gold_state)
    is_demo = run_record.get("system_id") == "demo-shared-candidate" and "active" not in snapshot
    try:
        predicted = _demo_view(snapshot) if is_demo else _state_view(snapshot)
    except (ValueError, KeyError, TypeError, AttributeError):
        return None

    slots = _DEMO_SLOTS if is_demo else SLOTS
    if not is_demo and any("meal" in section for state in (expected, predicted) for section in state.values()):
        slots = (*slots, "meal")
    sections = ("active", "unresolved") if is_demo else _SECTIONS
    fields = {}
    for slot in slots:
        expected_values = {section: expected[section].get(slot) for section in sections}
        predicted_values = {section: predicted[section].get(slot) for section in sections}
        fields[slot] = {
            "correct": expected_values == predicted_values,
            "expected": expected_values,
            "predicted": predicted_values,
        }

    relations = None
    if "relation_links" in snapshot and "gold_relation_links" in gold:
        try:
            actual_links = _links(snapshot["relation_links"])
            expected_links = _links(gold["gold_relation_links"])
        except (ValueError, KeyError, TypeError, AttributeError):
            pass
        else:
            relations = {
                "matched": len(actual_links & expected_links),
                "predicted": len(actual_links),
                "annotated": len(expected_links),
                "exact_match": actual_links == expected_links,
            }

    return {
        "step_id": step.get("step_id"),
        "context_turn_id": step["context_turn_id"],
        "snapshot_format": "demo_partial" if is_demo else "structured",
        "unannotated_steps": sum(_turn_number(item.get("context_turn_id")) != checkpoint for item in steps),
        "field_correct": sum(field["correct"] for field in fields.values()),
        "field_total": len(fields),
        "exact_match": None if is_demo else all(field["correct"] for field in fields.values()),
        "stale_requirement_error": _erroneously_active(predicted, expected, slots, "superseded"),
        "unaccepted_suggestion_error": _erroneously_active(predicted, expected, slots, "proposed_not_accepted"),
        "relation_metrics": relations,
        "fields": fields,
    }
