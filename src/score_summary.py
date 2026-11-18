"""Aggregate offline scores and compare systems on paired template families."""

from collections import Counter, defaultdict
from collections.abc import Sequence
from itertools import combinations
from random import Random
from statistics import mean, quantiles


def _rate(numerator: int, denominator: int) -> dict:
    return {
        "numerator": numerator,
        "denominator": denominator,
        "value": numerator / denominator if denominator else None,
    }


def _binary_rate(values) -> dict:
    known = [value for value in values if value is not None]
    return _rate(sum(known), len(known))


def _summarize(scores: Sequence[dict]) -> dict:
    n_runs = len(scores)
    questions: Counter = Counter()
    for row in scores:
        questions.update(row["question_counts"])
    fully_judged = [
        row["question_counts"] for row in scores
        if row["question_counts"]["judged"] == row["question_counts"]["delivered"]
    ]
    states = [row["state_metrics"] for row in scores if row["state_metrics"] is not None]

    usage = {}
    for key in ("input_tokens", "output_tokens", "model_calls"):
        values = [row["usage"][key] for row in scores if row["usage"].get(key) is not None]
        usage[key] = {
            "total_known": sum(values) if values else None,
            "mean_known": mean(values) if values else None,
            "coverage": _rate(len(values), n_runs),
        }
    return {
        "runs": n_runs,
        "termination_counts": dict(Counter(row["termination_reason"] for row in scores)),
        "task_success": _rate(sum(row["task_success"] for row in scores), n_runs),
        "initial_action_accuracy": _binary_rate(row["initial_action_matches"] for row in scores),
        "initial_action_coverage": _rate(
            sum(row["initial_action_matches"] is not None for row in scores), n_runs
        ),
        "missed_useful_clarification": _binary_rate(
            row["missed_useful_clarification"] for row in scores
        ),
        "right_question_rate": _rate(
            sum(row.get("useful_questions", 0) for row in scores), questions["judged"]
        ),
        "all_needed_slots_clarified": _binary_rate(
            row.get("all_needed_slots_clarified") for row in scores
        ),
        "question_counts": dict(questions),
        "mean_questions_per_run": _rate(questions["delivered"], n_runs),
        "question_judgment_coverage": _rate(questions["judged"], questions["delivered"]),
        "unnecessary_question_rate": _rate(questions["unnecessary"], questions["judged"]),
        "unnecessary_questions_per_fully_judged_run": _rate(
            sum(counts["unnecessary"] for counts in fully_judged), len(fully_judged)
        ),
        "state_run_coverage": _rate(len(states), n_runs),
        "state_field_accuracy": _rate(
            sum(state["field_correct"] for state in states),
            sum(state["field_total"] for state in states),
        ),
        "exact_state_accuracy": _binary_rate(state["exact_match"] for state in states),
        "stale_requirement_rate": _binary_rate(state["stale_requirement_error"] for state in states),
        "unaccepted_suggestion_misuse_rate": _binary_rate(
            state["unaccepted_suggestion_error"] for state in states
        ),
        "usage": usage,
    }


def _compare_systems(scores: Sequence[dict], bootstrap_samples: int, seed: int) -> list[dict]:
    systems: dict[str, dict[tuple[str, int], dict]] = defaultdict(dict)
    for row in scores:
        key = row["scenario_id"], row["repeat"]
        systems[row["system_id"]][key] = row

    comparisons = []
    for a, b in combinations(sorted(systems), 2):
        group_a, group_b = systems[a], systems[b]
        by_scenario: dict[str, list[int]] = defaultdict(list)
        families = {}
        for key in sorted(group_a.keys() & group_b.keys()):
            row_a, row_b = group_a[key], group_b[key]
            scenario = row_a["scenario_id"]
            by_scenario[scenario].append(int(row_b["task_success"]) - int(row_a["task_success"]))
            families[scenario] = row_a["template_family_id"]
        if not by_scenario:
            continue
        by_family = defaultdict(list)
        for scenario, differences in by_scenario.items():
            by_family[families[scenario]].append(mean(differences))
        family_totals = [(sum(values), len(values)) for values in by_family.values()]
        estimate = sum(total for total, _ in family_totals) / len(by_scenario)
        interval = None
        if len(family_totals) > 1:
            random = Random(seed)
            estimates = []
            for _ in range(bootstrap_samples):
                sampled = random.choices(family_totals, k=len(family_totals))
                estimates.append(sum(total for total, _ in sampled) / sum(n for _, n in sampled))
            half_percentiles = quantiles(estimates, n=200, method="inclusive")
            interval = [half_percentiles[4], half_percentiles[194]]
        comparisons.append({
            "system_a": a,
            "system_b": b,
            "paired_scenarios": len(by_scenario),
            "paired_runs": sum(len(values) for values in by_scenario.values()),
            "template_families": len(family_totals),
            "success_difference_b_minus_a": estimate,
            "ci95_by_template_family": interval,
        })
    return comparisons


def summarize(
    scores: Sequence[dict], *, bootstrap_samples: int = 2000, seed: int = 6120,
) -> dict:
    """Report overall results and break them down by system, budget and scenario type."""
    if not scores:
        raise ValueError("No runs to summarize.")
    if bootstrap_samples < 2:
        raise ValueError("At least two bootstrap samples are required.")
    grouped = defaultdict(list)
    for row in scores:
        grouped[row["database_version"], row["budget"]].append(row)

    groups = []
    comparisons = []
    for (database_version, budget), rows in sorted(grouped.items()):
        metadata = {"database_version": database_version, "budget": budget}
        by_system = defaultdict(list)
        for row in rows:
            by_system[row["system_id"]].append(row)
        for system, system_rows in sorted(by_system.items()):
            by_type = defaultdict(list)
            for row in system_rows:
                by_type[row["scenario_type"]].append(row)
            groups.append({
                **metadata,
                "system_id": system,
                **_summarize(system_rows),
                "by_scenario_type": {
                    name: _summarize(type_rows) for name, type_rows in sorted(by_type.items())
                },
            })
        comparisons.extend(
            {**metadata, **comparison}
            for comparison in _compare_systems(rows, bootstrap_samples, seed)
        )
    return {
        "scorer_version": scores[0]["scorer_version"],
        "overall": _summarize(scores),
        "groups": groups,
        "comparisons": comparisons,
        "bootstrap": {"samples": bootstrap_samples, "seed": seed, "unit": "template_family"},
    }
