# LLMDialogSystem

This project studies when a language model should ask a clarifying question before recommending a restaurant. It includes a dialogue pipeline, a scripted user that answers from a fixed table, and an offline scorer. The dataset contains 36 scenarios and a catalog of 40 fictional restaurants.

## Quick start

Use Python 3.11 or newer. No third-party packages or API key are needed for the two-scenario offline demo.

```sh
python3 -m src --budget 1 --output runs/demo.jsonl
python3 -m src.score_runs --input runs/demo.jsonl \
  --output runs/demo-scores.jsonl --summary runs/demo-summary.json
python3 -m unittest discover -s tests
```

The demo asks a location question in `XX-AMB-01A`. In `XX-AMB-01B`, it recommends a restaurant directly because one option satisfies both interpretations.

To run all 36 scenarios with Claude, set `ANTHROPIC_API_KEY` in your local environment, then run:

```sh
python3 -m src --strategy claude --all --budget 1 --output runs/claude-b1.jsonl
```

The question budget can be 0, 1, or 2. The CLI prints transcripts and final recommendations and saves detailed run records under the specified output path.

See the design docs for the [Dialogue Pipeline](docs/dialogue-pipeline.md), [Answer Service](docs/answer-service.md), and [Scoring Service](docs/scoring-service.md).
