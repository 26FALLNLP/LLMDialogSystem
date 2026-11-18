"""Guessability test: Claude with ZERO questions allowed on every should-ask
scenario in the dev split (original dev + proposed draft dev).

On a truly ambiguous scenario a model that cannot ask should be right about
half the time or less (1/number of readings). Much higher means the chat gives
the answer away. Results are also shown for each swapped-order twin pair:
  both right  -> the model may be following position (first/last mentioned)
  one right   -> the model may prefer one option (e.g. always "station")
  none right  -> consistently picks the other reading

DRY RUN BY DEFAULT: prints the number of calls, estimated tokens and cost,
and exits. Nothing is sent to the API unless --yes-run-api is given.

  python scripts/guessability.py                        # estimate only
  python scripts/guessability.py --yes-run-api          # real run (needs ANTHROPIC_API_KEY)
"""

import argparse
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.experiment_common import (DEFAULT_MODEL, EXTRA_TOKENS_PER_FOLLOW_UP, ROOT, gold,  # noqa: E402,F401
                                       print_estimate, request_tokens, should_ask_dev_ids)

VARIANTS = ("rule_given", "plain")


def plan(repeats, variants):
    ids = should_ask_dev_ids()
    tokens = {v: request_tokens(ids, v, budget=0) for v in variants}
    calls = len(ids) * repeats * len(variants)          # budget 0 -> exactly one call per run
    input_tokens = sum(sum(t.values()) for t in tokens.values()) * repeats
    return ids, calls, input_tokens


def chance(scenario_id):
    unresolved = gold(scenario_id)["gold_dialogue_state"]["unresolved"]
    n = 1
    for u in unresolved:
        n *= len(u["interpretations"])
    return 1 / n


def analyse(results):
    """results: list of dicts with scenario_id, variant, correct."""
    report = {}
    for variant in sorted({r["variant"] for r in results}):
        rows = [r for r in results if r["variant"] == variant]
        by_id = defaultdict(list)
        for r in rows:
            by_id[r["scenario_id"]].append(r["correct"])
        acc = {sid: sum(v) / len(v) for sid, v in by_id.items()}
        twins = {}
        for sid in by_id:
            v = gold(sid)["variant"]
            if v == "A":
                twin = f"{sid}-SW"
                if twin in by_id:
                    a, b = acc[sid], acc[twin]
                    pattern = "both right" if a > .5 and b > .5 else "none right" if a < .5 and b < .5 else "one right"
                    twins[gold(sid)["template_family_id"]] = {"original": a, "swapped": b, "pattern": pattern}
        report[variant] = {
            "runs": len(rows),
            "accuracy": sum(r["correct"] for r in rows) / len(rows),
            "chance": sum(chance(r["scenario_id"]) for r in rows) / len(rows),
            "per_scenario": acc,
            "twin_pairs": twins,
            "guessable_scenarios": sorted(sid for sid, a in acc.items() if a > chance(sid) + 0.25),
        }
    return report


def run(ids, repeats, variants, model, out_dir):
    from src.claude_client import ClaudeClient
    from src.claude_strategy import ClaudeStrategy
    from src.data import load_dataset
    from src.dialogue_pipeline import run_dialogue
    from src.scoring_service import score

    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("Set ANTHROPIC_API_KEY in your environment first.")
    client = ClaudeClient(api_key, model)
    dataset = load_dataset(ids)
    out_dir.mkdir(parents=True, exist_ok=True)
    results = []
    with open(out_dir / "guessability_runs.jsonl", "w", encoding="utf-8") as f:
        for variant in variants:
            strategy = ClaudeStrategy(client, variant)
            for rep in range(1, repeats + 1):
                for sid in ids:
                    sc = dataset.scenarios[sid]
                    record = run_dialogue(sc, strategy, dataset.answer_service, 0, repeat=rep,
                                          strategy_config={"model": model, "prompt_variant": variant})
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")
                    s = score(record, {**gold(sid), "scenario_id": sid}, sc.restaurants)
                    results.append({"scenario_id": sid, "variant": variant, "repeat": rep,
                                    "correct": bool(s["task_success"]), "restaurant_id": s["restaurant_id"]})
    report = analyse(results)
    (out_dir / "guessability_report.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repeats", type=int, default=3, help="Runs per scenario (the model is not deterministic).")
    ap.add_argument("--variants", nargs="+", choices=VARIANTS, default=list(VARIANTS))
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--out-dir", type=Path, default=ROOT / "runs" / "guessability")
    ap.add_argument("--yes-run-api", action="store_true", help="Actually call the API (costs money).")
    args = ap.parse_args(argv)
    ids, calls, input_tokens = plan(args.repeats, args.variants)
    twins = sum(1 for i in ids if gold(i)["variant"] == "A" and f"{i}-SW" in ids)
    print(f"Should-ask dev scenarios: {len(ids)} ({sum(i.startswith('XX-') for i in ids)} original, "
          f"{sum(i.startswith('BB-') for i in ids)} draft); swapped twin pairs: {twins}")
    print_estimate("Guessability (budget 0)", calls, input_tokens, args.model,
                   [f"{args.repeats} repeats x {len(args.variants)} prompt variants", "one call per run (no questions)"])
    if not args.yes_run_api:
        print("\nDRY RUN - no API call made. Re-run with --yes-run-api after approval.")
        return {"ids": ids, "calls": calls, "input_tokens": input_tokens}
    report = run(ids, args.repeats, args.variants, args.model, args.out_dir)
    for variant, r in report.items():
        print(f"{variant}: accuracy {r['accuracy']:.0%} (chance {r['chance']:.0%}) over {r['runs']} runs")
        for fam, t in sorted(r["twin_pairs"].items()):
            print(f"   {fam}: original {t['original']:.0%}, swapped {t['swapped']:.0%} -> {t['pattern']}")
    return report


if __name__ == "__main__":
    main()
