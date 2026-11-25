"""Ordinary code shared by the memory systems (S3, S4, S5).

Nothing here calls a model. It turns extracted propositions into a dialogue
state, filters the public restaurant catalog under every possible meaning, and
applies the ask rule. It only uses what a system is allowed to see (the
conversation, the catalog, the remaining budget); no gold data.
"""

from collections.abc import Mapping, Sequence
from itertools import product

from ..dialogue_types import Ask, Question, Recommend, Usage

SLOTS = ("cuisine", "exclude_cuisine", "max_price", "location", "vegetarian", "dinner")
STATUSES = ("proposed", "acknowledged", "unresolved", "superseded")
RELATIONS = ("revise", "confirm", "clarify")
LOCATIONS = {"station": "station", "train station": "station", "the station": "station",
             "mall": "mall", "the mall": "mall", "shopping mall": "mall"}


# ----------------------------------------------------------------- small helpers
def turn_number(turn) -> int | None:
    if isinstance(turn, int) and turn > 0:
        return turn
    if isinstance(turn, str):
        digits = turn.strip().lower().removeprefix("t")
        if digits.isdigit() and int(digits) > 0:
            return int(digits)
    return None


def add_usage(total: Usage, more: Usage) -> Usage:
    def plus(a, b):
        return None if a is None or b is None else a + b
    return Usage(plus(total.input_tokens, more.input_tokens), plus(total.output_tokens, more.output_tokens),
                 plus(total.model_calls, more.model_calls))


def normalize_value(slot: str, value, cuisines: set[str]):
    """Map a model-written value onto the catalog's vocabulary; None if unusable."""
    if value is None:
        return None
    if slot in ("cuisine", "exclude_cuisine"):
        values = value if isinstance(value, list) else [value]
        lookup = {c.casefold(): c for c in cuisines}
        out = sorted({lookup[v.strip().casefold()] for v in values
                      if isinstance(v, str) and v.strip().casefold() in lookup})
        if not out:
            return None
        return out if (slot == "exclude_cuisine" or len(out) > 1) else out[0]
    if slot == "max_price":
        if isinstance(value, bool):
            return None
        if isinstance(value, (int, float)):
            return int(value)
        if isinstance(value, str):
            digits = "".join(ch for ch in value if ch.isdigit())
            return int(digits) if digits else None
        return None
    if slot == "location":
        return LOCATIONS.get(value.strip().casefold()) if isinstance(value, str) else None
    if slot in ("vegetarian", "dinner"):
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return {"true": True, "yes": True, "false": False, "no": False}.get(value.strip().casefold())
    return None


# ----------------------------------------------------------------- state building
def build_state(propositions: Sequence[Mapping], links: Sequence[Mapping] | None,
                catalog: Sequence[Mapping]) -> dict:
    """Apply revisions and confirmations, then collect the active constraints,
    unresolved readings, superseded values and unaccepted proposals.

    links=None means a system without relation links (S4): only the
    propositions' own statuses are used. With links (S3/S5) the code also
    applies every revise/confirm/clarify link on top of the statuses.
    """
    cuisines = {r["cuisine"] for r in catalog}
    props = []
    for p in propositions:
        slot = p.get("slot")
        if slot not in SLOTS:
            continue
        props.append({
            "slot": slot,
            "value": normalize_value(slot, p.get("value"), cuisines),
            "options": [normalize_value(slot, o, cuisines) for o in (p.get("options") or [])],
            "speaker": p.get("speaker"),
            "turn": turn_number(p.get("source_turn")),
            "status": p.get("status") if p.get("status") in STATUSES else "acknowledged",
            "confirmed": False,
        })
    clean_links = []
    for link in links or []:
        source, target = turn_number(link.get("source_turn")), turn_number(link.get("target_turn"))
        if source and target and link.get("relation") in RELATIONS and link.get("slot") in SLOTS:
            clean_links.append({"source_turn": source, "target_turn": target,
                                "relation": link["relation"], "slot": link["slot"]})
            for p in props:
                if p["slot"] != link["slot"]:
                    continue
                if link["relation"] == "revise" and p["turn"] == target:
                    p["status"] = "superseded"
                elif link["relation"] == "confirm" and p["turn"] == target and p["speaker"] == "assistant":
                    p["status"], p["confirmed"] = "acknowledged", True
                elif link["relation"] == "clarify" and p["turn"] == target and p["status"] == "unresolved":
                    p["status"] = "superseded"
    # An assistant proposal counts only if the user confirmed it.
    for p in props:
        if p["speaker"] == "assistant" and p["status"] == "acknowledged" and links is not None and not p["confirmed"]:
            p["status"] = "proposed"

    active, unresolved, superseded, proposed = {}, [], [], []
    for p in sorted(props, key=lambda p: (p["turn"] or 0)):
        if p["status"] == "acknowledged" and p["value"] is not None:
            if p["slot"] in ("vegetarian", "dinner") and p["value"] is False:
                active.pop(p["slot"], None)
                continue
            if p["slot"] in active and active[p["slot"]] != p["value"]:
                superseded.append({"slot": p["slot"], "turn": p["turn"] or 1, "value": active[p["slot"]]})
            active[p["slot"]] = p["value"]
        elif p["status"] == "superseded" and p["value"] is not None:
            superseded.append({"slot": p["slot"], "turn": p["turn"] or 1, "value": p["value"]})
        elif p["status"] == "proposed" and p["value"] is not None:
            proposed.append({"slot": p["slot"], "turn": p["turn"] or 1, "value": p["value"], "status": "not accepted"})
        elif p["status"] == "unresolved":
            options = [o for o in dict.fromkeys(json_key(o) for o in p["options"] if o is not None)]
            if len(options) >= 2:
                unresolved.append({"slot": p["slot"], "turn": p["turn"] or 1,
                                   "interpretations": [{p["slot"]: from_key(o)} for o in options]})
    unresolved_slots = {u["slot"] for u in unresolved}
    for slot in unresolved_slots:
        active.pop(slot, None)
    proposed = [p for p in proposed if active.get(p["slot"]) != p["value"]]
    return {"active": active, "unresolved": unresolved, "superseded": superseded,
            "proposed_not_accepted": proposed, **({"relation_links": clean_links} if links is not None else {})}


def json_key(value):
    return tuple(value) if isinstance(value, list) else value


def from_key(value):
    return list(value) if isinstance(value, tuple) else value


# ----------------------------------------------------------------- catalog filtering and the rule
def matches(restaurant: Mapping, goal: Mapping) -> bool:
    cuisine = goal.get("cuisine")
    if cuisine is not None and restaurant["cuisine"] not in (cuisine if isinstance(cuisine, list) else [cuisine]):
        return False
    if restaurant["cuisine"] in (goal.get("exclude_cuisine") or []):
        return False
    if goal.get("max_price") is not None and restaurant["price_per_person"] > goal["max_price"]:
        return False
    if goal.get("location") in ("station", "mall") and not restaurant[f"near_{goal['location']}"]:
        return False
    if goal.get("vegetarian") and not restaurant["vegetarian_options"]:
        return False
    if goal.get("dinner") and not restaurant["open_for_dinner"]:
        return False
    return True


def readings(state: Mapping) -> list[dict]:
    """Every combination of the unresolved items' interpretations."""
    out = []
    for choice in product(*[u["interpretations"] for u in state["unresolved"]]):
        goal = dict(state["active"])
        for interpretation in choice:
            goal.update(interpretation)
        out.append(goal)
    return out


def candidate_sets(state: Mapping, catalog: Sequence[Mapping]) -> list[list[str]]:
    return [[r["restaurant_id"] for r in catalog if matches(r, goal)] for goal in readings(state)]


def _cheapest(ids, catalog):
    price = {r["restaurant_id"]: r["price_per_person"] for r in catalog}
    return min(ids, key=lambda i: (price[i], i))


def question_for(item: Mapping) -> Question:
    slot = item["slot"]
    options = [next(iter(i.values())) for i in item["interpretations"]]
    if slot == "location":
        text = "Do you mean near the " + " or near the ".join(str(o) for o in options) + "?"
    elif slot in ("cuisine", "exclude_cuisine"):
        text = "Which cuisine do you mean: " + ", ".join(str(o) for o in options) + "?"
    elif slot == "max_price":
        text = "What budget per person do you mean: " + " or ".join(f"${o}" for o in options) + "?"
    elif slot == "vegetarian":
        text = "Do you need vegetarian options?"
    else:
        text = "Is this for dinner?"
    return Question(text, slot, f"t{item['turn']:02d}")


def apply_rule(state: Mapping, catalog: Sequence[Mapping], remaining_budget: int) -> tuple[Ask | Recommend, dict]:
    """If one restaurant fits every meaning, recommend it; otherwise ask one
    targeted question if budget remains; otherwise make the best guess."""
    sets = candidate_sets(state, catalog)
    shared = set.intersection(*map(set, sets)) if sets else set()
    trace = {"candidate_sets": sets, "shared_candidates": sorted(shared)}
    if shared:
        return Recommend(_cheapest(shared, catalog)), {**trace, "rule": "shared_candidate"}
    if remaining_budget > 0 and state["unresolved"]:
        # One targeted question about the earliest unresolved item (deterministic).
        item = min(state["unresolved"], key=lambda u: (u["turn"], u["slot"]))
        return Ask((question_for(item),)), {**trace, "rule": "ask_targeted", "asked_slot": item["slot"]}
    counts = {}
    for s in sets:
        for rid in s:
            counts[rid] = counts.get(rid, 0) + 1
    if counts:
        best = max(counts.values())
        return Recommend(_cheapest([r for r, c in counts.items() if c == best], catalog)), {**trace, "rule": "best_guess"}
    # No restaurant fits any reading (e.g. an extraction mistake): fewest broken constraints.
    def broken(r):
        return sum(not matches(r, {k: v}) for k, v in state["active"].items())
    fallback = min(catalog, key=lambda r: (broken(r), r["price_per_person"], r["restaurant_id"]))
    return Recommend(fallback["restaurant_id"]), {**trace, "rule": "fallback_fewest_violations"}
