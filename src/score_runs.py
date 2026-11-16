"""Score Dialogue Pipeline JSONL files against the archived scenario annotations."""

import argparse
import json
from collections import defaultdict
from collections.abc import Sequence
from dataclasses import asdict
from pathlib import Path

from .data import DATA_DIR, load_dataset
from .score_summary import summarize
from .scoring_service import score


def score_records(records: Sequence[dict], data_dir: Path = DATA_DIR) -> list[dict]:
    """Match each recorded data version to its original scenario batch before scoring."""
    if not records:
        raise ValueError("No run records were supplied.")
    data_dir = Path(data_dir)
    run_ids = set()
    batches = defaultdict(list)
    for record in records:
        if not isinstance(record, dict) or record.get("schema_version") != 1:
            raise ValueError("Expected a Dialogue Pipeline record with schema_version 1.")
        run_id = record["run_id"]
        if run_id in run_ids:
            raise ValueError(f"Duplicate run ID: {run_id}")
        run_ids.add(run_id)
        batches[record["config"]["data_version"]].append(record)

    scored = {}
    for data_version, batch in batches.items():
        scenario_ids = sorted({record["scenario_id"] for record in batch})
        dataset = load_dataset(scenario_ids, data_dir)
        if dataset.data_version != data_version:
            raise ValueError(
                "Scenario files do not match the run's data version. "
                "Supply the original data and the full scenario batch."
            )
        gold_by_id = {}
        for scenario_id in scenario_ids:
            path = data_dir / "scenarios" / f"{scenario_id}.json"
            gold_by_id[scenario_id] = {
                **json.loads(path.read_bytes())["evaluation_only"],
                "scenario_id": scenario_id,
            }
        for record in batch:
            scenario_id = record["scenario_id"]
            scenario = dataset.scenarios[scenario_id]
            if record["config"]["database_version"] != dataset.database_version:
                raise ValueError(f"{record['run_id']}: restaurant database version mismatch.")
            original_prefix = [asdict(turn) for turn in scenario.turns]
            if record["turns"][:len(original_prefix)] != original_prefix:
                raise ValueError(f"{record['run_id']}: dialogue prefix differs from the scenario.")
            result = score(record, gold_by_id[scenario_id], scenario.restaurants)
            scored[record["run_id"]] = {
                **result,
                "data_version": data_version,
                "database_version": dataset.database_version,
            }
    return [scored[record["run_id"]] for record in records]


def _read_records(paths: Sequence[Path]) -> list[dict]:
    records = []
    for path in paths:
        with path.open(encoding="utf-8") as source:
            for line_number, line in enumerate(source, 1):
                if line.strip():
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError as exc:
                        raise ValueError(f"{path}:{line_number}: {exc.msg}") from exc
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, action="append", required=True, help="Run JSONL file. Repeat to score multiple batches.")
    parser.add_argument("--output", type=Path, required=True, help="Per-run scores JSONL.")
    parser.add_argument("--summary", type=Path, required=True, help="Aggregate metrics JSON.")
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR)
    parser.add_argument("--bootstrap-samples", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=6120)
    args = parser.parse_args()
    input_paths = {path.resolve() for path in args.input}
    outputs = {path.resolve() for path in (args.output, args.summary)}
    if len(outputs) != 2 or input_paths & outputs:
        parser.error("The two output paths must be distinct and separate from input files.")

    try:
        scores = score_records(_read_records(args.input), args.data_dir)
        summary = summarize(scores, bootstrap_samples=args.bootstrap_samples, seed=args.seed)
        for path in (args.output, args.summary):
            path.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in scores),
            encoding="utf-8",
        )
        args.summary.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(2, f"Could not score runs: {exc}\n")

    success = summary["overall"]["task_success"]
    print(f"Scored {len(scores)} runs; {success['numerator']}/{success['denominator']} recommendations meet the hidden goal.")
    print(f"Scores: {args.output}\nSummary: {args.summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
