"""
validate.py - checks scenario forms against the restaurant database.

Usage (from the repo root):
    python data/validate.py --scenarios data/scenarios --manifest data/dataset-manifest.json
    python data/validate.py --scenarios data/drafts/bhavishya/scenarios \
        --manifest data/drafts/bhavishya/dataset-manifest.json
    python data/validate.py --scenarios data/scenarios data/drafts/bhavishya/scenarios   # combined

--scenarios takes one or more folders, searched recursively. JSON files that
are not scenarios are skipped. --db defaults to data/restaurants.json.

Checks (per scenario):
  - 6-10 turns, last turn is the user's, every turn has a planned act
  - hidden goal uses only schema fields; success set is non-empty
  - hidden goal == gold active state (+ the correct interpretation, if unresolved)
  - for unresolved references: every interpretation (or combination of
    interpretations, when two things are unclear) is satisfiable, and
    should_ask == (no restaurant satisfies all interpretations)   <- the team's rule
  - questions_needed: the smallest number of clarification questions after
    which a safe recommendation exists (checked against the form, if given)
  - no leakage: user turns at/after the ambiguous turn don't reveal the answer
  - no unverifiable requests (ambiance, reviews, ...) in user turns
  - relation links point at real turns and use only revise/confirm/clarify
  - suggestion traps: treating the unaccepted suggestion as accepted must
    lead to a wrong restaurant (only checked when suggestion_trap is true)
  - two-question forms may leave necessary_question null and list
    necessary_questions instead (main's nlp-quota-v3 format)
  - computed_by_validator, if stored, matches what the database gives
Per ambiguity group (main's format: variants of a family that share one chat):
  - every variant has the same gold_dialogue_state
  - hidden targets have disjoint restaurant sets
  - each unresolved slot's hidden values are balanced (each value equally often)
  - with --manifest: every scenario is in exactly one manifest group, each
    group's members share one chat, and required_slots match the unresolved slots
Across the dataset (hint detector, WARN only; see hint_report):
  - hidden answer is the last-mentioned option too often
  - the same option is the hidden answer too often
  - the hidden option is the only one with a "better" restaurant
"""
import argparse, csv, glob, json, os, re, sys
from collections import Counter, defaultdict
from itertools import combinations, product

SLOTS = {"cuisine", "exclude_cuisine", "max_price", "location", "vegetarian", "dinner"}
TYPES = {"clear", "ambiguous_reference", "revision", "suggestion_acceptance"}
RELATIONS = {"revise", "confirm", "clarify"}
UNVERIFIABLE = ["romantic", "ambiance", "ambience", "review", "rating", "stars", "outdoor",
                "parking", "cozy", "quiet", "view", "trendy", "authentic", "late", "quick",
                "fast", "reservation", "delivery", "kid", "dog", "wifi"]
# Hint detector: warn when a rate is above this share (or the mirror below 1 - it).
BALANCE_THRESHOLD = 0.65
MIN_FOR_BALANCE = 4          # don't judge balance on fewer should-ask items than this
DOMINANCE_RATE_LIMIT = 0.25  # warn if the hidden option is "better" in more than this share
LOCATION_WORDS = {"station": "station", "mall": "mall"}


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


# ------------------------------------------------------------ unresolved items
def combos(unresolved):
    """Every combination of interpretations, merged into one constraint dict."""
    out = []
    for choice in product(*[u["interpretations"] for u in unresolved]):
        merged = {}
        for interp in choice:
            merged.update(interp)
        out.append((choice, merged))
    return out


def shared_for(db, active, unresolved, fixed=None):
    """Restaurants valid under every remaining combination (fixed = items already answered)."""
    fixed = fixed or {}
    sets = []
    for choice, merged in combos(unresolved):
        if any(choice[i] != v for i, v in fixed.items()):
            continue
        sets.append(set(candidates(db, {**active, **merged})))
    return set.intersection(*sets) if sets else set()


def questions_needed(db, active, unresolved):
    """Fewest unresolved items to ask about so that, whatever the answers,
    a restaurant valid under all remaining readings exists."""
    n = len(unresolved)
    for k in range(n + 1):
        for asked in combinations(range(n), k):
            answers = product(*[unresolved[i]["interpretations"] for i in asked])
            if all(shared_for(db, active, unresolved, dict(zip(asked, a))) for a in answers):
                return k
    return n


# ------------------------------------------------------------ dominance (hint iii)
def _profile(r):
    return (-r["price_per_person"], int(r["near_station"] and r["near_mall"]),
            int(r["vegetarian_options"]), int(r["open_for_dinner"]))


CLEAR_PRICE_GAP = 5  # a price-only advantage counts as "clearly better" above this many dollars


def dominates(r, s):
    """r is clearly better than s: no more expensive, at least as good on
    near-both / vegetarian / open-for-dinner, and either better on one of those
    features or more than CLEAR_PRICE_GAP dollars cheaper. (With 40 restaurants
    almost every pair differs by a few dollars, so a small price gap alone is
    not treated as a giveaway; the dataset-level 'cheapest' balance covers it.)"""
    a, b = _profile(r), _profile(s)
    if not all(x >= y for x, y in zip(a, b)) or a == b:
        return False
    return any(x > y for x, y in zip(a[1:], b[1:])) or s["price_per_person"] - r["price_per_person"] > CLEAR_PRICE_GAP


def set_dominates(xs, ys):
    """Some restaurant in xs is clearly better than every restaurant in ys."""
    return bool(xs) and bool(ys) and any(all(dominates(r, s) for s in ys) for r in xs)


# ------------------------------------------------------------ per scenario
def analyse(sc, db):
    """Return (computed gold dict, list of (level, check, message))."""
    issues = []
    ev = sc["evaluation_only"]
    turns = sc["model_visible"]["dialogue_prefix"]
    hidden = ev["hidden_user_goal"]
    state = ev["gold_dialogue_state"]
    decision = ev["gold_decision"]

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
    should_ask = decision["should_ask"]
    computed = {"success_set": success}
    active = state["active"]

    if unresolved:
        listed = decision.get("necessary_questions") or []
        two_question_form = decision.get("questions_needed", 1) >= 2 or len(listed) >= 2
        if len(unresolved) > 1 and not two_question_form:
            bad("one_tricky_thing", "more than one unresolved item", "WARN")
        sets = []
        for choice, merged in combos(unresolved):
            s = candidates(db, {**active, **merged})
            sets.append({"interpretation": merged, "candidates": s})
            if not s:
                bad("interpretation", f"interpretation {merged} has no valid restaurant")
        shared = sorted(set.intersection(*[set(x["candidates"]) for x in sets])) if sets else []
        qn = questions_needed(db, active, unresolved)
        computed.update(interpretation_sets=sets, shared_candidates=shared,
                        valid_without_clarification=shared, questions_needed=qn)
        rule_says_ask = len(shared) == 0
        if rule_says_ask != should_ask:
            bad("ask_rule", f"form says should_ask={should_ask} but rule gives {rule_says_ask} "
                            f"(shared={shared})")
        if "questions_needed" in decision and decision["questions_needed"] != qn:
            bad("questions_needed", f"form says {decision['questions_needed']} but database gives {qn}")
        if not any(norm({**active, **m}) == norm(hidden) for _, m in combos(unresolved)):
            bad("hidden_vs_state", "hidden goal is not active state + any listed interpretation")
        if should_ask:
            cat = decision.get("necessary_question") or listed
            if not cat:
                bad("answers", "should_ask but no necessary_question / necessary_questions")
            for u in unresolved:
                if u["slot"] not in ev["predefined_clarification_answers"]:
                    bad("answers", f"no scripted answer for slot {u['slot']}")
            slots = {u["slot"] for u in unresolved}
            for q in decision.get("necessary_questions", []):
                if q.partition("@")[0] not in slots:
                    bad("answers", f"necessary question {q} is not about an unresolved slot")
        # leakage
        for u in unresolved:
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
        computed["questions_needed"] = 0
        if should_ask:
            bad("ask_rule", "should_ask=True but nothing is unresolved")
        if norm(hidden) != norm(active):
            bad("hidden_vs_state", f"hidden {norm(hidden)} != active {norm(active)}")

    # unverifiable requests
    for t in turns:
        if t["speaker"] == "user":
            for w in UNVERIFIABLE:
                if re.search(rf"\b{w}", t["text"].lower()):
                    bad("unverifiable", f"turn {t['turn']} mentions '{w}'", "WARN")

    # unaccepted suggestions must not be active
    for p in state.get("proposed_not_accepted", []):
        if active.get(p["slot"]) == p["value"]:
            bad("suggestion", f"unaccepted proposal {p} is marked active")
        if ev.get("suggestion_trap") or (ev.get("draft_info") or {}).get("suggestion_trap"):
            wrong = set(candidates(db, {**active, p["slot"]: p["value"]}))
            if not wrong:
                bad("suggestion_trap", f"suggested {p['slot']}={p['value']} has no restaurants, so the trap cannot catch anything")
            overlap = wrong & set(success)
            if overlap:
                bad("suggestion_trap", f"accepting the suggestion still allows correct restaurants {sorted(overlap)}")

    # relations
    n = len(turns)
    for rel in ev.get("gold_relation_links", []):
        if rel["relation"] not in RELATIONS:
            bad("relation", f"unknown relation {rel['relation']}")
        for k in ("source_turn", "target_turn"):
            if not 1 <= rel[k] <= n:
                bad("relation", f"{k}={rel[k]} out of range")

    # stored candidate sets must match the database
    stored = ev.get("computed_by_validator")
    if stored:
        for key in ("success_set", "shared_candidates", "valid_without_clarification"):
            if key in stored and key in computed and sorted(stored[key]) != sorted(computed[key]):
                bad("computed", f"stored {key} {stored[key]} != database {computed[key]}")
        if "interpretation_sets" in stored and "interpretation_sets" in computed:
            got = [(x["interpretation"], sorted(x["candidates"])) for x in computed["interpretation_sets"]]
            want = [(x["interpretation"], sorted(x["candidates"])) for x in stored["interpretation_sets"]]
            if got != want:
                bad("computed", "stored interpretation_sets do not match the database")
    return computed, issues


# ------------------------------------------------------------ ambiguity groups
def infer_groups(scs):
    """Main's format: within a template family, variants with an identical
    model_visible chat form one ambiguity group. Returns {group_key: [scenarios]}."""
    groups = defaultdict(list)
    for sc in scs:
        key = (sc["evaluation_only"]["template_family_id"],
               json.dumps(sc["model_visible"], sort_keys=True))
        groups[key].append(sc)
    return {f"{k[0]}#{i}": v for i, (k, v) in enumerate(sorted(groups.items(), key=lambda kv: kv[0]))}


def group_checks(scs, db, manifest=None):
    """Per-group checks. Returns {scenario_id: [issues]} and dataset-level issues."""
    issues, dataset = defaultdict(list), []
    by_id = {sc["scenario_id"]: sc for sc in scs}
    if manifest is not None:
        groups = {}
        listed = []
        for g in manifest.get("groups", []):
            missing = [s for s in g["scenario_ids"] if s not in by_id]
            if missing:
                dataset.append(("FAIL", "manifest", f"group {g['group_id']} lists unknown scenarios {missing}"))
            groups[g["group_id"]] = [by_id[s] for s in g["scenario_ids"] if s in by_id]
            listed += g["scenario_ids"]
            members = groups[g["group_id"]]
            if len({json.dumps(m["model_visible"], sort_keys=True) for m in members}) > 1:
                for m in members:
                    issues[m["scenario_id"]].append(("FAIL", "group", f"group {g['group_id']} members have different chats"))
            unresolved_slots = sorted({u["slot"] for m in members
                                       for u in m["evaluation_only"]["gold_dialogue_state"]["unresolved"]})
            should_ask = any(m["evaluation_only"]["gold_decision"]["should_ask"] for m in members)
            want_slots = unresolved_slots if should_ask else []
            if sorted(g.get("required_slots", [])) != want_slots:
                dataset.append(("FAIL", "manifest", f"group {g['group_id']} required_slots {g.get('required_slots')} "
                                                     f"!= unresolved slots {want_slots}"))
        dupes = [s for s, c in Counter(listed).items() if c > 1]
        unlisted = sorted(set(by_id) - set(listed))
        if dupes:
            dataset.append(("FAIL", "manifest", f"scenarios in more than one group: {dupes}"))
        if unlisted:
            dataset.append(("FAIL", "manifest", f"scenarios in no group: {unlisted}"))
        if manifest.get("scenario_count") not in (None, len(by_id)):
            dataset.append(("FAIL", "manifest", f"scenario_count {manifest['scenario_count']} != {len(by_id)}"))
    else:
        groups = infer_groups(scs)
    for gid, members in groups.items():
        if len(members) < 2:
            continue
        states = {json.dumps(m["evaluation_only"]["gold_dialogue_state"], sort_keys=True) for m in members}
        if len(states) > 1:
            for m in members:
                issues[m["scenario_id"]].append(("FAIL", "group", f"group {gid}: variants disagree on gold_dialogue_state"))
        sets = [(m["scenario_id"], set(candidates(db, m["evaluation_only"]["hidden_user_goal"]))) for m in members]
        for (a, sa), (b, sb) in combinations(sets, 2):
            if sa & sb:
                issues[a].append(("FAIL", "group", f"group {gid}: hidden target overlaps {b} on {sorted(sa & sb)}"))
        for u in members[0]["evaluation_only"]["gold_dialogue_state"]["unresolved"]:
            values = Counter(json.dumps(m["evaluation_only"]["hidden_user_goal"].get(u["slot"])) for m in members)
            if len(values) < 2 or len(set(values.values())) != 1:
                for m in members:
                    issues[m["scenario_id"]].append(("FAIL", "group", f"group {gid}: hidden {u['slot']} not balanced {dict(values)}"))
    return issues, dataset


# ------------------------------------------------------------ dataset hint detector
def _keyword(slot, value):
    if slot == "location":
        return LOCATION_WORDS.get(value)
    if slot == "cuisine" and isinstance(value, str):
        return value.lower()
    return None


def mention_order(turns, before_turn, slot, values):
    """(first_mentioned, last_mentioned) among values, from the text before the
    ambiguous turn; None if some value is never mentioned."""
    text = " ".join(t["text"].lower() for t in turns if t["turn"] < before_turn)
    firsts, lasts = {}, {}
    for v in values:
        kw = _keyword(slot, v)
        if kw is None:
            return None, None
        hits = [m.start() for m in re.finditer(rf"\b{re.escape(kw)}\b", text)]
        if not hits:
            return None, None
        firsts[v], lasts[v] = hits[0], hits[-1]
    return min(firsts, key=firsts.get), max(lasts, key=lasts.get)


def hint_items(sc, db):
    """One record per unresolved item of a should-ask scenario."""
    ev = sc["evaluation_only"]
    if not ev["gold_decision"]["should_ask"]:
        return []
    by_id = {r["restaurant_id"]: r for r in db}
    state, hidden = ev["gold_dialogue_state"], ev["hidden_user_goal"]
    turns = sc["model_visible"]["dialogue_prefix"]
    out = []
    for u in state.get("unresolved", []):
        slot = u["slot"]
        values = [i.get(slot) for i in u["interpretations"]]
        hv = hidden.get(slot)
        first, last = mention_order(turns, u["turn"], slot, values)
        sets = {}
        for i in u["interpretations"]:
            ids = candidates(db, {**state["active"], **i})
            sets[json.dumps(i.get(slot))] = [by_id[x] for x in ids]
        h = sets.get(json.dumps(hv), [])
        others = [r for k, rs in sets.items() if k != json.dumps(hv) for r in rs]
        out.append({
            "scenario_id": sc["scenario_id"], "slot": slot, "hidden": hv,
            "hidden_is_first": None if first is None else first == hv,
            "hidden_is_last": None if last is None else last == hv,
            "hidden_better": set_dominates(h, others) and not set_dominates(others, h),
            "other_better": set_dominates(others, h) and not set_dominates(h, others),
            "hidden_cheaper": bool(h and others) and min(r["price_per_person"] for r in h)
                              < min(r["price_per_person"] for r in others),
        })
    return out


def hint_report(scs, db, threshold=BALANCE_THRESHOLD):
    """Balance report over should-ask items. Returns (report lines, per-scenario
    issues, dataset-level issues)."""
    items = [x for sc in scs for x in hint_items(sc, db)]
    lines, per, dataset = [], defaultdict(list), []
    n = len(items)
    lines.append(f"Hint/balance report: {n} unresolved items in should-ask scenarios")
    if not n:
        return lines, per, dataset

    def rate(key):
        known = [x[key] for x in items if x[key] is not None]
        return (sum(known), len(known))

    def pct(k, m):
        return f"{k}/{m} ({k / m:.0%})" if m else "n/a"

    for key, label in [("hidden_is_first", "hidden = first-mentioned option"),
                       ("hidden_is_last", "hidden = last-mentioned option"),
                       ("hidden_cheaper", "hidden option has the cheapest restaurant"),
                       ("hidden_better", "hidden option alone has a clearly better restaurant"),
                       ("other_better", "another option alone has a clearly better restaurant")]:
        k, m = rate(key)
        lines.append(f"  {label:55s} {pct(k, m)}")
    k, m = rate("hidden_is_last")
    if m >= MIN_FOR_BALANCE and not (1 - threshold) <= k / m <= threshold:
        dataset.append(("WARN", "hint_last_mentioned",
                        f"hidden answer is the last-mentioned option in {pct(k, m)} of should-ask items"))
    k, m = rate("hidden_cheaper")
    if m >= MIN_FOR_BALANCE and not (1 - threshold) <= k / m <= threshold:
        dataset.append(("WARN", "hint_cheaper",
                        f"hidden option has the cheapest restaurant in {pct(k, m)} of should-ask items"))
    k, m = rate("hidden_better")
    if m and k / m > DOMINANCE_RATE_LIMIT:
        dataset.append(("WARN", "hint_better_option",
                        f"hidden option alone has a clearly better restaurant in {pct(k, m)} of should-ask items"))
    by_slot = defaultdict(Counter)
    for x in items:
        by_slot[x["slot"]][json.dumps(x["hidden"])] += 1
    for slot, cnt in sorted(by_slot.items()):
        total = sum(cnt.values())
        lines.append(f"  hidden {slot} values: " + ", ".join(f"{v}={c}" for v, c in cnt.most_common()))
        value, top = cnt.most_common(1)[0]
        if total >= MIN_FOR_BALANCE and top / total > threshold:
            dataset.append(("WARN", "hint_same_option",
                            f"hidden {slot} is {value} in {pct(top, total)} of should-ask items"))
    for x in items:
        if x["hidden_better"]:
            per[x["scenario_id"]].append(("WARN", "hint_better_option",
                                          f"only the hidden {x['slot']} option has a clearly better restaurant"))
    return lines, per, dataset


# ------------------------------------------------------------ main
def load_scenarios(root):
    paths = sorted(glob.glob(os.path.join(root, "**", "*.json"), recursive=True))
    out = []
    for p in paths:
        with open(p) as f:
            sc = json.load(f)
        if isinstance(sc, dict) and "scenario_id" in sc and "evaluation_only" in sc:
            out.append((p, sc))
    return out


def validate(scenario_dirs, db, manifests=(), threshold=BALANCE_THRESHOLD):
    """Run every check. Returns (loaded [(path, scenario)], {path: issues}, dataset issues,
    {path: computed}, report lines)."""
    loaded = [x for d in scenario_dirs for x in load_scenarios(d)]
    scs = [sc for _, sc in loaded]
    group_issues, dataset = defaultdict(list), []
    if manifests:
        for m in manifests:
            with open(m) as f:
                manifest = json.load(f)
            ids = {s for g in manifest.get("groups", []) for s in g["scenario_ids"]}
            gi, ds = group_checks([sc for sc in scs if sc["scenario_id"] in ids] or scs, db, manifest)
            for k, v in gi.items():
                group_issues[k] += v
            dataset += [(lvl, chk, f"{os.path.basename(os.path.dirname(m))}: {msg}") for lvl, chk, msg in ds]
        covered = {s for m in manifests for g in json.load(open(m)).get("groups", []) for s in g["scenario_ids"]}
        rest = [sc for sc in scs if sc["scenario_id"] not in covered]
        if rest:
            gi, _ = group_checks(rest, db)
            for k, v in gi.items():
                group_issues[k] += v
    else:
        gi, _ = group_checks(scs, db)
        group_issues.update(gi)
    report, hint_per, hint_dataset = hint_report(scs, db, threshold)
    per, computed_by_path, seen = {}, {}, {}
    for p, sc in loaded:
        sid = sc["scenario_id"]
        computed, issues = analyse(sc, db)
        if sid in seen:
            issues.append(("FAIL", "duplicate_id", f"also in {seen[sid]}"))
        seen[sid] = p
        if os.path.splitext(os.path.basename(p))[0] != sid:
            issues.append(("FAIL", "file_name", "file name does not match scenario_id"))
        issues += group_issues.get(sid, []) + hint_per.get(sid, [])
        per[p] = issues
        computed_by_path[p] = computed
    return loaded, per, dataset + hint_dataset, computed_by_path, report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=os.path.join("data", "restaurants.json"))
    ap.add_argument("--scenarios", nargs="+", default=[os.path.join("data", "scenarios")])
    ap.add_argument("--manifest", nargs="*", default=[],
                    help="dataset-manifest.json file(s) describing the ambiguity groups")
    ap.add_argument("--log", default="quality_log.csv")
    ap.add_argument("--write-computed", action="store_true",
                    help="write computed candidate sets back into each file")
    ap.add_argument("--balance-threshold", type=float, default=BALANCE_THRESHOLD)
    args = ap.parse_args()

    db = json.load(open(args.db))
    loaded, per, dataset_issues, computed_by_path, report = validate(
        args.scenarios, db, args.manifest, args.balance_threshold)
    paths = [p for p, _ in loaded]
    scs = [sc for _, sc in loaded]
    hint_dataset = dataset_issues

    rows, n_fail = [], 0
    for p, sc in zip(paths, scs):
        sid = sc["scenario_id"]
        computed, issues = computed_by_path[p], per[p]
        if args.write_computed:
            sc["evaluation_only"]["computed_by_validator"] = computed
            with open(p, "w") as f:
                json.dump(sc, f, indent=2)
                f.write("\n")
        if not issues:
            rows.append([sid, "all", "PASS", ""])
        for lvl, chk, msg in issues:
            rows.append([sid, chk, lvl, msg])
            n_fail += lvl == "FAIL"
    for lvl, chk, msg in hint_dataset:
        rows.append(["DATASET", chk, lvl, msg])
    with open(args.log, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["scenario_id", "check", "status", "message"])
        w.writerows(rows)
    n_warn = sum(r[2] == "WARN" for r in rows)
    print(f"{len(scs)} scenarios | {n_fail} FAIL | {n_warn} WARN | log -> {args.log}")
    for r in rows:
        if r[2] != "PASS":
            print("  ", *r)
    print("\n".join(report))
    sys.exit(1 if n_fail else 0)


if __name__ == "__main__":
    main()
