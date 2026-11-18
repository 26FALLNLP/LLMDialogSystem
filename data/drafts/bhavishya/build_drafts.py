"""Build Bhavishya's draft scenarios (parts 4a-4g) from the restaurant database.

Run from the repo root:
    python data/drafts/bhavishya/build_drafts.py

Nothing is guessed: every configuration is found by searching the database,
and every candidate set, ask decision and number of questions needed is
computed with the same functions the validator uses (data/validate.py).
The script refuses to write a scenario the validator would FAIL.

Uses the database the repo currently uses (data/restaurants.json:
near_station / near_mall / vegetarian_options / open_for_dinner), because the
team harbor/campus database is not in the repository.
"""
import json
import random
import shutil
import sys
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from data.validate import analyse, candidates, set_dominates  # noqa: E402

OUT = ROOT / "data" / "drafts" / "bhavishya"
DB = json.loads((ROOT / "data" / "restaurants.json").read_text())
BY_ID = {r["restaurant_id"]: r for r in DB}
CUISINES = sorted({r["cuisine"] for r in DB})
TEXT_SOURCE = "draft by Claude; wording to be regenerated with Qwen before testing"
FOLDERS = {"4a": "should_ask_pairs", "4b": "two_question", "4c": "swapped_twins",
           "4d": "suggestion_traps", "4e": "paraphrases", "4f": "long_dialogues", "4g": "fixes"}
OTHER = {"station": "mall", "mall": "station"}


# ----------------------------------------------------------------- helpers
def rows(ids):
    return [BY_ID[i] for i in ids]


def no_clear_winner(*sets):
    """No interpretation has a restaurant clearly better than all of another's."""
    for i, a in enumerate(sets):
        for j, b in enumerate(sets):
            if i != j and set_dominates(rows(a), rows(b)):
                return False
    return True


def describe(ids):
    return ", ".join(f"{i} {BY_ID[i]['name']} (${BY_ID[i]['price_per_person']})" for i in ids) or "(none)"


def base_constraints(cuisine=None, budget=None, veg=False, meal="lunch", location=None):
    c = {}
    if cuisine:
        c["cuisine"] = cuisine
    if budget is not None:
        c["max_price"] = budget
    if location:
        c["location"] = location
    if veg:
        c["vegetarian"] = True
    if meal == "dinner":
        c["dinner"] = True
    return c


def cuisine_phrase(c):
    if c is None:
        return "I'm looking for somewhere to eat."
    if isinstance(c, list):
        return f"I'm up for {c[0]} or {c[1]} food, either is fine."
    return f"I'm in the mood for {c} food."


def meal_sentence(meal, veg):
    s = "It's for dinner." if meal == "dinner" else "It's for lunch."
    return s + (" I also need vegetarian options." if veg else "")


def answers_for(goal):
    c = goal.get("cuisine")
    if c is None:
        cuisine = "I'm open to any cuisine."
    elif isinstance(c, list):
        cuisine = f"Either {c[0]} or {c[1]} is fine."
    else:
        cuisine = f"{c}, please."
    loc = goal.get("location")
    return {
        "cuisine": cuisine,
        "max_price": f"No more than ${goal['max_price']} per person." if "max_price" in goal else "I don't have a budget.",
        "location": f"Near the {loc}." if loc else "I don't mind which area.",
        "vegetarian": "Yes, I need vegetarian options." if goal.get("vegetarian") else "No dietary restrictions.",
        "dinner": "Yes, it needs to be open for dinner." if goal.get("dinner") else "It doesn't need to be open for dinner.",
        "_unsupported": "I don't have a preference on that.",
        "_multi_question": "Sorry, one thing at a time - what did you want to know first?",
    }


def scenario(sid, family, variant, stype, part, turns, acts, goal, active, *, unresolved=(),
             superseded=(), proposed=(), relations=(), should_ask=False, necessary=None,
             necessary_list=None, questions_needed=None, note="", extra=None):
    """Assemble one scenario in the repo's exact file format and check it."""
    assert len(turns) == len(acts)
    decision = {"should_ask": should_ask, "necessary_question": necessary,
                "any_other_question_is_unnecessary": True}
    if necessary_list:
        decision["necessary_questions"] = necessary_list
    if questions_needed is not None:
        decision["questions_needed"] = questions_needed
    ev = {
        "scenario_type": stype,
        "template_family_id": family,
        "variant": variant,
        "contrast_note": note,
        "turn_plan": [{"turn": i, "speaker": s, "act": a} for i, ((s, _), a) in enumerate(zip(turns, acts), 1)],
        "hidden_user_goal": goal,
        "predefined_clarification_answers": answers_for(goal),
        "gold_dialogue_state": {
            "at_turn": len(turns), "active": active, "superseded": list(superseded),
            "proposed_not_accepted": list(proposed), "unresolved": list(unresolved)},
        "gold_relation_links": list(relations),
        "gold_decision": decision,
        "flags_for_team": [],
        "draft_part": part,
    }
    ev.update(extra or {})
    sc = {
        "scenario_id": sid, "author": "BB", "text_source": TEXT_SOURCE,
        "model_visible": {
            "dialogue_prefix": [{"turn": i, "speaker": s, "text": t} for i, (s, t) in enumerate(turns, 1)],
            "restaurant_database": "restaurants.json"},
        "evaluation_only": ev,
    }
    computed, issues = analyse(sc, DB)
    fails = [i for i in issues if i[0] == "FAIL"]
    if fails:
        raise SystemExit(f"{sid} would FAIL validation: {fails}")
    ev["computed_by_validator"] = computed
    return sc


def location_unresolved(turn, expression, order):
    return [{"slot": "location", "turn": turn, "expression": expression,
             "interpretations": [{"location": o} for o in order]}]


# ----------------------------------------------------------------- configuration search
BUDGETS = list(range(12, 51))


def location_split(c, veg, meal, b):
    base = base_constraints(c, b, veg, meal)
    return (candidates(DB, {**base, "location": "station"}),
            candidates(DB, {**base, "location": "mall"}))


def shared_loc(c, veg, meal, b):
    s, m = location_split(c, veg, meal, b)
    return sorted(set(s) & set(m))


def round_up(b, ok):
    """Prefer a budget that is a multiple of 5 if it is still valid."""
    r = -(-b // 5) * 5
    return r if r <= 50 and ok(r) else b


def location_configs():
    """Configs where 'near there' (station vs mall) has no shared restaurant, every
    reading has 1-3 restaurants, no reading is clearly better, and one change
    (higher budget, or lunch instead of dinner) creates a shared restaurant."""
    opts = [None] + CUISINES + [[a, b] for i, a in enumerate(CUISINES) for b in CUISINES[i + 1:]]
    found = {}
    for c in opts:
        for veg in (False, True):
            for meal in ("dinner", "lunch"):
                for b in BUDGETS:
                    s, m = location_split(c, veg, meal, b)
                    if not s or not m or set(s) & set(m) or len(s) > 3 or len(m) > 3:
                        continue
                    if not no_clear_winner(s, m):
                        continue
                    b2 = next((x for x in BUDGETS if x > b and shared_loc(c, veg, meal, x)), None)
                    lunch_ok = meal == "dinner" and bool(shared_loc(c, veg, "lunch", b))
                    if not (b2 or lunch_ok):
                        continue
                    key = (tuple(s), tuple(m))
                    cfg = {"cuisine": c, "veg": veg, "meal": meal, "budget": b,
                           "b_budget": b2, "lunch_ok": lunch_ok, "S": s, "M": m}
                    old = found.get(key)
                    # prefer round budgets, then the lowest budget
                    rank = (b % 5 != 0, b)
                    if old is None or rank < (old["budget"] % 5 != 0, old["budget"]):
                        found[key] = cfg
    out = list(found.values())
    for cfg in out:
        if cfg["b_budget"]:
            cfg["b_budget"] = round_up(cfg["b_budget"],
                                       lambda x: bool(shared_loc(cfg["cuisine"], cfg["veg"], cfg["meal"], x)))
    return out


def pick_diverse(configs, n, used, key=lambda c: set(c["S"]) | set(c["M"])):
    """Greedy: take configs that reuse the fewest already-used restaurants."""
    chosen, pool = [], list(configs)
    while pool and len(chosen) < n:
        pool.sort(key=lambda c: (len(key(c) & used), repr(sorted(c.items(), key=str))))
        c = pool.pop(0)
        chosen.append(c)
        used |= key(c)
    if len(chosen) < n:
        raise SystemExit(f"only found {len(chosen)} configurations, needed {n}")
    return chosen


def cuisine_ref_configs():
    found = []
    for i, x in enumerate(CUISINES):
        for y in CUISINES[i + 1:]:
            for loc in (None, "station", "mall"):
                for veg in (False, True):
                    for meal in ("dinner", "lunch"):
                        for b in BUDGETS:
                            base = base_constraints(None, b, veg, meal, loc)
                            sx = candidates(DB, {**base, "cuisine": x})
                            sy = candidates(DB, {**base, "cuisine": y})
                            if not sx or not sy or len(sx) > 3 or len(sy) > 3:
                                continue
                            if not no_clear_winner(sx, sy):
                                continue
                            found.append({"X": x, "Y": y, "loc": loc, "veg": veg, "meal": meal,
                                          "budget": b, "SX": sx, "SY": sy})
                            break  # lowest budget per setting
    return found


def two_question_configs():
    """Only a few cuisine pairs work in this database, so each setting is used
    twice: preferably with a different set of candidate restaurants, otherwise
    with a different budget. Returned in alternating order of settings."""
    settings = {}
    for i, x in enumerate(CUISINES):
        for y in CUISINES[i + 1:]:
            for veg in (False, True):
                for meal in ("dinner", "lunch"):
                    for b in BUDGETS:
                        base = base_constraints(None, b, veg, meal)
                        grid = {(c, l): candidates(DB, {**base, "cuisine": c, "location": l})
                                for c in (x, y) for l in ("station", "mall")}
                        if not all(grid.values()) or any(len(v) > 3 for v in grid.values()):
                            continue
                        ok = all(not set(grid[(c, "station")]) & set(grid[(c, "mall")]) and
                                 no_clear_winner(grid[(c, "station")], grid[(c, "mall")]) for c in (x, y))
                        ok = ok and all(no_clear_winner(grid[(x, l)], grid[(y, l)]) for l in ("station", "mall"))
                        if ok:
                            settings.setdefault((x, y, veg, meal), []).append(
                                {"X": x, "Y": y, "veg": veg, "meal": meal, "budget": b, "grid": grid})
    firsts, seconds = [], []
    for key in sorted(settings):
        opts = settings[key]
        first = opts[0]
        other = [o for o in opts if o["grid"] != first["grid"]]
        second = other[0] if other else (opts[-1] if len(opts) > 1 else None)
        firsts.append(first)
        if second is not None:
            seconds.append(second)
    return firsts + seconds


# ----------------------------------------------------------------- 4a / 4c / 4e : location pairs
DEIXIS = ["Can you find me something near there?", "Let's look over that side.",
          "Something around that area would be great.", "Can you check that part of town for me?",
          "Find me a spot over there.", "Let's go with that area. What's good there?",
          "Somewhere near there works for me.", "Pick something on that side, please.",
          "I'd like something around there.", "Can you look in that area?"]
PARA_DEIXIS = [("Something around that area, please.", "Let's try over that side."),
               ("Anything over that side?", "What's good around that area?"),
               ("Can you find something near there?", "Let's go over that side."),
               ("What's around that area?", "Find me something near there."),
               ("Let's look over that side.", "Something around there would be good.")]


def b_change(cfg, i):
    """Which single change makes a shared restaurant: budget (default) or lunch."""
    use_lunch = cfg["lunch_ok"] and (not cfg["b_budget"] or i % 3 == 2)
    return ("lunch", None) if use_lunch else ("budget", cfg["b_budget"])


def location_family(kind, idx, cfg, o1, hidden, phrase, part="4a", variant_suffix="",
                    wording=0, family=None, sid_base=None, extra_note=""):
    """Build the A/B pair for one location-ambiguity configuration.
    kind = 'deixis' or 'ordinal'. o1 = area mentioned first."""
    o2 = OTHER[o1]
    c, veg, meal, b = cfg["cuisine"], cfg["veg"], cfg["meal"], cfg["budget"]
    change, b2 = b_change(cfg, idx)
    fam = family or f"BB-{'LOC' if kind == 'deixis' else 'ORD'}-{idx + 1:02d}"
    sid_base = sid_base or fam
    out = []
    for side in ("A", "B"):
        bb = b2 if (side == "B" and change == "budget") else b
        mm = "lunch" if (side == "B" and change == "lunch") else meal
        if wording == 0:
            t1 = cuisine_phrase(c)
            t2 = f"Sure! There are good options near the {o1} and near the {o2}."
            t4 = "Got it, I'll keep the budget in mind."
            t6 = "Okay, noted."
        elif wording == 1:
            t1 = "Can you help me find a place to eat? " + ("" if c is None else
                 (f"{c[0]} or {c[1]} would both be fine." if isinstance(c, list) else f"I'd like {c}."))
            t2 = f"Happy to help. I can see places by the {o1} and by the {o2}."
            t4 = "Thanks, that helps."
            t6 = "Understood."
        else:
            t1 = "I need ideas for a meal. " + ("Any cuisine works." if c is None else
                 (f"Maybe {c[0]}, maybe {c[1]}, I'm easy." if isinstance(c, list) else f"{c} sounds good to me."))
            t2 = f"Of course. A couple of spots are close to the {o1}, and a couple are close to the {o2}."
            t4 = "Okay, budget noted."
            t6 = "Sounds good."
        t3 = f"My budget is ${bb} per person."
        t5 = meal_sentence(mm, veg)
        if kind == "deixis":
            t7 = phrase
            turns = [("user", t1), ("assistant", t2), ("user", t3), ("assistant", t4),
                     ("user", t5), ("assistant", t6), ("user", t7)]
            expr = phrase
        else:
            t4 = f"Okay. With that budget, the {o2} side and the {o1} side both still have choices."
            t7 = phrase
            turns = [("user", t1), ("assistant", t2), ("user", t3), ("assistant", t4),
                     ("user", t5), ("assistant", t6), ("user", t7)]
            expr = phrase
        base = base_constraints(c, bb, veg, mm)
        goal = {**base, "location": hidden}
        s, m = location_split(c, veg, mm, bb)
        shared = sorted(set(s) & set(m))
        acts = ["user states " + ("no cuisine preference" if c is None else f"cuisine={c}"),
                f"assistant mentions both areas ({o1} first, {o2} second); not a user choice",
                f"user states max_price={bb}", "assistant acknowledges",
                f"user states meal={mm}" + (" (dinner=true)" if mm == "dinner" else " (no dinner constraint)")
                + (", vegetarian=true" if veg else ""),
                "assistant acknowledges",
                f"user: '{expr}' = station or mall (UNRESOLVED; hidden: {hidden})"]
        if kind == "ordinal":
            acts[3] = f"assistant re-lists the areas in the opposite order ({o2} first, {o1} second)"
            acts[6] = (f"user: 'second place' = {o2} (second in turn 2) or {o1} (second in turn 4) "
                       f"(UNRESOLVED; hidden: {hidden})")
        note = (f"A: station -> {describe(location_split(c, veg, meal, b)[0])}; mall -> "
                f"{describe(location_split(c, veg, meal, b)[1])}; nothing near both -> ask. "
                + (f"B: budget ${b2} makes {describe(shared_loc(c, veg, meal, b2))} valid for both -> recommend it."
                   if change == "budget" else
                   f"B: lunch instead of dinner makes {describe(shared_loc(c, veg, 'lunch', b))} valid for both -> recommend it.")
                + extra_note)
        variant = side + variant_suffix
        suffix = {"": "", "_swap": "-SW", "_para1": "-P1", "_para2": "-P2"}.get(variant_suffix, "")
        sid = f"{sid_base}{side}{suffix}"
        out.append(scenario(
            sid, fam, variant, "ambiguous_reference", part, turns, acts, goal, base,
            unresolved=location_unresolved(7, expr, [o1, o2]),
            should_ask=(side == "A"), necessary="location@t7" if side == "A" else None,
            note=note,
            extra={"ambiguity_kind": "location_deixis" if kind == "deixis" else "ordinal_reference",
                   "mention_order": [o1, o2], "single_change": change}))
        assert bool(shared) == (side == "B"), sid
    return out


# ----------------------------------------------------------------- 4a / 4c : cuisine reference
FRIENDS = ["Maya", "Sam", "Priya", "Leo", "Nora"]


def cuisine_family(idx, cfg, x_first, hidden, part="4a", variant_suffix="", family=None, sid_base=None):
    x, y = (cfg["X"], cfg["Y"]) if x_first else (cfg["Y"], cfg["X"])
    loc, veg, meal, b = cfg["loc"], cfg["veg"], cfg["meal"], cfg["budget"]
    fam = family or f"BB-CUI-{idx + 1:02d}"
    sid_base = sid_base or fam
    friend = FRIENDS[idx % len(FRIENDS)]
    out = []
    for side in ("A", "B"):
        t1 = f"Two of my friends each recommended a place around here: one {x}, one {y}."
        t2 = "Both sound like good options! Want me to look into them?"
        t3 = f"I'd like somewhere near the {loc}." if loc else "The area doesn't matter to me."
        t4 = f"Got it, near the {loc}." if loc else "Okay, anywhere works."
        t5 = f"No more than ${b} a person. " + meal_sentence(meal, veg)
        t6 = "Noted."
        t7 = (f"Let's go with {friend}'s recommendation." if side == "A"
              else "Either of those cuisines is fine with me.")
        turns = [("user", t1), ("assistant", t2), ("user", t3), ("assistant", t4),
                 ("user", t5), ("assistant", t6), ("user", t7)]
        base = base_constraints(None, b, veg, meal, loc)
        if side == "A":
            goal, active = {**base, "cuisine": hidden}, dict(base)
            unresolved = [{"slot": "cuisine", "turn": 7, "expression": f"{friend}'s recommendation",
                           "interpretations": [{"cuisine": x}, {"cuisine": y}]}]
        else:
            goal = active = {**base, "cuisine": [x, y]}
            unresolved = []
        acts = [f"user mentions two cuisines ({x} first, {y} second); neither chosen; no link to who said which",
                "assistant offers", f"user states location={loc}" if loc else "user: no location constraint",
                "assistant acknowledges",
                f"user states max_price={b}, meal={meal}" + (", vegetarian=true" if veg else ""),
                "assistant acknowledges",
                (f"user: '{friend}'s recommendation' = {x} or {y} (UNRESOLVED; hidden: {hidden})" if side == "A"
                 else f"user: cuisine in {{{x}, {y}}}; disjunction, not ambiguity")]
        sx = candidates(DB, {**base, "cuisine": x})
        sy = candidates(DB, {**base, "cuisine": y})
        note = (f"A: {x} -> {describe(sx)}; {y} -> {describe(sy)}; no restaurant serves both -> ask. "
                f"B: user accepts either cuisine (one turn changed; a single restaurant cannot serve two "
                f"cuisines, so this is the only one-change way to remove the need to ask).")
        suffix = {"": "", "_swap": "-SW"}[variant_suffix]
        out.append(scenario(
            f"{sid_base}{side}{suffix}", fam, side + variant_suffix, "ambiguous_reference", part, turns, acts,
            goal, active, unresolved=unresolved, should_ask=(side == "A"),
            necessary="cuisine@t7" if side == "A" else None, note=note,
            extra={"ambiguity_kind": "cuisine_reference", "mention_order": [x, y], "single_change": "accept_either"}))
    return out


# ----------------------------------------------------------------- 4b : two questions
def two_question(idx, cfg, x_first, o1, hidden_c, hidden_l):
    x, y = (cfg["X"], cfg["Y"]) if x_first else (cfg["Y"], cfg["X"])
    o2 = OTHER[o1]
    veg, meal, b = cfg["veg"], cfg["meal"], cfg["budget"]
    t1 = "My friend is choosing where we eat tonight." if meal == "dinner" else "My friend is choosing where we get lunch."
    turns = [("user", t1), ("assistant", "Fun! What is she considering?"),
             ("user", f"She's deciding between {x} and {y}, either near the {o1} or near the {o2}."),
             ("assistant", "Got it. Any budget?"),
             ("user", f"Up to ${b} each." + (" We both need vegetarian options." if veg else "")),
             ("assistant", "Noted."),
             ("user", "She just texted me her choice. Can you find a place that matches it?")]
    base = base_constraints(None, b, veg, meal)
    goal = {**base, "cuisine": hidden_c, "location": hidden_l}
    unresolved = [
        {"slot": "cuisine", "turn": 7, "expression": "her choice", "interpretations": [{"cuisine": x}, {"cuisine": y}]},
        {"slot": "location", "turn": 7, "expression": "her choice", "interpretations": [{"location": o1}, {"location": o2}]}]
    grid = "; ".join(f"{c}+{l} -> {describe(cfg['grid'][(c, l)])}" for c in (x, y) for l in (o1, o2))
    acts = ["user: friend decides; " + ("tonight = dinner" if meal == "dinner" else "lunch, no dinner constraint"),
            "assistant asks", f"user lists two cuisines ({x}, {y}) and two areas ({o1}, {o2}); none chosen",
            "assistant asks budget", f"user states max_price={b}" + (", vegetarian=true" if veg else ""),
            "assistant acknowledges",
            f"user: 'her choice' = cuisine AND area unknown (UNRESOLVED x2; hidden: {hidden_c} + {hidden_l})"]
    note = (f"Two things unclear. {grid}. Knowing only the cuisine still leaves station vs mall with no shared "
            f"restaurant; knowing only the area still leaves two cuisines -> exactly 2 questions needed.")
    sid = f"BB-TWOQ-{idx + 1:02d}"
    return scenario(sid, sid, "single", "ambiguous_reference", "4b", turns, acts, goal, dict(base),
                    unresolved=unresolved, should_ask=True, necessary="cuisine@t7",
                    necessary_list=["cuisine@t7", "location@t7"], questions_needed=2, note=note,
                    extra={"ambiguity_kind": "two_unresolved", "mention_order": {"cuisine": [x, y], "location": [o1, o2]}})


# ----------------------------------------------------------------- 4d : suggestion traps
HEDGES = ["Hmm, I'll think about it.", "Maybe, I'm not sure yet.", "I don't know, possibly.",
          "Let me think about that one.", "I'm not sure about that yet.", "Hmm, maybe another time.",
          "Possibly, we'll see.", "Oh, by the way, this is for my dad's birthday."]


def trap_pair(idx, kind, cfg):
    fam = f"BB-SUG-{idx + 1:02d}"
    hedge = HEDGES[idx % len(HEDGES)]
    out = []
    for side in ("A", "B"):
        if kind == "cuisine":
            x, y, loc, b, meal = cfg["X"], cfg["Y"], cfg["loc"], cfg["budget"], cfg["meal"]
            t1 = f"I'd like {x} food near the {loc}."
            t3 = f"No more than ${b} per person." + (" It's for dinner." if meal == "dinner" else "")
            t4 = f"There are also some nice {y} places near the {loc}. Would {y} work instead?"
            accept = f"Sure, let's do {y} instead."
            base = base_constraints(None, b, False, meal, loc)
            orig, sugg, slot, sugg_turn_ref = {**base, "cuisine": x}, {**base, "cuisine": y}, "cuisine", (x, y)
        else:
            c, loc, b, meal = cfg["cuisine"], cfg["loc"], cfg["budget"], cfg["meal"]
            l2 = OTHER[loc]
            t1 = f"I'm looking for {c} food near the {loc}."
            t3 = f"No more than ${b} per person." + (" It's for dinner." if meal == "dinner" else "")
            t4 = f"The {l2} area also has {c} food in that range. Want me to look there instead?"
            accept = f"Yes, let's look near the {l2} instead."
            base = base_constraints(c, b, False, meal)
            orig, sugg, slot, sugg_turn_ref = {**base, "location": loc}, {**base, "location": l2}, "location", (loc, l2)
        t5 = hedge if side == "A" else accept
        turns = [("user", t1), ("assistant", "Sounds good! Any budget?"), ("user", t3), ("assistant", t4),
                 ("user", t5), ("assistant", "Okay!"), ("user", "What do you recommend?")]
        old, new = sugg_turn_ref
        acts = [f"user states {slot}={old}" + (f", cuisine={orig.get('cuisine')}" if slot == "location" else ""),
                "assistant asks budget",
                f"user states max_price={orig['max_price']}" + (", dinner=true" if orig.get("dinner") else ""),
                f"assistant PROPOSES {slot}={new}",
                (f"user does NOT accept ({'changes the subject' if 'birthday' in hedge else 'hedges'}); {slot} stays {old}"
                 if side == "A" else f"user ACCEPTS proposal; {slot}={new}"),
                "assistant acknowledges", "user requests recommendation"]
        good, wrong = candidates(DB, orig), candidates(DB, sugg)
        note = (f"A: suggestion not accepted -> {slot}={old}: {describe(good)}. Treating the suggestion as "
                f"accepted picks {describe(wrong)}, which is WRONG. B (control): explicit acceptance -> "
                f"{describe(wrong)} correct.")
        if side == "A":
            sc = scenario(f"{fam}A", fam, "A", "suggestion_acceptance", "4d", turns, acts, orig, orig,
                          proposed=[{"slot": slot, "value": new, "turn": 4, "status": "not accepted"}],
                          note=note, extra={"suggestion_trap": True})
        else:
            sc = scenario(f"{fam}B", fam, "B", "suggestion_acceptance", "4d", turns, acts, sugg, sugg,
                          superseded=[{"slot": slot, "value": old, "turn": 1}],
                          relations=[{"source_turn": 5, "target_turn": 4, "relation": "confirm", "slot": slot},
                                     {"source_turn": 5, "target_turn": 1, "relation": "revise", "slot": slot}],
                          note=note)
        out.append(sc)
    return out


# ----------------------------------------------------------------- 4f : long dialogues
def long_clear(idx, c, loc, b, key):
    """10 turns; the key detail is in the user's first message (turn 2)."""
    veg = key in ("veg+dinner", "veg")
    dinner = key in ("veg+dinner", "dinner")
    key_text = {"veg+dinner": "I need a place that's open for dinner and has vegetarian options.",
                "veg": "I need somewhere with vegetarian options, my partner doesn't eat meat.",
                "dinner": "I need a place that's open for dinner.",
                "budget": f"I can't spend more than ${b} per person."}[key]
    t8 = f"Near the {loc}." if key == "budget" else f"Near the {loc}, and let's keep it under ${b} a person."
    t9 = f"Okay: {c}, near the {loc}" + ("." if key == "budget" else f", under ${b}.")
    turns = [("assistant", "Hi! What can I help you with today?"), ("user", key_text),
             ("assistant", "Sure. Is this for a special occasion?"),
             ("user", "Yes, it's my sister's birthday. She just got a new job too."),
             ("assistant", "Congratulations to her! What food does she like?"),
             ("user", f"She loves {c} food."), ("assistant", "Great choice. Any area in mind?"),
             ("user", t8), ("assistant", t9), ("user", "Perfect. What would you recommend?")]
    goal = base_constraints(c, b, veg, "dinner" if dinner else "lunch", loc)
    forgot = {k: v for k, v in goal.items() if not (
        (k == "vegetarian" and veg) or (k == "dinner" and dinner) or (k == "max_price" and key == "budget"))}
    good, loose = candidates(DB, goal), candidates(DB, forgot)
    trap = sorted(set(loose) - set(good))
    acts = ["assistant greets", f"KEY DETAIL in first user message: {key}", "assistant asks occasion",
            "user: off-topic detail (no constraint)", "assistant asks cuisine", f"user states cuisine={c}",
            "assistant asks area", f"user states location={loc}" + ("" if key == "budget" else f", max_price={b}"),
            "assistant summary that LEAVES OUT the turn-2 detail (not a revision)", "user requests recommendation"]
    note = (f"Correct: {describe(good)}. Forgetting the turn-2 detail ({key}) would also allow "
            f"{describe(trap)}, which is wrong.")
    sid = f"BB-LONG-{idx + 1:02d}"
    return scenario(sid, sid, "single", "clear", "4f", turns, acts, goal, goal, note=note,
                    extra={"key_detail_turn": 2, "forgetting_trap": trap}), trap


def long_ambiguous(idx, cfg, o1, hidden):
    o2 = OTHER[o1]
    c, veg, meal, b = cfg["cuisine"], cfg["veg"], cfg["meal"], cfg["budget"]
    fam = f"BB-LONG-{idx + 1:02d}"
    out = []
    for side in ("A", "B"):
        bb = cfg["b_budget"] if side == "B" else b
        turns = [("user", cuisine_phrase(c)),
                 ("assistant", f"There are options near the {o1} and near the {o2}."),
                 ("user", "Nice. Unrelated, but I'm also trying to pick a birthday gift for my mom."),
                 ("assistant", "Flowers or a good book are always safe choices!"),
                 ("user", f"Good idea. Anyway, my budget is ${bb} per person."),
                 ("assistant", "Got it."), ("user", meal_sentence(meal, veg)), ("assistant", "Okay, noted."),
                 ("user", "Can you find me something in that area you mentioned at the start?")]
        base = base_constraints(c, bb, veg, meal)
        s, m = location_split(c, veg, meal, bb)
        acts = ["user states " + ("no cuisine preference" if c is None else f"cuisine={c}"),
                f"KEY DETAIL: assistant mentions both areas ({o1} first, {o2} second)",
                "user: off-topic", "assistant: off-topic reply", f"user states max_price={bb}",
                "assistant acknowledges", f"user states meal={meal}" + (", vegetarian=true" if veg else ""),
                "assistant acknowledges",
                f"user: 'that area you mentioned at the start' = station or mall (UNRESOLVED; hidden: {hidden})"]
        note = (f"Reference reaches back to turn 2. A: station -> {describe(location_split(c, veg, meal, b)[0])}; "
                f"mall -> {describe(location_split(c, veg, meal, b)[1])} -> ask. B: budget ${cfg['b_budget']} -> "
                f"{describe(shared_loc(c, veg, meal, cfg['b_budget']))} valid for both -> recommend.")
        out.append(scenario(
            f"{fam}{side}", fam, side, "ambiguous_reference", "4f", turns, acts, {**base, "location": hidden}, base,
            unresolved=location_unresolved(9, "that area you mentioned at the start", [o1, o2]),
            should_ask=(side == "A"), necessary="location@t9" if side == "A" else None, note=note,
            extra={"ambiguity_kind": "location_deixis", "mention_order": [o1, o2], "key_detail_turn": 2,
                   "single_change": "budget"}))
    return out


# ----------------------------------------------------------------- 4g : fixes
def load_original(sid):
    return json.loads((ROOT / "data" / "scenarios" / f"{sid}.json").read_text())


def fix_02():
    """XX-AMB-02A: 'over there' points at the most recently mentioned area (mall)."""
    out = []
    for orig_id, side in (("XX-AMB-02A", "A"), ("XX-AMB-02B", "B")):
        o = load_original(orig_id)
        ev = o["evaluation_only"]
        turns = [(t["speaker"], t["text"]) for t in o["model_visible"]["dialogue_prefix"]]
        turns[6] = ("user", "Great, find me something near where I'm headed.")
        acts = [p["act"] for p in ev["turn_plan"]]
        acts[6] = acts[6].replace("over there", "near where I'm headed")
        st = ev["gold_dialogue_state"]
        unresolved = [dict(u, expression="near where I'm headed") for u in st["unresolved"]]
        out.append(scenario(
            f"BB-FIX-AMB-02{side}", "BB-FIX-AMB-02", side, ev["scenario_type"], "4g", turns, acts,
            ev["hidden_user_goal"], st["active"], unresolved=unresolved, should_ask=ev["gold_decision"]["should_ask"],
            necessary=ev["gold_decision"]["necessary_question"], note=ev["contrast_note"],
            extra={"fix_of": orig_id, "mention_order": ["station", "mall"],
                   "fix_note": ("Removed hint: 'over there' (singular, distal) tends to point at the most recently "
                                "mentioned area, and the hidden answer (mall) was the last-mentioned area. Turn 7 now "
                                "says 'near where I'm headed', which is not tied to either mention. Everything else, "
                                "including the gold labels and restaurants (R28 vs R29, $22 vs $27, comparable), is unchanged.")}))
    return out


def fix_03(cref):
    """XX-AMB-03A: hidden Mexican was the last-mentioned cuisine AND El Comal (R13) beat Lotus Thai (R17)
    on everything (cheaper, near both areas, open for dinner)."""
    pick = None
    for prefer in (lambda c: {c["X"], c["Y"]} == {"Mexican", "Thai"}, lambda c: "Mexican" in (c["X"], c["Y"])):
        opts = [c for c in cref if prefer(c)]
        if opts:
            opts.sort(key=lambda c: (c["loc"] != "mall", not c["veg"], c["budget"] % 5 != 0, c["budget"]))
            pick = opts[0]
            break
    if pick is None:
        return [], "No configuration with hidden Mexican and no clearly-better option exists in this database."
    other = pick["Y"] if pick["X"] == "Mexican" else pick["X"]
    cfg = dict(pick, X="Mexican", Y=other)
    cfg["SX"], cfg["SY"] = (pick["SX"], pick["SY"]) if pick["X"] == "Mexican" else (pick["SY"], pick["SX"])
    # Mexican mentioned FIRST this time (original: last), hidden stays Mexican.
    pair = cuisine_family(0, cfg, True, "Mexican", part="4g", family="BB-FIX-AMB-03", sid_base="BB-FIX-AMB-03")
    changed = []
    if other != "Thai":
        changed.append(f"the second cuisine is {other} instead of Thai")
    changed.append(f"constraints are now location={cfg['loc']}, max_price={cfg['budget']}, "
                   f"vegetarian={cfg['veg']}, meal={cfg['meal']}")
    note = ("Removed hints: (1) the hidden cuisine (Mexican) was mentioned last; now it is mentioned first, which "
            "balances the original. (2) El Comal (R13) was cheaper, near both areas and open for dinner, so it beat "
            f"Lotus Thai (R17) on every count. With this database Mexican always has a clearly better option against "
            f"Thai near the mall, so: {'; '.join(changed)}. Candidates are now Mexican -> {describe(cfg['SX'])}, "
            f"{other} -> {describe(cfg['SY'])}, with neither clearly better. 'The cuisine they mentioned' became "
            "\"Maya's recommendation\" because both cuisines were mentioned by 'they'. Hidden answer stays Mexican.")
    for sc in pair:
        sc["evaluation_only"]["fix_of"] = "XX-AMB-03A" if sc["evaluation_only"]["variant"] == "A" else "XX-AMB-03B"
        sc["evaluation_only"]["fix_note"] = note
    return pair, None


def fix_04(locs):
    """XX-AMB-04A: 'I work by the station but I live by the mall' + 'dinner tonight' points at home (mall),
    and Pita Port (R37, $14) was clearly cheaper than the station options ($23, $33)."""
    opts = [c for c in locs if c["lunch_ok"] and c["meal"] == "dinner"]
    opts.sort(key=lambda c: (not (isinstance(c["cuisine"], list) and "Mediterranean" in c["cuisine"]),
                             not c["veg"], c["budget"]))
    cfg = dict(opts[0])
    cfg["b_budget"] = None  # force the B change to be lunch, like the original
    pair = location_family("deixis", 2, cfg, "station", "mall", "Find me something close to where I'll be.",
                           part="4g", family="BB-FIX-AMB-04", sid_base="BB-FIX-AMB-04")
    # Replace the opening with a neutral one: both areas, no work/home or time-of-day link.
    for sc in pair:
        t = sc["model_visible"]["dialogue_prefix"]
        t[0]["text"] = "I'll be around both the train station and the mall today. " + t[0]["text"]
        sc["evaluation_only"]["turn_plan"][0]["act"] += "; user says they will be near BOTH areas (no work/home cue)"
        sc["evaluation_only"]["turn_plan"][6]["act"] = ("user: 'close to where I'll be' = station or mall "
                                                        "(UNRESOLVED; hidden: mall)")
        sc["evaluation_only"]["fix_of"] = "XX-AMB-04A" if sc["evaluation_only"]["variant"] == "A" else "XX-AMB-04B"
        sc["evaluation_only"]["fix_note"] = (
            "Removed hints: (1) 'I work by the station but I live by the mall' + 'dinner tonight' lets a model infer "
            "'at home in the evening' = mall; now the user just says they'll be around both areas. (2) Pita Port "
            "(R37, $14) was $9-19 cheaper than every station option with the same features. Mediterranean alone "
            "always has that gap here, so the cuisine/budget changed to "
            f"{cfg['cuisine']}, ${cfg['budget']}, vegetarian={cfg['veg']}: station -> {describe(cfg['S'])}, "
            f"mall -> {describe(cfg['M'])}. Hidden answer stays mall; the A/B change stays dinner vs lunch.")
        computed, issues = analyse(sc, DB)
        assert not [i for i in issues if i[0] == "FAIL"], issues
        sc["evaluation_only"]["computed_by_validator"] = computed
    return pair


# ----------------------------------------------------------------- swap helper
def swapped(pair_builder):
    return pair_builder


# ----------------------------------------------------------------- main
def main():
    for folder in FOLDERS.values():
        shutil.rmtree(OUT / folder, ignore_errors=True)
    written = {}

    def save(part, scs):
        d = OUT / FOLDERS[part]
        d.mkdir(parents=True, exist_ok=True)
        for sc in scs:
            (d / f"{sc['scenario_id']}.json").write_text(json.dumps(sc, indent=2) + "\n")
            written.setdefault(part, []).append(sc["scenario_id"])

    locs = location_configs()
    used = set()
    loc_cfgs = pick_diverse(locs, 17, used)          # 10 deixis + 5 ordinal + 2 long
    deixis_cfgs, ordinal_cfgs, long_cfgs = loc_cfgs[:10], loc_cfgs[10:15], loc_cfgs[15:17]
    long_cfgs = [dict(c, b_budget=c["b_budget"] or next(x for x in BUDGETS if x > c["budget"]
                 and shared_loc(c["cuisine"], c["veg"], c["meal"], x))) for c in long_cfgs]

    # --- 4a + 4c + 4e : location deixis (hidden = first-mentioned in 5 of 10)
    # (area mentioned first, hidden area): 5 first-mentioned / 5 last; 5 station / 5 mall;
    # the first five (which also get paraphrases) are 3/2 on both.
    deixis_plan = [("station", "station"), ("mall", "station"), ("mall", "mall"), ("station", "mall"),
                   ("station", "station"), ("mall", "mall"), ("station", "mall"), ("mall", "station"),
                   ("station", "station"), ("station", "mall")]
    for i, cfg in enumerate(deixis_cfgs):
        o1, hidden = deixis_plan[i]
        save("4a", location_family("deixis", i, cfg, o1, hidden, DEIXIS[i]))
        # 4c twin: opposite order, hidden flipped (so its position is unchanged)
        save("4c", location_family("deixis", i, cfg, OTHER[o1], OTHER[hidden], DEIXIS[i], part="4c",
                                   variant_suffix="_swap"))
        if i < 5:  # 4e: two paraphrases, same answer key
            for k in (1, 2):
                save("4e", location_family("deixis", i, cfg, o1, hidden, PARA_DEIXIS[i][k - 1], part="4e",
                                           variant_suffix=f"_para{k}", wording=k))

    # --- 4a + 4c : ordinal reference (hidden = the area mentioned first AND last in 3 of 5)
    ordinal_plan = [("mall", "mall"), ("station", "mall"), ("station", "station"), ("mall", "station"),
                    ("station", "station")]
    for i, cfg in enumerate(ordinal_cfgs):
        o1, hidden = ordinal_plan[i]
        phrase = "Let's go with the second place you mentioned."
        save("4a", location_family("ordinal", i, cfg, o1, hidden, phrase))
        save("4c", location_family("ordinal", i, cfg, OTHER[o1], OTHER[hidden], phrase, part="4c",
                                   variant_suffix="_swap"))

    # --- 4a + 4c : cuisine reference (hidden = first-mentioned in 2 of 5)
    cref = cuisine_ref_configs()
    by_pair = {}
    for c in cref:
        by_pair.setdefault((c["X"], c["Y"]), []).append(c)
    pool = []
    for k in sorted(by_pair):
        opts = sorted(by_pair[k], key=lambda c: (c["budget"] % 5 != 0, c["budget"]))
        pool.append(opts[0])
    cui_cfgs = pick_diverse([c for c in pool if "Mexican" not in (c["X"], c["Y"])], 5, set(),
                            key=lambda c: {c["X"], c["Y"]})
    for i, cfg in enumerate(cui_cfgs):
        x_first = i % 2 == 0
        first, second = (cfg["X"], cfg["Y"]) if x_first else (cfg["Y"], cfg["X"])
        hidden = first if i in (0, 2) else second
        save("4a", cuisine_family(i, cfg, x_first, hidden))
        save("4c", cuisine_family(i, cfg, not x_first, second if hidden == first else first, part="4c",
                                  variant_suffix="_swap"))

    # --- 4b : two-question scenarios (hidden combos balanced)
    tq = two_question_configs()
    if len(tq) < 8:
        raise SystemExit(f"only {len(tq)} two-question configurations")
    tq_cfgs = tq[:8]
    # (cuisine order as found?, area mentioned first, hidden cuisine is first-mentioned?, hidden area is first?)
    # -> hidden area station 4 / mall 4; first-mentioned area 4/8; first-mentioned cuisine 4/8.
    tq_plan = [(True, "station", True, True), (False, "mall", False, True), (True, "station", False, False),
               (False, "mall", True, False), (True, "mall", True, True), (False, "station", False, True),
               (True, "mall", False, False), (False, "station", True, False)]
    for i, cfg in enumerate(tq_cfgs):
        x_first, o1, c_first, l_first = tq_plan[i]
        first_c, second_c = (cfg["X"], cfg["Y"]) if x_first else (cfg["Y"], cfg["X"])
        hidden_c = first_c if c_first else second_c
        hidden_l = o1 if l_first else OTHER[o1]
        save("4b", [two_question(i, cfg, x_first, o1, hidden_c, hidden_l)])

    # --- 4d : suggestion traps (4 cuisine swaps + 4 location swaps), each with an accepted control
    traps = []
    cuisine_traps = [c for c in cref if c["loc"] and not c["veg"]]
    cuisine_traps.sort(key=lambda c: (c["budget"] % 5 != 0, c["budget"], c["X"], c["Y"]))
    seen = set()
    for c in cuisine_traps:
        if len(traps) == 4:
            break
        if (c["X"], c["Y"]) in seen or c["X"] in {t[1]["X"] for t in traps}:
            continue
        seen.add((c["X"], c["Y"]))
        traps.append(("cuisine", c))
    loc_traps = [c for c in locs if isinstance(c["cuisine"], str) and not c["veg"]]
    for j, c in enumerate(sorted(loc_traps, key=lambda c: (c["cuisine"], c["budget"]))[:4]):
        traps.append(("location", {"cuisine": c["cuisine"], "loc": "station" if j % 2 == 0 else "mall",
                                   "budget": c["budget"], "meal": c["meal"]}))
    if len(traps) < 8:
        raise SystemExit(f"only {len(traps)} suggestion-trap configurations")
    for i, (kind, cfg) in enumerate(traps):
        save("4d", trap_pair(i, kind, cfg))

    # --- 4f : long dialogues (4 clear singles + 2 ambiguous A/B pairs)
    long_specs = []
    for key in ("veg+dinner", "veg", "dinner", "budget"):
        for c in CUISINES:
            for loc in ("station", "mall"):
                for b in (20, 25, 30, 35):
                    try:
                        sc, trap = long_clear(len(long_specs), c, loc, b, key)
                    except SystemExit:
                        continue
                    if trap and not any(s[0] == c for s in long_specs):
                        long_specs.append((c, loc, b, key, sc))
                        break
                else:
                    continue
                break
            if len(long_specs) and long_specs[-1][3] == key:
                break
    save("4f", [s[4] for s in long_specs])
    for j, cfg in enumerate(long_cfgs):
        o1 = "station"
        hidden = "station" if j == 0 else "mall"  # one first-mentioned, one last-mentioned
        save("4f", long_ambiguous(len(long_specs) + j, cfg, o1, hidden))

    # --- 4g : fixes
    save("4g", fix_02())
    f3, problem = fix_03(cref)
    if problem:
        print("4g AMB-03 fix skipped:", problem)
    save("4g", f3)
    save("4g", fix_04([c for c in locs if c not in loc_cfgs]))

    # --- proposed dev/test split for the drafts (family level, stratified by part; NOT frozen)
    rng = random.Random(6120)
    split = {"status": "PROPOSAL for the drafts only - not frozen. The frozen split for the original 36 "
                       "is data/splits/split.json and is not changed.",
             "seed": 6120, "dev_fraction": 0.25, "dev": [], "test": []}
    for part in sorted(written):
        fams = sorted({json.loads((OUT / FOLDERS[part] / f"{s}.json").read_text())["evaluation_only"]["template_family_id"]
                       for s in written[part]})
        rng.shuffle(fams)
        k = max(1, round(len(fams) * split["dev_fraction"]))
        for p_ids, fam_list in ((split["dev"], fams[:k]), (split["test"], fams[k:])):
            for s in written[part]:
                sc = json.loads((OUT / FOLDERS[part] / f"{s}.json").read_text())
                if sc["evaluation_only"]["template_family_id"] in fam_list:
                    p_ids.append(s)
    split["dev"].sort()
    split["test"].sort()
    (OUT / "draft_split_proposal.json").write_text(json.dumps(split, indent=2) + "\n")

    total = sum(len(v) for v in written.values())
    for part in sorted(written):
        print(f"{part} ({FOLDERS[part]}): {len(written[part])} scenarios")
    print(f"total {total}; proposed draft split: {len(split['dev'])} dev / {len(split['test'])} test")


if __name__ == "__main__":
    main()
