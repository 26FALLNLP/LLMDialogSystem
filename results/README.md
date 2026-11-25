# Experiment results

This folder is committed (not ignored). Each run of `scripts/run_experiments.py --yes-run-api`
writes one folder here: `dev-<timestamp>/` or, for the final evaluation, `test-<timestamp>/`.

Each folder holds:
- `<system>-budget-<0|1|2>.jsonl` - one dialogue record per scenario (transcript, decisions, state snapshots, usage)
- `scores.jsonl`, `summary.json` - from `python -m src.score_runs`
- `tables/summary.csv`, `figures/*.svg` - from `python scripts/make_results.py`, with 95% confidence
  intervals from a bootstrap over template families

**No experiment has been run on this branch yet.** Nothing here is a result until a folder exists.
