"""
validate.py - checks scenario forms against the restaurant database.

Usage:
    python validate.py --db restaurants.json --scenarios scenarios/ [--log quality_log.csv]

Checks (per scenario):
  - 6-10 turns, last turn is the user's, every turn has a planned act
  - hidden goal uses only schema fields; success set is non-empty
  - hidden goal == gold active state (+ the correct interpretation, if unresolved)
  - for unresolved references: every interpretation is satisfiable, and
    should_ask == (no restaurant satisfies all interpretations)   <- the team's rule
  - no leakage: user turns at/after the ambiguous turn don't reveal the answer
  - no unverifiable requests (ambiance, reviews, ...) in user turns
  - relation links point at real turns and use only revise/confirm/clarify
Per contrastive pair:
  - both variants exist, same length, differ in exactly one turn
"""
import argparse, csv, glob, json, os, re, sys
from collections import defaultdict

SLOTS = {"cuisine", "exclude_cuisine", "max_price", "location", "vegetarian", "dinner"}
TYPES = {"clear", "ambiguous_reference", "revision", "suggestion_acceptance"}
RELATIONS = {"revise", "confirm", "clarify"}
UNVERIFIABLE = ["romantic", "ambiance", "ambience", "review", "rating", "stars", "outdoor",
                "parking", "cozy", "quiet", "view", "trendy", "authentic", "late", "quick",
                "fast", "reservation", "delivery", "kid", "dog", "wifi"]


def matches(r, c):
    cu = c.get("cuisine")
    if cu is not None:
        allowed = cu if isinstance(cu, list) else [cu]
        if r["cuisine"] not in allowed:
            return False
    if r["cuisine"] in (c.get("exclude_cuisine") or []):
        return False
    if c.get("max_price") is not None and r["price_per_person"] > c["max_price"]:
        return False
    loc = c.get("location")
    if loc == "station" and not r["near_station"]:
        return False
    if loc == "mall" and not r["near_mall"]:
        return False
    if c.get("vegetarian") and not r["vegetarian_options"]:
        return False
    if c.get("dinner") and not r["open_for_dinner"]:
        return False
    return True


def candidates(db, c):
    return sorted(r["restaurant_id"] for r in db if matches(r, c))


def norm(c):
    """Drop None values so {'location': None} == {}."""
    return {k: v for k, v in c.items() if v is not None and v != []}


def analyse(sc, db):
    """Return (computed gold dict, list of (level, check, message))."""
    issues = []
    ev = sc["evaluation_only"]
    turns = sc["model_visible"]["dialogue_prefix"]
    hidden = ev["hidden_user_goal"]
    state = ev["gold_dialogue_state"]

    def bad(check, msg, level="FAIL"):
        issues.append((level, check, msg))

    # structure
    if not 6 <= len(turns) <= 10:
        bad("length", f"{len(turns)} turns (need 6-10)")
    if turns and turns[-1]["speaker"] != "user":
        bad("ends_on_user", "last turn must be the user's so the assistant acts next")
    for i, t in enumerate(turns, 1):
        if t["turn"] != i:
            bad("turn_numbers", f"turn {t['turn']} at position {i}")
        if t["speaker"] not in ("user", "assistant"):
            bad("speaker", f"turn {i}: bad speaker {t['speaker']}")
    for p in ev.get("turn_plan", []):
        if not p.get("act"):
            bad("plan", f"turn {p.get('turn')} has no planned act")
    if ev["scenario_type"] not in TYPES:
        bad("type", ev["scenario_type"])

    # schema
    for name, c in [("hidden_user_goal", hidden), ("active", state["active"])]:
        extra = set(c) - SLOTS
        if extra:
            bad("schema", f"{name} has non-schema fields {extra}")
    cuisines = {r["cuisine"] for r in db}
    for c in [hidden, state["active"]]:
        cu = c.get("cuisine")
        for x in (cu if isinstance(cu, list) else [cu] if cu else []):
            if x not in cuisines:
                bad("schema", f"cuisine {x} not in database")

    success = candidates(db, hidden)
    if not success:
        bad("success_set", "no restaurant satisfies the hidden goal")

    unresolved = state.get("unresolved", [])
    should_ask = ev["gold_decision"]["should_ask"]
    computed = {"success_set": success}

    if unresolved:
        u = unresolved[0]
        if len(unresolved) > 1:
            bad("one_tricky_thing", "more than one unresolved item", "WARN")
        sets = []
        for interp in u["interpretations"]:
            s = candidates(db, {**state["active"], **interp})
            sets.append({"interpretation": interp, "candidates": s})
            if not s:
                bad("interpretation", f"interpretation {interp} has no valid restaurant")
        shared = sorted(set.intersection(*[set(x["candidates"]) for x in sets])) if sets else []
        computed.update(interpretation_sets=sets, shared_candidates=shared,
                        valid_without_clarification=shared)
        rule_says_ask = len(shared) == 0
        if rule_says_ask != should_ask:
            bad("ask_rule", f"form says should_ask={should_ask} but rule gives {rule_says_ask} "
                            f"(shared={shared})")
        if not any(norm({**state["active"], **i}) == norm(hidden) for i in u["interpretations"]):
            bad("hidden_vs_state", "hidden goal is not active state + any listed interpretation")
        if should_ask:
            cat = ev["gold_decision"].get("necessary_question")
            if not cat:
                bad("answers", "should_ask but no necessary_question category")
            elif u["slot"] not in ev["predefined_clarification_answers"]:
                bad("answers", f"no scripted answer for slot {u['slot']}")
        # leakage
        key = hidden.get(u["slot"])
        words = []
        if u["slot"] == "location" and key:
            words = [key]
        elif u["slot"] == "cuisine" and isinstance(key, str):
            words = [key.lower()]
        elif u["slot"] == "max_price" and key:
            words = [f"${key}"]
        for t in turns:
            if t["speaker"] == "user" and t["turn"] >= u["turn"]:
                for w in words:
                    if w.lower() in t["text"].lower():
                        bad("leakage", f"turn {t['turn']} reveals '{w}' before clarification")
    else:
        computed["valid_without_clarification"] = success
        if should_ask:
            bad("ask_rule", "should_ask=True but nothing is unresolved")
        if norm(hidden) != norm(state["active"]):
            bad("hidden_vs_state", f"hidden {norm(hidden)} != active {norm(state['active'])}")

    # unverifiable requests
    for t in turns:
        if t["speaker"] == "user":
            for w in UNVERIFIABLE:
                if re.search(rf"\b{w}", t["text"].lower()):
                    bad("unverifiable", f"turn {t['turn']} mentions '{w}'", "WARN")

    # unaccepted suggestions must not be active
    for p in state.get("proposed_not_accepted", []):
        if state["active"].get(p["slot"]) == p["value"]:
            bad("suggestion", f"unaccepted proposal {p} is marked active")

    # relations
    n = len(turns)
    for rel in ev.get("gold_relation_links", []):
        if rel["relation"] not in RELATIONS:
            bad("relation", f"unknown relation {rel['relation']}")
        for k in ("source_turn", "target_turn"):
            if not 1 <= rel[k] <= n:
                bad("relation", f"{k}={rel[k]} out of range")
    return computed, issues


def pair_checks(scs):
    issues = defaultdict(list)
    fam = defaultdict(list)
    for sc in scs:
        fam[sc["evaluation_only"]["template_family_id"]].append(sc)
    for f, members in fam.items():
        variants = sorted(m["evaluation_only"]["variant"] for m in members)
        if variants == ["single"]:
            continue
        if variants != ["A", "B"]:
            issues[f].append(("FAIL", "pair", f"family {f} has variants {variants}"))
            continue
        a, b = sorted(members, key=lambda m: m["evaluation_only"]["variant"])
        ta, tb = a["model_visible"]["dialogue_prefix"], b["model_visible"]["dialogue_prefix"]
        if len(ta) != len(tb):
            issues[f].append(("FAIL", "pair", "variants have different lengths"))
            continue
        diff = [x["turn"] for x, y in zip(ta, tb) if x["text"] != y["text"]]
        if len(diff) != 1:
            issues[f].append(("WARN", "pair", f"variants differ in turns {diff} (want exactly 1)"))
    return issues


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="restaurants.json")
    ap.add_argument("--scenarios", default="scenarios")
    ap.add_argument("--log", default="quality_log.csv")
    ap.add_argument("--write-computed", action="store_true",
                    help="write computed candidate sets back into each file")
    args = ap.parse_args()

    db = json.load(open(args.db))
    paths = sorted(glob.glob(os.path.join(args.scenarios, "*.json")))
    scs = [json.load(open(p)) for p in paths]
    pair_issues = pair_checks(scs)

    rows, n_fail = [], 0
    for p, sc in zip(paths, scs):
        sid = sc["scenario_id"]
        computed, issues = analyse(sc, db)
        issues += pair_issues.get(sc["evaluation_only"]["template_family_id"], [])
        if args.write_computed:
            sc["evaluation_only"]["computed_by_validator"] = computed
            json.dump(sc, open(p, "w"), indent=2)
        if not issues:
            rows.append([sid, "all", "PASS", ""])
        for lvl, chk, msg in issues:
            rows.append([sid, chk, lvl, msg])
            n_fail += lvl == "FAIL"
    with open(args.log, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["scenario_id", "check", "status", "message"])
        w.writerows(rows)
    n_warn = sum(r[2] == "WARN" for r in rows)
    print(f"{len(scs)} scenarios | {n_fail} FAIL | {n_warn} WARN | log -> {args.log}")
    for r in rows:
        if r[2] != "PASS":
            print("  ", *r)
    sys.exit(1 if n_fail else 0)


if __name__ == "__main__":
    main()
