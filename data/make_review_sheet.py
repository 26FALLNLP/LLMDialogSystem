"""Renders every scenario as a readable page for the human check (step 9)."""
import json, glob
names = {r["restaurant_id"]: r["name"] for r in json.load(open("restaurants.json"))}
fmt = lambda ids: ", ".join(f"{i} {names[i]}" for i in ids) or "(none)"
out = ["# Scenario review sheet\n", "Tick each box after reading the dialogue against its plan.\n"]
for p in sorted(glob.glob("scenarios/*.json")):
    s = json.load(open(p)); e = s["evaluation_only"]; c = e["computed_by_validator"]
    st = e["gold_dialogue_state"]
    out.append(f"\n---\n\n## {s['scenario_id']}  ({e['scenario_type']}, variant {e['variant']})\n")
    out.append(f"*Contrast:* {e['contrast_note']}\n")
    out.append("| # | Speaker | Text | Planned act |\n|---|---|---|---|")
    for t, pl in zip(s["model_visible"]["dialogue_prefix"], e["turn_plan"]):
        out.append(f"| {t['turn']} | {t['speaker']} | {t['text']} | {pl['act']} |")
    out.append(f"\n**Hidden goal:** `{json.dumps(e['hidden_user_goal'])}`  ")
    out.append(f"**Gold active state:** `{json.dumps(st['active'])}`  ")
    if st["superseded"]: out.append(f"**Superseded:** `{json.dumps(st['superseded'])}`  ")
    if st["proposed_not_accepted"]: out.append(f"**Proposed, not accepted:** `{json.dumps(st['proposed_not_accepted'])}`  ")
    if st["unresolved"]:
        u = st["unresolved"][0]
        out.append(f"**Unresolved:** '{u['expression']}' (turn {u['turn']})  ")
        for x in c["interpretation_sets"]:
            out.append(f"&nbsp;&nbsp;- {json.dumps(x['interpretation'])} -> {fmt(x['candidates'])}  ")
    out.append(f"**Should ask:** {'YES - ' + e['gold_decision']['necessary_question'] if e['gold_decision']['should_ask'] else 'no'}  ")
    out.append(f"**Successful recommendations:** {fmt(c['success_set'])}  ")
    out.append(f"**Safe without asking:** {fmt(c['valid_without_clarification'])}  ")
    if e["gold_relation_links"]:
        out.append("**Relations:** " + "; ".join(f"t{r['source_turn']} {r['relation']} t{r['target_turn']} ({r['slot']})" for r in e["gold_relation_links"]) + "  ")
    for f in e["flags_for_team"]: out.append(f"\n> FLAG: {f}")
    out.append("\n- [ ] Text matches plan  - [ ] No extra details  - [ ] No spoilers  - [ ] Only one tricky thing")
open("review_sheet.md", "w").write("\n".join(out))
print("review_sheet.md written")
