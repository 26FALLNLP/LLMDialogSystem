"""Convert Bhavishya's BB- drafts into main's nlp-quota-v3 format.

Run from the repo root:
    python data/drafts/bhavishya/convert_drafts.py [--source-ref bhavishya/complete-data-and-eval]

Reads the old drafts from the given git ref (data/drafts/bhavishya/*/*.json),
and writes:
    data/drafts/bhavishya/scenarios/*.json        converted scenarios
    data/drafts/bhavishya/dataset-manifest.json   groups, like data/dataset-manifest.json
    data/drafts/bhavishya/conversion_report.json  what was kept / dropped and why

Main's format, as used for XX-AMB-01A/01C and XX-AMB-06A-D: every variant of
an ambiguity group shares one chat, and the variants enumerate every hidden
target. So each should-ask draft chat becomes a group with one variant per
reading (-H1, -H2, ...); the draft's own hidden goal is one of them. Its gold
labels are not changed. Chats that need no question stay single-scenario groups.

A draft chat is dropped if it duplicates a setup already in main's 48, fails
the validator, or gets a hint warning.
"""

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from data.validate import analyse, hint_report, norm  # noqa: E402

OUT = ROOT / "data" / "drafts" / "bhavishya"
DB = json.loads((ROOT / "data" / "restaurants.json").read_text())
TEXT_SOURCE = "draft by Claude; wording to be regenerated with Qwen before testing"
MAIN_KEYS = ("scenario_type", "template_family_id", "variant", "contrast_note", "turn_plan",
             "hidden_user_goal", "predefined_clarification_answers", "gold_dialogue_state",
             "gold_relation_links", "gold_decision", "flags_for_team")
DRAFT_INFO_KEYS = ("draft_part", "ambiguity_kind", "mention_order", "single_change", "suggestion_trap",
                   "key_detail_turn", "forgetting_trap", "fix_of", "fix_note")


def git_drafts(ref):
    names = subprocess.run(["git", "ls-tree", "-r", "--name-only", ref, "data/drafts/bhavishya/"],
                           cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
    out = []
    for name in sorted(names):
        if not name.endswith(".json") or name.count("/") != 4:
            continue  # only data/drafts/bhavishya/<part>/<id>.json
        sc = json.loads(subprocess.run(["git", "show", f"{ref}:{name}"], cwd=ROOT,
                                       capture_output=True, text=True, check=True).stdout)
        if "scenario_id" in sc and "evaluation_only" in sc:
            out.append(sc)
    return out


def setup_signature(sc):
    """Same constraints and same readings = same setup, whatever the wording."""
    st = sc["evaluation_only"]["gold_dialogue_state"]
    readings = tuple(sorted(json.dumps(sorted(json.dumps(i, sort_keys=True) for i in u["interpretations"]))
                            for u in st["unresolved"]))
    history = tuple(sorted(json.dumps([section, item["slot"], item.get("value")])
                           for section in ("superseded", "proposed_not_accepted") for item in st[section]))
    return (json.dumps(norm(st["active"]), sort_keys=True), readings, history,
            sc["evaluation_only"]["gold_decision"]["should_ask"])


def answer_for(slot, value, template):
    if slot == "location":
        return f"Near the {value}."
    if slot == "cuisine":
        return f"{value}, please."
    return template


def best_correct(worlds, slots, budget):
    """Same rule as tests/test_scenario_ambiguity.py: correct worlds with an
    optimal choice and independent-slot questions."""
    counts = Counter(r for w in worlds for r in w["candidates"])
    best = max(counts.values(), default=0)
    if budget == 0:
        return best
    for slot in slots:
        parts = defaultdict(list)
        for w in worlds:
            parts[w["answers"][slot]].append(w)
        rest = tuple(s for s in slots if s != slot)
        best = max(best, sum(best_correct(p, rest, budget - 1) for p in parts.values()))
    return best


def convert(src):
    """One old draft -> list of scenarios in main's format (one group)."""
    ev = src["evaluation_only"]
    st = ev["gold_dialogue_state"]
    info = {k: ev[k] for k in DRAFT_INFO_KEYS if k in ev}
    info["converted_from"] = src["scenario_id"]
    decision = dict(ev["gold_decision"])
    if decision.get("necessary_questions"):
        decision = {"should_ask": True, "necessary_question": None, "any_other_question_is_unnecessary": True,
                    "necessary_questions": decision["necessary_questions"], "score_followup_clarifications": True}
    else:
        decision = {k: decision[k] for k in ("should_ask", "necessary_question", "any_other_question_is_unnecessary")}
    base = {
        "scenario_id": None, "author": "BB", "text_source": TEXT_SOURCE,
        "model_visible": src["model_visible"],
        "evaluation_only": None,
    }
    if not decision["should_ask"]:
        targets = [(ev["hidden_user_goal"], "")]
    else:
        targets = []
        for choice in product(*[u["interpretations"] for u in st["unresolved"]]):
            goal = dict(st["active"])
            for interp in choice:
                goal.update(interp)
            targets.append((goal, f"-H{len(targets) + 1}"))
        own = [i for i, (g, _) in enumerate(targets) if norm(g) == norm(ev["hidden_user_goal"])]
        assert len(own) == 1, src["scenario_id"]
        targets[own[0]] = (ev["hidden_user_goal"], targets[own[0]][1])  # keep the original label exactly
    out = []
    group_id = src["scenario_id"]
    for goal, suffix in targets:
        answers = dict(ev["predefined_clarification_answers"])
        for u in st["unresolved"]:
            if decision["should_ask"]:
                answers[u["slot"]] = answer_for(u["slot"], goal.get(u["slot"]), answers.get(u["slot"]))
        new_ev = {k: ev[k] for k in MAIN_KEYS if k in ev}
        new_ev.update(variant=ev["variant"] + suffix, hidden_user_goal=goal,
                      predefined_clarification_answers=answers, gold_decision=dict(decision))
        if suffix:
            new_ev["contrast_note"] = (ev["contrast_note"] + " All -H variants share this chat and enumerate "
                                       "the hidden targets (main's nlp-quota-v3 format).")
            new_ev["ambiguity_pair_id"] = f"{group_id}-hidden-target"
        sc = dict(base, scenario_id=group_id + suffix, evaluation_only=new_ev)
        computed, issues = analyse(sc, DB)
        new_ev["computed_by_validator"] = {k: computed[k] for k in
                                           ("success_set", "interpretation_sets", "shared_candidates",
                                            "valid_without_clarification") if k in computed}
        new_ev["draft_info"] = dict(info, original_hidden_goal=(suffix == "" or norm(goal) == norm(ev["hidden_user_goal"])))
        out.append((sc, issues))
    return group_id, out, sorted({u["slot"] for u in st["unresolved"]}) if decision["should_ask"] else []


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source-ref", default="bhavishya/complete-data-and-eval")
    args = ap.parse_args(argv)
    sources = git_drafts(args.source_ref)
    main48 = [json.loads(p.read_text()) for p in sorted((ROOT / "data" / "scenarios").glob("*.json"))]
    in_main = {setup_signature(sc): sc["scenario_id"] for sc in main48}
    in_drafts = {}  # setup -> (family, scenario) of the first kept draft

    kept, report = [], {"source_ref": args.source_ref, "source_scenarios": len(sources),
                        "kept_groups": [], "dropped": []}
    for src in sources:
        sig = setup_signature(src)
        family = src["evaluation_only"]["template_family_id"]
        if sig in in_main:
            report["dropped"].append({"draft": src["scenario_id"],
                                      "reason": f"duplicate of main: same setup as {in_main[sig]}"})
            continue
        if sig in in_drafts and in_drafts[sig][0] != family:
            # Swapped twins and paraphrases share a setup on purpose (same family);
            # the same setup in an unrelated family is an accidental duplicate.
            report["dropped"].append({"draft": src["scenario_id"],
                                      "reason": f"duplicate of another draft family: same setup as {in_drafts[sig][1]}"})
            continue
        group_id, members, required = convert(src)
        fails = [(sc["scenario_id"], i) for sc, issues in members for i in issues if i[0] == "FAIL"]
        if fails:
            report["dropped"].append({"draft": src["scenario_id"], "reason": f"validator FAIL {fails}"})
            continue
        _, per, _ = hint_report([sc for sc, _ in members], DB)
        if per:
            report["dropped"].append({"draft": src["scenario_id"], "reason": f"hint warning {dict(per)}"})
            continue
        in_drafts.setdefault(sig, (family, src["scenario_id"]))
        kept.append((group_id, [sc for sc, _ in members], required))
        report["kept_groups"].append(group_id)

    shutil.rmtree(OUT / "scenarios", ignore_errors=True)
    (OUT / "scenarios").mkdir(parents=True)
    groups, composition, totals = [], Counter(), {0: 0, 1: 0, 2: 0}
    for group_id, members, required in kept:
        for sc in members:
            (OUT / "scenarios" / f"{sc['scenario_id']}.json").write_text(json.dumps(sc, indent=1) + "\n")
        worlds = [{"candidates": set(sc["evaluation_only"]["computed_by_validator"]["success_set"]),
                   "answers": sc["evaluation_only"]["predefined_clarification_answers"]} for sc in members]
        possible = {b: best_correct(worlds, tuple(required), b) for b in (0, 1, 2)}
        minimum = next((b for b, c in possible.items() if c == len(worlds)), 2)
        composition[minimum] += len(members)
        for b in totals:
            totals[b] += possible[b]
        groups.append({"group_id": group_id, "scenario_ids": [sc["scenario_id"] for sc in members],
                       "required_slots": required})

    from src.data import load_dataset  # after files exist
    ids = [s for g in groups for s in g["scenario_ids"]]
    ds = load_dataset(ids)
    manifest = {
        "dataset_id": "bb-drafts-v1",
        "purpose": "Bhavishya's draft scenarios converted to the nlp-quota-v3 format; under review, not part "
                   "of the main dataset until the team approves them and the wording is regenerated with Qwen.",
        "scenario_count": len(ids), "catalog_count": len(DB),
        "composition": {"zero_question": composition[0], "one_question": composition[1],
                        "two_question": composition[2]},
        "idealized_expected_correct": {str(b): c for b, c in totals.items()},
        "expectation_assumptions": "Same rule as data/dataset-manifest.json: uniform hidden goals, optimal "
                                   "independent-slot questions. Design expectations, not measured results.",
        "data_version": ds.data_version, "database_version": ds.database_version,
        "groups": groups,
    }
    (OUT / "dataset-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    reasons = Counter(d["reason"].split(":")[0].split(" [")[0].split(" {")[0] for d in report["dropped"])
    report.update(kept_scenarios=len(ids), dropped_count=len(report["dropped"]), dropped_by_reason=dict(reasons))
    (OUT / "conversion_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"source drafts {len(sources)} -> kept {len(kept)} chats as {len(ids)} scenarios; "
          f"dropped {len(report['dropped'])}: {dict(reasons)}")
    print("composition", manifest["composition"], "idealized", manifest["idealized_expected_correct"])
    return report


if __name__ == "__main__":
    main()
