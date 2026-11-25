# Cost estimates for the experiments

**No API call has been made.** API calls are blocked by the $0 cap in `configs/budget.yaml`.

Systems S1-S4, one run per scenario. Numbers come from `scripts/run_experiments.py`'s offline estimate: the exact request text each call would send, divided by 3.5 characters per token (roughly +/-30%), plus a guess for output tokens per call (central / high: decision (400, 1500), summary (300, 1000), memory extraction (800, 2500)). Call counts are upper bounds (every allowed question asked). The same output guesses are used for every model; smaller models may think less or more, so treat the Sonnet and Haiku rows as rough.

Prices per million tokens (input / output): Claude Opus 5.5 $4.00 / $20.00; Claude Sonnet 5.5 $2.00 / $10.00; Claude Haiku 5.5 $0.10 / $0.50.

## All budgets (0, 1, 2), main + drafts

| Run | Scenarios | API calls (max) | Input tokens | Claude Opus 5.5 | Claude Sonnet 5.5 | Claude Haiku 5.5 |
|---|---|---|---|---|---|---|
| Dev | 52 | 3,798 | 5,887,740 | $76.21 (high $191.61) | $38.10 (high $95.81) | $1.91 (high $4.79) |
| Final test | 202 | 14,634 | 22,584,198 | $292.97 (high $737.20) | $146.48 (high $368.60) | $7.32 (high $18.43) |

## Budget 1 only, main + drafts

| Run | Scenarios | API calls (max) | Input tokens | Claude Opus 5.5 | Claude Sonnet 5.5 | Claude Haiku 5.5 |
|---|---|---|---|---|---|---|
| Dev | 52 | 1,266 | 1,947,346 | $25.34 (high $63.81) | $12.67 (high $31.90) | $0.63 (high $1.60) |
| Final test | 202 | 4,878 | 7,469,286 | $97.42 (high $245.50) | $48.71 (high $122.75) | $2.44 (high $6.14) |

## All budgets, `--no-drafts` (main's 48 only)

| Run | Scenarios | API calls (max) | Input tokens | Claude Opus 5.5 | Claude Sonnet 5.5 | Claude Haiku 5.5 |
|---|---|---|---|---|---|---|
| Dev | 8 | 576 | 886,030 | $11.51 (high $28.98) | $5.76 (high $14.49) | $0.29 (high $0.72) |
| Final test | 40 | 2,880 | 4,430,800 | $57.56 (high $144.92) | $28.78 (high $72.46) | $1.44 (high $3.62) |

## Budget 1 only, `--no-drafts`

| Run | Scenarios | API calls (max) | Input tokens | Claude Opus 5.5 | Claude Sonnet 5.5 | Claude Haiku 5.5 |
|---|---|---|---|---|---|---|
| Dev | 8 | 192 | 293,029 | $3.83 (high $9.65) | $1.91 (high $4.83) | $0.10 (high $0.24) |
| Final test | 40 | 960 | 1,465,335 | $19.14 (high $48.26) | $9.57 (high $24.13) | $0.48 (high $1.21) |

## Where the cost goes (dev, all budgets, Opus 5.5)

| System | API calls (max) | Cost |
|---|---|---|
| S1 | 312 | $6.43 |
| S2 | 624 | $8.99 |
| S3 | 1,431 | $30.92 |
| S4 | 1,431 | $29.87 |

S3 and S4 update their memory with one model call per conversation turn, which is why they cost the most.

Regenerate this file with `python scripts/make_reports.py`.
