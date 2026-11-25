# LLMDialogSystem

This project studies when a language model should ask a clarifying question before recommending a restaurant. It includes a dialogue pipeline, a scripted user that answers from a fixed table, and an offline scorer. The current dataset contains 48 scenarios and a catalog of 40 fictional restaurants.

## Quick start

Use Python 3.11 or newer. Run all commands from the repository root. If you need a local checkout, clone the repository first.

```sh
git clone https://github.com/26FALLNLP/LLMDialogSystem.git
cd LLMDialogSystem
```

The two-scenario offline demo needs no third-party packages or API key.

```sh
python3 -m src --budget 1 --output runs/demo.jsonl
python3 -m src.score_runs --input runs/demo.jsonl \
  --output runs/demo-scores.jsonl --summary runs/demo-summary.json
python3 -m unittest discover -s tests
```

The demo asks a location question in `XX-AMB-01A`. In `XX-AMB-01B`, it recommends a restaurant directly because one option satisfies both interpretations.

## Run Claude manually

### Set your API key

Run this block in Bash or Zsh. Paste your Anthropic API key at the prompt and press Enter. The terminal hides the input. Use the same terminal for the commands below.

```sh
{
  printf 'Anthropic API key: '
  read -r -s ANTHROPIC_API_KEY && export ANTHROPIC_API_KEY
  printf '\n'
}
```

### Run and score one scenario

```sh
python3 -m src --strategy claude --model claude-opus-5-5 \
  --scenario XX-AMB-06A --budget 1 \
  --output runs/claude-amb-06a-b1.jsonl

python3 -m src.score_runs --input runs/claude-amb-06a-b1.jsonl \
  --output runs/claude-amb-06a-b1-scores.jsonl \
  --summary runs/claude-amb-06a-b1-summary.json
```

Use a filename stem from [data/scenarios](data/scenarios) as the scenario ID. **Runs use the dev split only** ([data/splits/split.json](data/splits/split.json)); a test-split scenario is refused unless you add `--final-test`, which is for the final evaluation only. The question budget is the maximum number of clarification questions the model can ask. If Claude asks, the scripted user replies from the scenario's fixed answer table. The runner prints the transcript and final recommendation and saves the detailed record to the output path. Running the example again replaces its previous output files.

### Compare question budgets of 0, 1, and 2

Run every dev scenario once at each budget with the same Claude model (`--all` means the dev split, including the BB- drafts; add `--no-drafts` for main's scenarios only, and `--final-test` only for the final test-split run). Each comparison gets its own output directory under `runs/`.

```sh
mkdir -p runs
run_dir=$(mktemp -d runs/budget-comparison.XXXXXX)

for budget in 0 1 2; do
  python3 -m src --strategy claude --model claude-opus-5-5 \
    --all --budget "$budget" --output "$run_dir/budget-$budget.jsonl"
done

python3 -m src.score_runs \
  --input "$run_dir/budget-0.jsonl" \
  --input "$run_dir/budget-1.jsonl" \
  --input "$run_dir/budget-2.jsonl" \
  --output "$run_dir/scores.jsonl" \
  --summary "$run_dir/summary.json"
```

To print the budget results side by side, run this in the same terminal.

```sh
python3 - "$run_dir/summary.json" <<'PY'
import json
import sys
from pathlib import Path

summary = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
print("Budget  Correct recommendations  Questions asked")
for group in summary["groups"]:
    success = group["task_success"]
    result = f"{success['numerator']}/{success['denominator']}"
    print(f"{group['budget']:>6}  {result:>23}  {group['question_counts']['delivered']:>15}")
PY
```

`scores.jsonl` contains one score per run. In `summary.json`, each entry under `groups` reports recommendation success and the number of questions actually asked for one budget. If a batch exits with errors, check its `termination_counts` in the summary. The scorer counts failed runs in the denominator, so keep every record from each batch.

## Clarification budget dataset

The `nlp-quota-v3` revision is a synthetic diagnostic benchmark with a fixed restaurant catalog and balanced hidden targets. Histories within each ambiguity group are identical, and the hidden targets have disjoint eligible restaurant sets. The composition is specified before model evaluation in [data/dataset-manifest.json](data/dataset-manifest.json).

| Scenario group | Count | Information needed |
| --- | --- | --- |
| Clear or shared-candidate controls | 8 | Direct recommendation |
| XX-AMB-01A/C through XX-AMB-04A/C | 8 | Choose one of two interpretations |
| XX-AMB-06 through XX-AMB-11, variants A–D | 24 | Choose one of four cuisines |
| XX-AMB-12 and XX-AMB-13, variants A–D | 8 | Confirm cuisine and location independently |

With uniformly balanced hidden targets and optimal independent-slot questions, the idealized expected success counts are 20/48 at budget 0, 44/48 at budget 1, and 48/48 at budget 2. These are design expectations. Measured model results are saved with each experiment batch. This targeted composition is intended to expose the value of additional clarification opportunities.

In the two-question cases, both cuisine and location are unresolved. A cuisine reply gives only the cuisine, and a location reply gives only the location. The scorer updates the remaining candidate interpretations after each answered question and judges a second useful question against that updated state.

The model receives only the visible conversation, catalog, and run parameters. Hidden goals, variant labels, pair IDs, and answer tables are held by the evaluation and answer modules. Keep all variants of a template family in the same development or test split.

The original 36-scenario snapshot is available in `data/archive/nlp-v1/`, and the previous 40-scenario revision is in `data/archive/nlp-ambiguity-v2/`. Add `--data-dir` with the matching archive path when scoring historical logs. New runs use the revised `data/scenarios/` by default, and their data hashes distinguish them from the archived runs.

See the design docs for the [Dialogue Pipeline](docs/dialogue-pipeline.md), [Answer Service](docs/answer-service.md), and [Scoring Service](docs/scoring-service.md).
