"""Run archived restaurant scenarios and export their transcripts."""

import argparse
import json
import os
from pathlib import Path

from .claude_client import API_VERSION, DEFAULT_MODEL, EFFORT, ClaudeClient
from .claude_strategy import PROMPT_VERSION, ClaudeStrategy
from .data import DATA_DIR, load_dataset
from .demo_strategy import DemoStrategy
from .dialogue_pipeline import run_dialogue


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    scenarios = parser.add_mutually_exclusive_group()
    scenarios.add_argument("--scenario", action="append", help="Scenario ID. May be supplied more than once.")
    scenarios.add_argument("--all", action="store_true", help="Run every local scenario.")
    parser.add_argument("--budget", type=int, choices=(0, 1, 2), default=1)
    parser.add_argument("--strategy", choices=("demo", "claude"), default="demo")
    parser.add_argument("--model", help="Override the Claude model ID.")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    if args.strategy == "demo" and args.model is not None:
        parser.error("--model requires --strategy claude.")

    client = None
    strategy_config = None
    if args.strategy == "claude":
        api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
        if not api_key:
            parser.error("Set ANTHROPIC_API_KEY in your local environment to run Claude.")
        model = args.model if args.model is not None else os.environ.get("ANTHROPIC_MODEL", DEFAULT_MODEL)
        model = model.strip()
        if not model:
            parser.error("The Claude model ID must not be blank.")
        try:
            client = ClaudeClient(api_key, model)
        except ValueError as exc:
            parser.error(str(exc))
        strategy_config = {
            "provider": "anthropic",
            "model": client.model,
            "api_version": API_VERSION,
            "prompt_version": PROMPT_VERSION,
            "max_output_tokens": client.max_tokens,
            "effort": EFFORT,
        }

    if args.all:
        scenario_ids = sorted(path.stem for path in (DATA_DIR / "scenarios").glob("*.json"))
    else:
        scenario_ids = list(dict.fromkeys(args.scenario or ["XX-AMB-01A", "XX-AMB-01B"]))
    try:
        dataset = load_dataset(scenario_ids)
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(2, f"Could not load the scenario data: {exc}\n")

    records = [
        run_dialogue(
            dataset.scenarios[scenario_id],
            ClaudeStrategy(client) if client is not None else DemoStrategy(),
            dataset.answer_service,
            args.budget,
            strategy_config=strategy_config,
        )
        for scenario_id in scenario_ids
    ]
    default_output = Path("runs/amb-01.jsonl")
    if client is not None:
        default_output = Path("runs/all-claude.jsonl" if args.all else "runs/amb-01-claude.jsonl")
    output_path = args.output or default_output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records),
        encoding="utf-8",
    )

    for record in records:
        print(f"{record['scenario_id']} (question budget: {record['budget']})")
        for turn in record["turns"]:
            print(f"  {turn['turn_id']} {turn['role']}: {turn['text']}")
        delivered = sum(len(step["delivered_questions"]) for step in record["steps"])
        recommendation = record["final_recommendation"]
        print(f"  Questions delivered: {delivered}")
        if recommendation:
            print(f"  Final recommendation: {recommendation['restaurant_id']}")
        print(f"  Termination: {record['termination_reason']}\n")

    print(f"JSONL: {output_path}")
    return int(any(record["termination_reason"] != "completed" for record in records))


if __name__ == "__main__":
    raise SystemExit(main())
