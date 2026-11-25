"""Turn scored runs into a summary table and figures, with 95% confidence
intervals from a bootstrap that resamples template families (not scenarios).

    python scripts/make_results.py results/<run>/scores.jsonl

Writes next to the scores file:
    tables/summary.csv              one row per system x budget
    figures/success_by_budget.svg
    figures/unnecessary_question_rate.svg
    figures/state_accuracy.svg
Only the standard library is used (no plotting package needed).
"""

import csv
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

SEED = 6120
SAMPLES = 2000
METRICS = {
    # name: (numerator(row), denominator(row)) - ratios are pooled over runs, then bootstrapped by family
    "task_success": (lambda r: int(bool(r["task_success"])), lambda r: 1),
    "unnecessary_question_rate": (lambda r: r["question_counts"]["unnecessary"], lambda r: r["question_counts"]["judged"]),
    "state_field_accuracy": (lambda r: (r["state_metrics"] or {}).get("field_correct", 0),
                             lambda r: (r["state_metrics"] or {}).get("field_total", 0)),
    "state_exact_match": (lambda r: int(bool((r["state_metrics"] or {}).get("exact_match"))),
                          lambda r: int((r["state_metrics"] or {}).get("exact_match") is not None)),
}


def pooled(rows, metric):
    num, den = METRICS[metric]
    n, d = sum(num(r) for r in rows), sum(den(r) for r in rows)
    return (n / d if d else None), n, d


def family_ci(rows, metric, samples=SAMPLES, seed=SEED):
    """95% percentile interval, resampling template families with replacement."""
    by_family = defaultdict(list)
    for r in rows:
        by_family[r["template_family_id"]].append(r)
    families = sorted(by_family)
    if len(families) < 2:
        return None, None
    rng = random.Random(seed)
    estimates = []
    for _ in range(samples):
        picked = [row for f in rng.choices(families, k=len(families)) for row in by_family[f]]
        value, _, _ = pooled(picked, metric)
        if value is not None:
            estimates.append(value)
    if not estimates:
        return None, None
    estimates.sort()
    return estimates[int(0.025 * (len(estimates) - 1))], estimates[int(0.975 * (len(estimates) - 1))]


def summary_rows(scores):
    groups = defaultdict(list)
    for r in scores:
        groups[(r["system_id"], r["budget"])].append(r)
    out = []
    for (system, budget), rows in sorted(groups.items()):
        row = {"system_id": system, "budget": budget, "runs": len(rows),
               "families": len({r["template_family_id"] for r in rows})}
        for metric in METRICS:
            value, n, d = pooled(rows, metric)
            low, high = family_ci(rows, metric) if value is not None else (None, None)
            row.update({metric: value, f"{metric}_n": n, f"{metric}_d": d,
                        f"{metric}_ci_low": low, f"{metric}_ci_high": high})
        out.append(row)
    return out


def bar_chart_svg(rows, metric, title):
    """Grouped bars (one group per budget, one bar per system) with CI whiskers."""
    systems = sorted({r["system_id"] for r in rows})
    budgets = sorted({r["budget"] for r in rows})
    colors = ["#4C78A8", "#F58518", "#54A24B", "#B279A2", "#E45756", "#72B7B2"]
    width, height, left, bottom, top = 640, 360, 60, 50, 40
    plot_w, plot_h = width - left - 20, height - top - bottom
    group_w = plot_w / max(1, len(budgets))
    bar_w = group_w * 0.8 / max(1, len(systems))
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height + 20 * len(systems)}" '
             f'font-family="sans-serif" font-size="12">',
             f'<text x="{width / 2}" y="20" text-anchor="middle" font-size="14">{title}</text>']
    for tick in range(0, 11, 2):
        y = top + plot_h * (1 - tick / 10)
        parts.append(f'<line x1="{left}" x2="{left + plot_w}" y1="{y}" y2="{y}" stroke="#ddd"/>')
        parts.append(f'<text x="{left - 6}" y="{y + 4}" text-anchor="end">{tick / 10:.1f}</text>')
    lookup = {(r["system_id"], r["budget"]): r for r in rows}
    for gi, budget in enumerate(budgets):
        gx = left + gi * group_w + group_w * 0.1
        parts.append(f'<text x="{gx + group_w * 0.4}" y="{top + plot_h + 18}" text-anchor="middle">budget {budget}</text>')
        for si, system in enumerate(systems):
            r = lookup.get((system, budget))
            if not r or r[metric] is None:
                continue
            x = gx + si * bar_w
            h = plot_h * r[metric]
            parts.append(f'<rect x="{x:.1f}" y="{top + plot_h - h:.1f}" width="{bar_w * 0.9:.1f}" height="{h:.1f}" '
                         f'fill="{colors[si % len(colors)]}"><title>{system} budget {budget}: {r[metric]:.3f}</title></rect>')
            if r[f"{metric}_ci_low"] is not None:
                cx = x + bar_w * 0.45
                y1, y2 = top + plot_h * (1 - r[f"{metric}_ci_low"]), top + plot_h * (1 - r[f"{metric}_ci_high"])
                parts.append(f'<line x1="{cx:.1f}" x2="{cx:.1f}" y1="{y1:.1f}" y2="{y2:.1f}" stroke="black"/>')
    for si, system in enumerate(systems):
        y = height + 12 + 20 * si - 20
        parts.append(f'<rect x="{left}" y="{y}" width="12" height="12" fill="{colors[si % len(colors)]}"/>')
        parts.append(f'<text x="{left + 18}" y="{y + 10}">{system}</text>')
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def write_results(scores_path: Path) -> list[dict]:
    scores = [json.loads(line) for line in scores_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    rows = summary_rows(scores)
    out_dir = scores_path.parent
    (out_dir / "tables").mkdir(exist_ok=True)
    (out_dir / "figures").mkdir(exist_ok=True)
    with open(out_dir / "tables" / "summary.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    for metric, title in (("task_success", "Task success by question budget (95% family-bootstrap CI)"),
                          ("unnecessary_question_rate", "Unnecessary questions / judged questions"),
                          ("state_field_accuracy", "State accuracy at the checkpoint (field level)")):
        (out_dir / "figures" / f"{'success_by_budget' if metric == 'task_success' else metric}.svg").write_text(
            bar_chart_svg(rows, metric, title), encoding="utf-8")
    return rows


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    for r in write_results(Path(sys.argv[1])):
        print(r["system_id"], r["budget"], r["task_success"], (r["task_success_ci_low"], r["task_success_ci_high"]))
