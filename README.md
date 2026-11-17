# LLMDialogSystem

This project studies when a language model should ask a clarifying question before recommending a restaurant. It includes a dialogue pipeline, a scripted user that answers from a fixed table, and an offline scorer. The dataset contains 36 scenarios and a catalog of 40 fictional restaurants.

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
  --scenario XX-AMB-02A --budget 1 \
  --output runs/claude-amb-02a-b1.jsonl

python3 -m src.score_runs --input runs/claude-amb-02a-b1.jsonl \
  --output runs/claude-amb-02a-b1-scores.jsonl \
  --summary runs/claude-amb-02a-b1-summary.json
```

Use a filename stem from [data/scenarios](data/scenarios) as the scenario ID. The question budget is the maximum number of clarification questions the model can ask. If Claude asks, the scripted user replies from the scenario's fixed answer table. The runner prints the transcript and final recommendation and saves the detailed record to the output path. Running the example again replaces its previous output files.

### Compare question budgets of 0, 1, and 2

Run all 36 scenarios once at each budget with the same Claude model. Each comparison gets its own output directory under `runs/`.

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

`scores.jsonl` contains one score per run. In `summary.json`, each entry under `groups` reports recommendation success and the number of questions actually asked for one budget. If a batch exits with errors, check its `termination_counts` in the summary. The scorer counts failed runs in the denominator, so keep all 36 records from each batch.

See the design docs for the [Dialogue Pipeline](docs/dialogue-pipeline.md), [Answer Service](docs/answer-service.md), and [Scoring Service](docs/scoring-service.md).
