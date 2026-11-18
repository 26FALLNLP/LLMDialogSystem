"""Render every draft scenario as a readable page for checking answer keys by hand.

Run from the repo root:
    python data/drafts/bhavishya/make_review_sheet.py
Writes data/drafts/bhavishya/review_sheet.md. All numbers come from the files
(computed_by_validator), which the generator filled in from the database.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PARTS = [("4a", "should_ask_pairs", "Should-ask A/B pairs"),
         ("4c", "swapped_twins", "Swapped-order twins"),
         ("4e", "paraphrases", "Paraphrase versions"),
         ("4b", "two_question", "Two-question scenarios"),
         ("4d", "suggestion_traps", "Suggestion traps (with accepted controls)"),
         ("4f", "long_dialogues", "Long conversations"),
         ("4g", "fixes", "Fixed versions of guessable originals")]


def main():
    names = {r["restaurant_id"]: (r["name"], r["price_per_person"])
             for r in json.loads((ROOT / "data" / "restaurants.json").read_text())}

    def fmt(ids):
        return ", ".join(f"{i} {names[i][0]} (${names[i][1]})" for i in ids) or "(none)"

    out = ["# Draft review sheet (Bhavishya, BB-)", "",
           "Every draft scenario with its chat plan, hidden goal, candidate restaurants per meaning, "
           "ask decision and number of questions needed. All sets were computed from "
           "`data/restaurants.json` by code. Tick the boxes after checking each answer key by hand.", "",
           "Wording is a Claude draft and must be regenerated with Qwen before testing.", ""]
    counts = []
    for part, folder, title in PARTS:
        files = sorted((HERE / folder).glob("*.json"))
        counts.append(f"- {part} {title}: {len(files)} scenarios (`{folder}/`)")
    out += ["## Contents", ""] + counts + [""]
    for part, folder, title in PARTS:
        out += [f"# {part}: {title}", ""]
        for p in sorted((HERE / folder).glob("*.json")):
            s = json.loads(p.read_text())
            e = s["evaluation_only"]
            c = e["computed_by_validator"]
            st = e["gold_dialogue_state"]
            d = e["gold_decision"]
            out.append(f"---\n\n## {s['scenario_id']}  ({e['scenario_type']}, family {e['template_family_id']}, "
                       f"variant {e['variant']})\n")
            if e.get("fix_of"):
                out.append(f"**Fix of:** {e['fix_of']}  \n**What was removed:** {e['fix_note']}\n")
            out.append(f"*Contrast:* {e['contrast_note']}\n")
            out.append("| # | Speaker | Text | Planned act |\n|---|---|---|---|")
            for t, pl in zip(s["model_visible"]["dialogue_prefix"], e["turn_plan"]):
                out.append(f"| {t['turn']} | {t['speaker']} | {t['text']} | {pl['act']} |")
            out.append(f"\n**Hidden goal:** `{json.dumps(e['hidden_user_goal'])}`  ")
            out.append(f"**Gold active state:** `{json.dumps(st['active'])}`  ")
            if st["superseded"]:
                out.append(f"**Superseded:** `{json.dumps(st['superseded'])}`  ")
            if st["proposed_not_accepted"]:
                out.append(f"**Proposed, not accepted:** `{json.dumps(st['proposed_not_accepted'])}`  ")
            for u in st["unresolved"]:
                out.append(f"**Unresolved:** '{u['expression']}' (turn {u['turn']}, slot {u['slot']})  ")
            if st["unresolved"]:
                out.append("**Candidates per meaning:**  ")
                for x in c["interpretation_sets"]:
                    out.append(f"&nbsp;&nbsp;- `{json.dumps(x['interpretation'])}` -> {fmt(x['candidates'])}  ")
                if e.get("mention_order"):
                    out.append(f"**Mention order in the chat:** `{json.dumps(e['mention_order'])}`  ")
            ask = "YES - " + ", ".join(d.get("necessary_questions") or [d["necessary_question"]]) if d["should_ask"] else "no"
            out.append(f"**Should ask:** {ask}  ")
            out.append(f"**Questions needed:** {c['questions_needed']}  ")
            out.append(f"**Successful recommendations:** {fmt(c['success_set'])}  ")
            out.append(f"**Safe without asking:** {fmt(c['valid_without_clarification'])}  ")
            if e.get("forgetting_trap"):
                out.append(f"**Wrong if the early detail is forgotten:** {fmt(e['forgetting_trap'])}  ")
            if e["gold_relation_links"]:
                out.append("**Relations:** " + "; ".join(
                    f"t{r['source_turn']} {r['relation']} t{r['target_turn']} ({r['slot']})"
                    for r in e["gold_relation_links"]) + "  ")
            out.append("\n- [ ] Answer key correct  - [ ] No hint gives the answer away  "
                       "- [ ] Text matches plan  - [ ] Natural wording\n")
    (HERE / "review_sheet.md").write_text("\n".join(out) + "\n")
    print(f"review_sheet.md written ({sum(line.count('## BB-') for line in out)} scenarios)")


if __name__ == "__main__":
    main()
