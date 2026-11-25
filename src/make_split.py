"""Make the family-level dev/test split of the combined dataset.

    python -m src.make_split            # writes data/splits/split.json (refuses to overwrite)
    python -m src.make_split --force    # overwrite (only if the team agrees)

Combined dataset = main's scenarios (data/scenarios) + the BB- drafts
(data/drafts/*/scenarios). The unit is the template family, so every variant
of an ambiguity group (and a draft's swapped twin and paraphrases) lands on
the same side. Families are stratified by scenario type and shuffled with a
fixed seed; about DEV_FRACTION of each type's families go to dev.
"""

import argparse
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

from .data import DATA_DIR, load_dataset

SEED = 6120
DEV_FRACTION = 0.25
SPLIT_PATH = DATA_DIR / "splits" / "split.json"


def all_scenarios(data_dir: Path = DATA_DIR) -> dict[str, dict]:
    paths = sorted((data_dir / "scenarios").glob("*.json")) + sorted(data_dir.glob("drafts/*/scenarios/*.json"))
    out = {}
    for p in paths:
        sc = json.loads(p.read_text(encoding="utf-8"))
        if sc["scenario_id"] in out:
            raise ValueError(f"Duplicate scenario ID {sc['scenario_id']}")
        out[sc["scenario_id"]] = sc
    return out


def make_split(scenarios: dict[str, dict], seed: int = SEED, dev_fraction: float = DEV_FRACTION) -> dict:
    families = defaultdict(list)
    for sid, sc in scenarios.items():
        families[sc["evaluation_only"]["template_family_id"]].append(sid)
    strata = defaultdict(list)
    for fam, ids in sorted(families.items()):
        types = Counter(scenarios[s]["evaluation_only"]["scenario_type"] for s in ids)
        strata[types.most_common(1)[0][0]].append(fam)
    rng = random.Random(seed)
    dev, test, per_type = [], [], {}
    for stype in sorted(strata):
        fams = sorted(strata[stype])
        rng.shuffle(fams)
        k = int(len(fams) * dev_fraction + 0.5) if len(fams) > 1 else 0
        for fam in fams[:k]:
            dev += families[fam]
        for fam in fams[k:]:
            test += families[fam]
        per_type[stype] = {"families_dev": k, "families_test": len(fams) - k,
                           "scenarios_dev": sum(len(families[f]) for f in fams[:k]),
                           "scenarios_test": sum(len(families[f]) for f in fams[k:])}
    return {"seed": seed, "dev_fraction": dev_fraction, "unit": "template_family",
            "stratified_by": "scenario_type", "n_scenarios": len(scenarios),
            "n_dev": len(dev), "n_test": len(test), "per_type": per_type,
            "dev_families": sorted({scenarios[s]["evaluation_only"]["template_family_id"] for s in dev}),
            "dev": sorted(dev), "test": sorted(test)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=SPLIT_PATH)
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--force", action="store_true", help="Overwrite an existing split file.")
    args = ap.parse_args(argv)
    if args.out.exists() and not args.force:
        print(f"{args.out} already exists; refusing to overwrite. Use --force only if the team agrees.",
              file=sys.stderr)
        return 2
    scenarios = all_scenarios()
    split = make_split(scenarios, args.seed)
    split["data_version"] = load_dataset(sorted(scenarios)).data_version
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(split, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.out}: {split['n_dev']} dev / {split['n_test']} test scenarios")
    for stype, row in split["per_type"].items():
        print(f"  {stype}: {row}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
