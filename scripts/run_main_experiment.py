"""Main experiment: every system x question budget 0/1/2 on the DEV split
(original dev + proposed draft dev), then score everything together.

Systems: Claude with the rule-given prompt and Claude with the plain prompt.
(The rule-based demo only handles two sample dialogues, so it is left out.)

DRY RUN BY DEFAULT: prints the number of calls, estimated tokens and cost,
plus the exact commands, and exits. Nothing is sent to the API unless
--yes-run-api is given. The test split is never used here.

  python scripts/run_main_experiment.py                 # estimate only
  python scripts/run_main_experiment.py --yes-run-api   # real run (needs ANTHROPIC_API_KEY)
"""

import argparse
import shlex
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.experiment_common import (DEFAULT_MODEL, EXTRA_TOKENS_PER_FOLLOW_UP, ROOT, dev_ids,  # noqa: E402
                                       print_estimate, request_tokens)

SYSTEMS = ("rule_given", "plain")
BUDGETS = (0, 1, 2)


def plan(systems=SYSTEMS, budgets=BUDGETS):
    ids = dev_ids(include_drafts=True)
    calls = input_tokens = 0
    for system in systems:
        for budget in budgets:
            first = request_tokens(ids, system, budget)
            max_calls = budget + 1          # each delivered question leads to one more decision
            calls += len(ids) * max_calls
            for k in range(max_calls):
                input_tokens += sum(first.values()) + len(ids) * k * EXTRA_TOKENS_PER_FOLLOW_UP
    return ids, calls, input_tokens


def commands(run_dir, model, systems=SYSTEMS, budgets=BUDGETS):
    cmds, outputs = [], []
    for system in systems:
        for budget in budgets:
            out = run_dir / f"{system}-budget-{budget}.jsonl"
            outputs.append(out)
            cmds.append([sys.executable, "-m", "src", "--strategy", "claude", "--model", model,
                         "--prompt-variant", system, "--all", "--drafts", "--budget", str(budget),
                         "--output", str(out)])
    score = [sys.executable, "-m", "src.score_runs"]
    for out in outputs:
        score += ["--input", str(out)]
    score += ["--output", str(run_dir / "scores.jsonl"), "--summary", str(run_dir / "summary.json")]
    return cmds, score


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--systems", nargs="+", choices=SYSTEMS, default=list(SYSTEMS))
    ap.add_argument("--run-dir", type=Path, default=None)
    ap.add_argument("--yes-run-api", action="store_true", help="Actually call the API (costs money).")
    args = ap.parse_args(argv)
    ids, calls, input_tokens = plan(args.systems)
    print(f"Dev scenarios: {len(ids)} ({sum(i.startswith('XX-') for i in ids)} original, "
          f"{sum(i.startswith('BB-') for i in ids)} draft)")
    print_estimate("Main experiment (systems x budgets 0/1/2, dev)", calls, input_tokens, args.model,
                   [f"{len(args.systems)} systems x budgets {BUDGETS}",
                    "upper bound: assumes every allowed question is asked; real runs use fewer calls"])
    run_dir = args.run_dir or ROOT / "runs" / f"main-dev-{time.strftime('%Y%m%d-%H%M%S')}"
    cmds, score = commands(run_dir, args.model, args.systems)
    print("\nCommands:")
    for c in cmds + [score]:
        print("  " + shlex.join(c))
    if not args.yes_run_api:
        print("\nDRY RUN - no API call made. Re-run with --yes-run-api after approval.")
        return {"ids": ids, "calls": calls, "input_tokens": input_tokens, "commands": cmds + [score]}
    run_dir.mkdir(parents=True, exist_ok=True)
    for c in cmds:
        subprocess.run(c, cwd=ROOT, check=False)   # a failed run is still recorded and scored
    subprocess.run(score, cwd=ROOT, check=True)
    print(f"Results in {run_dir}")


if __name__ == "__main__":
    main()
