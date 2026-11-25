"""Readable review sheet for the converted BB- drafts, one section per ambiguity group.

Run from the repo root:
    python data/drafts/bhavishya/make_review_sheet.py
Writes data/drafts/bhavishya/review_sheet.md. Every number is read from the
scenario files (computed from data/restaurants.json by code).
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PART_NAMES = {"4a": "should-ask A/B pair", "4b": "two questions", "4c": "swapped-order twin",
              "4d": "suggestion trap / accepted control", "4e": "paraphrase", "4f": "long conversation",
              "4g": "fix of an original"}


def main():
    names = {r["restaurant_id"]: (r["name"], r["price_per_person"])
             for r in json.loads((ROOT / "data" / "restaurants.json").read_text())}
    manifest = json.loads((HERE / "dataset-manifest.json").read_text())
    report = json.loads((HERE / "conversion_report.json").read_text())

    def fmt(ids):
        return ", ".join(f"{i} {names[i][0]} (${names[i][1]})" for i in ids) or "(none)"

    out = ["# Review sheet: BB- draft scenarios (converted to the nlp-quota-v3 format)", "",
           f"{manifest['scenario_count']} scenarios in {len(manifest['groups'])} groups. Variants in a group share "
           "one chat; each -H variant has a different hidden target. Candidate sets were computed from "
           "`data/restaurants.json` by code.", "",
           "**Wording is Claude-written and must be regenerated with Qwen before final testing.**", "",
           f"Composition: {manifest['composition']}. Dropped during conversion: {report['dropped_count']} "
           "(see `conversion_report.json`).", ""]
    for g in manifest["groups"]:
        scs = [json.loads((HERE / "scenarios" / f"{s}.json").read_text()) for s in g["scenario_ids"]]
        first = scs[0]
        e = first["evaluation_only"]
        info = e["draft_info"]
        st = e["gold_dialogue_state"]
        d = e["gold_decision"]
        out.append(f"---\n\n## {g['group_id']}  ({e['scenario_type']}; {PART_NAMES.get(info.get('draft_part'), '')}; "
                   f"family {e['template_family_id']})\n")
        if info.get("fix_note"):
            out.append(f"**Fix of {info.get('fix_of')}:** {info['fix_note']}\n")
        out.append(f"*Contrast:* {e['contrast_note']}\n")
        out.append("| # | Speaker | Text | Planned act |\n|---|---|---|---|")
        for t, pl in zip(first["model_visible"]["dialogue_prefix"], e["turn_plan"]):
            out.append(f"| {t['turn']} | {t['speaker']} | {t['text']} | {pl['act']} |")
        out.append(f"\n**Gold active state:** `{json.dumps(st['active'])}`  ")
        if st["superseded"]:
            out.append(f"**Superseded:** `{json.dumps(st['superseded'])}`  ")
        if st["proposed_not_accepted"]:
            out.append(f"**Proposed, not accepted:** `{json.dumps(st['proposed_not_accepted'])}`  ")
        for u in st["unresolved"]:
            out.append(f"**Unresolved:** '{u['expression']}' (turn {u['turn']}, slot {u['slot']})  ")
        if st["unresolved"]:
            out.append("**Candidates per meaning:**  ")
            for x in e["computed_by_validator"]["interpretation_sets"]:
                out.append(f"&nbsp;&nbsp;- `{json.dumps(x['interpretation'])}` -> {fmt(x['candidates'])}  ")
        ask = ("YES - " + ", ".join(d.get("necessary_questions") or [d["necessary_question"]])) if d["should_ask"] else "no"
        out.append(f"**Should ask:** {ask}  ")
        out.append(f"**Questions needed:** {len(g['required_slots'])}  ")
        out.append(f"**Safe without asking:** {fmt(e['computed_by_validator']['valid_without_clarification'])}  ")
        if info.get("forgetting_trap"):
            out.append(f"**Wrong if the early detail is forgotten:** {fmt(info['forgetting_trap'])}  ")
        if e["gold_relation_links"]:
            out.append("**Relations:** " + "; ".join(f"t{r['source_turn']} {r['relation']} t{r['target_turn']} ({r['slot']})"
                                                     for r in e["gold_relation_links"]) + "  ")
        out.append("\n| Scenario | Hidden goal | Scripted answers | Correct restaurants | Original draft label? |\n|---|---|---|---|---|")
        for sc in scs:
            ev = sc["evaluation_only"]
            answers = "; ".join(f"{s}: {ev['predefined_clarification_answers'][s]}" for s in g["required_slots"]) or "-"
            out.append(f"| {sc['scenario_id']} | `{json.dumps(ev['hidden_user_goal'])}` | {answers} | "
                       f"{fmt(ev['computed_by_validator']['success_set'])} | "
                       f"{'yes' if ev['draft_info'].get('original_hidden_goal') else 'added target'} |")
        out.append("\n- [ ] Answer keys correct  - [ ] No hint gives the answer away  - [ ] Text matches plan  "
                   "- [ ] Natural wording\n")
    (HERE / "review_sheet.md").write_text("\n".join(out) + "\n")
    print(f"review_sheet.md written ({len(manifest['groups'])} groups, {manifest['scenario_count']} scenarios)")


if __name__ == "__main__":
    main()
