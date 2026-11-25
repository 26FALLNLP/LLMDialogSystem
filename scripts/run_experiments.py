"""Main experiment: systems S1-S4 (S5 optional) x question budgets 0/1/2.

DRY RUN BY DEFAULT. It prints, separately for the DEV run and the final TEST
run, the number of API calls (upper bound), estimated tokens and estimated
cost, plus the exact commands, and exits. Nothing is sent to the API unless
--yes-run-api is given. The test run additionally needs --final-test.

    python scripts/run_experiments.py                      # estimates for dev and test
    python scripts/run_experiments.py --yes-run-api        # DEV run (after approval)
    python scripts/run_experiments.py --yes-run-api --final-test   # final TEST run (after approval)

Results go to results/<split>-<timestamp>/: one JSONL per system x budget,
scores.jsonl, summary.json (from src.score_runs), tables/summary.csv and
figures/*.svg (from scripts/make_results.py). results/ is committed, not ignored.

Estimates are offline: the request text each call would send is built locally
and its characters divided by CHARS_PER_TOKEN (roughly +/-30%). Output tokens
are guesses (Claude Opus 5.5 always thinks; effort=low; thinking is billed as
output), given as a central and a high value.
"""

import argparse
import json
import shlex
import subprocess
import sys
import time
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.claude_client import DEFAULT_MODEL  # noqa: E402
from src.claude_strategy import ACTION_SCHEMA, PROMPT_VARIANTS  # noqa: E402
from src.data import load_dataset  # noqa: E402
from src.splits import load_split  # noqa: E402
from src.systems.strategies import (EXTRACT_NO_LINKS_PROMPT, EXTRACT_WITH_LINKS_PROMPT,  # noqa: E402
                                    MEMORY_NO_LINKS_SCHEMA, MEMORY_WITH_LINKS_SCHEMA, MEMORY_NOTE,
                                    SUMMARY_NOTE, SUMMARY_PROMPT, SUMMARY_SCHEMA)

CHARS_PER_TOKEN = 3.5
MEMORY_CHARS_PER_TURN = 250        # how fast the stored memory grows, per processed turn
QA_TURN_CHARS = 120                 # one question + one answer added to the context
OUTPUT_TOKENS = {                   # per call: (central, high)
    "decision": (400, 1500), "summary": (300, 1000), "extraction": (800, 2500),
}
PRICES = {"claude-opus-5-5": (4.00, 20.00), "claude-sonnet-5-5": (2.00, 10.00), "claude-haiku-5-5": (0.10, 0.50)}
BUDGETS = (0, 1, 2)
CORE_SYSTEMS = ("s1", "s2", "s3", "s4")


def tokens(chars):
    return int(chars / CHARS_PER_TOKEN + 0.999)


def scenario_calls(system, scenario, budget, variant="rule_given"):
    """Upper-bound list of (call kind, input tokens) for one run of one scenario."""
    turns = [asdict(t) for t in scenario.turns]
    catalog = [dict(r) for r in scenario.restaurants]
    decision_prompt = PROMPT_VARIANTS[variant][1]
    public = len(json.dumps({"turns": turns, "restaurant_database": catalog, "remaining_budget": budget,
                             "allowed_actions": ["ASK", "RECOMMEND"]})) + len(json.dumps(ACTION_SCHEMA))
    turn_chars = len(json.dumps(turns)) / max(1, len(turns))
    calls = []
    steps = budget + 1                       # each delivered question adds one more decision step
    if system == "s1":
        calls += [("decision", tokens(len(decision_prompt) + public + k * QA_TURN_CHARS)) for k in range(steps)]
    elif system == "s2":
        for k in range(steps):
            calls.append(("summary", tokens(len(SUMMARY_PROMPT) + len(json.dumps(turns)) + k * QA_TURN_CHARS
                                            + len(json.dumps(SUMMARY_SCHEMA)))))
            calls.append(("decision", tokens(len(decision_prompt + SUMMARY_NOTE) + public + 600 + k * QA_TURN_CHARS)))
    else:
        prompt, schema = ((EXTRACT_NO_LINKS_PROMPT, MEMORY_NO_LINKS_SCHEMA) if system == "s4"
                          else (EXTRACT_WITH_LINKS_PROMPT, MEMORY_WITH_LINKS_SCHEMA))
        total_turns = len(turns) + 2 * budget
        for i in range(1, total_turns + 1):   # one extraction call per turn, seeing the conversation so far
            calls.append(("extraction", tokens(len(prompt) + len(json.dumps(schema)) + i * turn_chars
                                               + (i - 1) * MEMORY_CHARS_PER_TURN)))
        if system == "s5":
            calls += [("decision", tokens(len(decision_prompt + MEMORY_NOTE) + public
                                          + total_turns * MEMORY_CHARS_PER_TURN * 2 + k * QA_TURN_CHARS))
                      for k in range(steps)]
    return calls


def estimate(scenario_ids, systems, reps, variant="rule_given"):
    dataset = load_dataset(sorted(scenario_ids))
    per_system = {}
    for system in systems:
        n_calls, inp, out_c, out_h = 0, 0, 0, 0
        for budget in BUDGETS:
            for sid in scenario_ids:
                for kind, t in scenario_calls(system, dataset.scenarios[sid], budget, variant):
                    n_calls += reps
                    inp += t * reps
                    out_c += OUTPUT_TOKENS[kind][0] * reps
                    out_h += OUTPUT_TOKENS[kind][1] * reps
        per_system[system] = {"calls": n_calls, "input_tokens": inp, "output_central": out_c, "output_high": out_h}
    return per_system


def cost(row, model, which):
    price = PRICES.get(model)
    if not price:
        return None
    out = row["output_central"] if which == "central" else row["output_high"]
    return round(row["input_tokens"] / 1e6 * price[0] + out / 1e6 * price[1], 2)


def print_estimate(title, ids, per_system, model):
    print(f"\n=== {title}: {len(ids)} scenarios ({sum(i.startswith('XX-') for i in ids)} main, "
          f"{sum(i.startswith('BB-') for i in ids)} drafts), budgets {BUDGETS} ===")
    total = {"calls": 0, "input_tokens": 0, "output_central": 0, "output_high": 0}
    for system, row in per_system.items():
        for k in total:
            total[k] += row[k]
        print(f"  {system}: <= {row['calls']:>6,} calls  input ~{row['input_tokens']:>11,} tok  "
              f"output ~{row['output_central']:>10,} (high {row['output_high']:,})  "
              f"-> ${cost(row, model, 'central')} (high ${cost(row, model, 'high')})")
    print(f"  TOTAL: <= {total['calls']:,} calls, input ~{total['input_tokens']:,} tok, output ~"
          f"{total['output_central']:,} tok (high {total['output_high']:,}) -> ${cost(total, model, 'central')} "
          f"(high ${cost(total, model, 'high')})")
    return total


def commands(run_dir, systems, model, final_test, variant):
    cmds, outs = [], []
    for system in systems:
        for budget in BUDGETS:
            out = run_dir / f"{system}-budget-{budget}.jsonl"
            outs.append(out)
            cmd = [sys.executable, "-m", "src", "--strategy", system, "--model", model, "--all",
                   "--budget", str(budget), "--output", str(out)]
            if system in ("s1", "s2", "s5"):
                cmd += ["--prompt-variant", variant]
            if final_test:
                cmd.append("--final-test")
            cmds.append(cmd)
    score = [sys.executable, "-m", "src.score_runs"]
    for out in outs:
        score += ["--input", str(out)]
    score += ["--output", str(run_dir / "scores.jsonl"), "--summary", str(run_dir / "summary.json")]
    report = [sys.executable, "scripts/make_results.py", str(run_dir / "scores.jsonl")]
    return cmds, score, report


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--with-s5", action="store_true", help="Also run the optional S5.")
    ap.add_argument("--reps", type=int, default=1, help="Runs per scenario (same for every system).")
    ap.add_argument("--prompt-variant", choices=sorted(PROMPT_VARIANTS), default="rule_given")
    ap.add_argument("--final-test", action="store_true", help="Run the TEST split (final evaluation only).")
    ap.add_argument("--yes-run-api", action="store_true", help="Actually call the API (costs money).")
    args = ap.parse_args(argv)
    systems = CORE_SYSTEMS + (("s5",) if args.with_s5 else ())
    split = load_split()
    estimates = {}
    for name, ids in (("DEV run", sorted(split.dev)), ("final TEST run", sorted(split.test))):
        per_system = estimate(ids, systems, args.reps, args.prompt_variant)
        estimates[name] = {"ids": ids, "per_system": per_system,
                           "total": print_estimate(name, ids, per_system, args.model)}
    label = "test" if args.final_test else "dev"
    run_dir = ROOT / "results" / f"{label}-{time.strftime('%Y%m%d-%H%M%S')}"
    cmds, score, report = commands(run_dir.relative_to(ROOT), systems, args.model, args.final_test,
                                   args.prompt_variant)
    print(f"\nCommands for the {label.upper()} run:")
    for c in cmds + [score, report]:
        print("  " + shlex.join(c))
    if not args.yes_run_api:
        print("\nDRY RUN - no API call made. Re-run with --yes-run-api after approval.")
        return estimates
    run_dir.mkdir(parents=True, exist_ok=True)
    for c in cmds:
        subprocess.run(c, cwd=ROOT, check=False)   # failed runs are still written and scored as failures
    subprocess.run(score, cwd=ROOT, check=True)
    subprocess.run(report, cwd=ROOT, check=True)
    print(f"Results in {run_dir}")
    return estimates


if __name__ == "__main__":
    main()
