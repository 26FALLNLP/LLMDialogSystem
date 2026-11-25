"""Write the two team reports in docs/ (no API calls):

    python scripts/make_reports.py

docs/cost-estimates.md      cost of the dev and final test runs, Opus vs Sonnet vs Haiku,
                            for all budgets, budget 1 only, and --no-drafts
docs/hedged-suggestions.md  every draft where the user hedges on an assistant suggestion,
                            with what changes if the team decides hedging means "ask"
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from data.validate import candidates  # noqa: E402
from scripts.run_experiments import CORE_SYSTEMS, OUTPUT_TOKENS, estimate  # noqa: E402
from src.budget import PRICES  # noqa: E402
from src.splits import load_split  # noqa: E402

MODELS = (("Claude Opus 5.5", "claude-opus-5-5"), ("Claude Sonnet 5.5", "claude-sonnet-5-5"),
          ("Claude Haiku 5.5", "claude-haiku-5-5"))
HEDGE = re.compile(r"\b(maybe|not sure|possibly|think about|we'll see|don't know|another time|could be|"
                   r"get back)\b", re.IGNORECASE)


def usd(row, model, which):
    price = PRICES[model]
    out = row["output_central"] if which == "central" else row["output_high"]
    return row["input_tokens"] / 1e6 * price[0] + out / 1e6 * price[1]


def cost_report():
    split = load_split()
    scopes = [
        ("All budgets (0, 1, 2), main + drafts", lambda ids: ids, (0, 1, 2)),
        ("Budget 1 only, main + drafts", lambda ids: ids, (1,)),
        ("All budgets, `--no-drafts` (main's 48 only)", lambda ids: [i for i in ids if not i.startswith("BB-")], (0, 1, 2)),
        ("Budget 1 only, `--no-drafts`", lambda ids: [i for i in ids if not i.startswith("BB-")], (1,)),
    ]
    lines = ["# Cost estimates for the experiments", "",
             "**No API call has been made.** API calls are blocked by the $0 cap in `configs/budget.yaml`.", "",
             "Systems S1-S4, one run per scenario. Numbers come from `scripts/run_experiments.py`'s offline "
             "estimate: the exact request text each call would send, divided by 3.5 characters per token "
             "(roughly +/-30%), plus a guess for output tokens per call "
             f"(central / high: decision {OUTPUT_TOKENS['decision']}, summary {OUTPUT_TOKENS['summary']}, "
             f"memory extraction {OUTPUT_TOKENS['extraction']}). Call counts are upper bounds (every allowed "
             "question asked). The same output guesses are used for every model; smaller models may think "
             "less or more, so treat the Sonnet and Haiku rows as rough.", "",
             "Prices per million tokens (input / output): " + "; ".join(
                 f"{name} ${PRICES[mid][0]:.2f} / ${PRICES[mid][1]:.2f}" for name, mid in MODELS) + ".", ""]
    for title, pick, budgets in scopes:
        lines += [f"## {title}", "", "| Run | Scenarios | API calls (max) | Input tokens | "
                  + " | ".join(f"{name}" for name, _ in MODELS) + " |",
                  "|---|---|---|---|" + "---|" * len(MODELS)]
        for run, ids in (("Dev", sorted(split.dev)), ("Final test", sorted(split.test))):
            ids = pick(ids)
            per = estimate(ids, CORE_SYSTEMS, 1, budgets=budgets)
            total = {k: sum(r[k] for r in per.values()) for k in ("calls", "input_tokens", "output_central", "output_high")}
            cells = [f"${usd(total, mid, 'central'):,.2f} (high ${usd(total, mid, 'high'):,.2f})" for _, mid in MODELS]
            lines.append(f"| {run} | {len(ids)} | {total['calls']:,} | {total['input_tokens']:,} | " + " | ".join(cells) + " |")
        lines.append("")
    per = estimate(sorted(split.dev), CORE_SYSTEMS, 1)
    lines += ["## Where the cost goes (dev, all budgets, Opus 5.5)", "", "| System | API calls (max) | Cost |", "|---|---|---|"]
    for system, row in per.items():
        lines.append(f"| {system.upper()} | {row['calls']:,} | ${usd(row, 'claude-opus-5-5', 'central'):,.2f} |")
    lines += ["", "S3 and S4 update their memory with one model call per conversation turn, which is why they "
              "cost the most.", "", "Regenerate this file with `python scripts/make_reports.py`.", ""]
    (ROOT / "docs" / "cost-estimates.md").write_text("\n".join(lines), encoding="utf-8")


def hedges(folder):
    out = []
    for path in sorted(folder.glob("*.json")):
        sc = json.loads(path.read_text())
        ev = sc["evaluation_only"]
        state = ev["gold_dialogue_state"]
        turns = sc["model_visible"]["dialogue_prefix"]
        for p in state["proposed_not_accepted"]:
            reply = next((t for t in turns if t["speaker"] == "user" and t["turn"] > p["turn"]), None)
            if not reply:
                continue
            kind = "hedge" if HEDGE.search(reply["text"]) else "other"
            original = dict(state["active"])
            suggested = {**state["active"], p["slot"]: p["value"]}
            keep, take = set(candidates(DB, original)), set(candidates(DB, suggested))
            out.append({"id": sc["scenario_id"], "kind": kind,
                        "suggestion": turns[p["turn"] - 1]["text"], "reply": reply["text"],
                        "slot": p["slot"], "original": original.get(p["slot"]), "suggested": p["value"],
                        "shared": sorted(keep & take), "gold_ask": ev["gold_decision"]["should_ask"]})
    return out


def hedge_report():
    rows = hedges(ROOT / "data" / "drafts" / "bhavishya" / "scenarios")
    main_rows = hedges(ROOT / "data" / "scenarios")
    lines = ["# Drafts where the user hedges on a suggestion", "",
             "**Team decision needed.** In these chats the assistant suggests a different cuisine, area or "
             "budget, and the user answers without clearly saying yes or no (\"maybe\", \"not sure\", "
             "\"possibly\", ...).", "",
             "- **Current rule (keep original):** a hedge is *not* acceptance. The original requirement stays, "
             "the suggestion is recorded as \"proposed, not accepted\", and the system should recommend "
             "without asking (`should_ask: false`). This matches the S1 prompt (\"do not infer agreement from "
             "uncertainty\") and main's XX-SUG-03A (and the archived XX-SUG-01A).",
             "- **Alternative (ask):** a hedge leaves the requirement unclear, so it becomes an unresolved item "
             "with two readings (original vs suggested). Then the system should ask **only if** no restaurant "
             "fits both readings - the last column shows what would change.", "",
             "If the team picks \"ask\", the gold labels of the rows marked *would become should-ask* must "
             "change; nothing has been changed yet.", "",
             "| Scenario | Assistant suggestion | User reply | Original -> suggested | Restaurants fitting both | If hedge = unclear |",
             "|---|---|---|---|---|---|"]

    def row(r):
        change = ("no change (a shared restaurant exists)" if r["shared"]
                  else "**would become should-ask** (no restaurant fits both)")
        return (f"| {r['id']} | {r['suggestion']} | {r['reply']} | {r['slot']}: {r['original']} -> {r['suggested']} | "
                f"{', '.join(r['shared']) or 'none'} | {change} |")

    hedged = [r for r in rows if r["kind"] == "hedge"]
    lines += [row(r) for r in hedged]
    lines += ["", f"{len(hedged)} drafts hedge; {sum(not r['shared'] for r in hedged)} of them would become should-ask "
              "under the alternative rule (they were built as suggestion traps, so the readings never overlap).", ""]
    other = [r for r in rows if r["kind"] != "hedge"]
    if other:
        lines += ["## Not a hedge, but also not an answer", "",
                  "The user ignores the suggestion and changes the subject. Under both rules the original stays.", "",
                  "| Scenario | Assistant suggestion | User reply |", "|---|---|---|"]
        lines += [f"| {r['id']} | {r['suggestion']} | {r['reply']} |" for r in other]
        lines.append("")
    if main_rows:
        lines += ["## For comparison: main's scenarios with an unaccepted suggestion", "",
                  "| Scenario | Assistant suggestion | User reply | Reply type | Original -> suggested | Restaurants fitting both |",
                  "|---|---|---|---|---|---|"]
        lines += [f"| {r['id']} | {r['suggestion']} | {r['reply']} | "
                  f"{'hedge' if r['kind'] == 'hedge' else 'clear answer'} | {r['slot']}: {r['original']} -> {r['suggested']} | "
                  f"{', '.join(r['shared']) or 'none'} |" for r in main_rows]
        lines.append("")
    lines += ["Regenerate this file with `python scripts/make_reports.py`.", ""]
    (ROOT / "docs" / "hedged-suggestions.md").write_text("\n".join(lines), encoding="utf-8")
    return hedged, other, main_rows


DB = json.loads((ROOT / "data" / "restaurants.json").read_text())

if __name__ == "__main__":
    cost_report()
    hedged, other, main_rows = hedge_report()
    print(f"docs/cost-estimates.md written; docs/hedged-suggestions.md: {len(hedged)} hedges, "
          f"{len(other)} ignored suggestions, {len(main_rows)} main scenarios for comparison")
