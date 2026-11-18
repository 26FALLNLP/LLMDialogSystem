"""Inter-annotator agreement (Cohen's kappa) for the scenario labels.

Three commands (run from the repo root, no extra packages needed):

  # 1. Make the blank labeling sheet for a second annotator (30 scenarios, old + new, no answers)
  python scripts/annotator_agreement.py make-sheet

  # 2. Write the data author's labels (taken from the gold files) in the same format
  python scripts/annotator_agreement.py export-gold --out labels_author.csv

  # 3. Compare two label files filled in BEFORE any discussion (pre-adjudication)
  python scripts/annotator_agreement.py kappa labels_author.csv labels_teammate.csv

Label file format (CSV, one row per item):
  item          S01..S30 (from the sheet; the item -> scenario key is kept separately)
  should_ask    yes / no
  cuisine       e.g. Thai, or Thai|Mexican if either is fine; blank = no settled cuisine
  exclude_cuisine, max_price, location   blank = not settled
  vegetarian, dinner                      yes / blank
  relations     links between turns, e.g. "5>4:confirm:max_price; 5>3:revise:max_price"

Kappa is computed for: should_ask (one item per scenario), active constraints
(one item per scenario x slot, category = value or 'none'; also per slot), and
relation labels (one item per (scenario, source turn, target turn) that either
annotator linked; category = relation:slot or 'none'). Relation kappa only
counts pairs someone linked, so it is also reported as an F1 overlap.
"""

import argparse
import csv
import json
import random
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from data.validate import load_scenarios  # noqa: E402

SLOTS = ("cuisine", "exclude_cuisine", "max_price", "location", "vegetarian", "dinner")
COLUMNS = ("item", "should_ask") + SLOTS + ("relations",)
ANNOTATION_DIR = ROOT / "data" / "drafts" / "bhavishya" / "annotation"
N_ITEMS = 30
SEED = 6120


# ------------------------------------------------------------------ kappa
def cohens_kappa(labels_a, labels_b):
    """Cohen's kappa for two equal-length label lists. None if undefined
    (both annotators used one single identical category everywhere)."""
    if len(labels_a) != len(labels_b) or not labels_a:
        raise ValueError("Need two non-empty label lists of the same length")
    n = len(labels_a)
    observed = sum(a == b for a, b in zip(labels_a, labels_b)) / n
    ca, cb = Counter(labels_a), Counter(labels_b)
    expected = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / (n * n)
    if expected == 1:
        return None
    return (observed - expected) / (1 - expected)


def _norm_value(slot, value):
    value = (value or "").strip()
    if not value:
        return "none"
    if slot in ("vegetarian", "dinner"):
        return "yes" if value.lower() in ("yes", "true", "y", "1") else "none"
    if slot in ("cuisine", "exclude_cuisine"):
        return "|".join(sorted(v.strip().lower() for v in value.split("|") if v.strip())) or "none"
    if slot == "max_price":
        return value.replace("$", "").strip()
    return value.lower()


def _relations(text):
    out = {}
    for part in (text or "").split(";"):
        part = part.strip()
        if not part:
            continue
        pair, relation, slot = part.split(":")
        source, target = (int(x) for x in pair.split(">"))
        out[(source, target)] = f"{relation.strip().lower()}:{slot.strip().lower()}"
    return out


def read_labels(path):
    with open(path, newline="") as f:
        rows = {r["item"].strip(): r for r in csv.DictReader(f) if r.get("item", "").strip()}
    missing = [c for c in COLUMNS if rows and c not in next(iter(rows.values()))]
    if missing:
        raise ValueError(f"{path}: missing columns {missing}")
    return rows


def agreement(rows_a, rows_b):
    items = sorted(set(rows_a) & set(rows_b))
    if not items:
        raise ValueError("The two files share no items")
    report = {"items_compared": len(items),
              "only_in_first": sorted(set(rows_a) - set(rows_b)),
              "only_in_second": sorted(set(rows_b) - set(rows_a))}
    ask_a = [rows_a[i]["should_ask"].strip().lower() for i in items]
    ask_b = [rows_b[i]["should_ask"].strip().lower() for i in items]
    report["should_ask"] = {"kappa": cohens_kappa(ask_a, ask_b),
                            "raw_agreement": sum(a == b for a, b in zip(ask_a, ask_b)) / len(items)}
    all_a, all_b, per_slot = [], [], {}
    for slot in SLOTS:
        va = [_norm_value(slot, rows_a[i][slot]) for i in items]
        vb = [_norm_value(slot, rows_b[i][slot]) for i in items]
        all_a += va
        all_b += vb
        per_slot[slot] = cohens_kappa(va, vb)
    report["active_constraints"] = {"kappa": cohens_kappa(all_a, all_b),
                                    "raw_agreement": sum(a == b for a, b in zip(all_a, all_b)) / len(all_a),
                                    "per_slot_kappa": per_slot}
    rel_a, rel_b = [], []
    tp = n_a = n_b = 0
    for i in items:
        ra, rb = _relations(rows_a[i]["relations"]), _relations(rows_b[i]["relations"])
        n_a += len(ra)
        n_b += len(rb)
        tp += sum(ra[k] == rb.get(k) for k in ra)
        for key in sorted(set(ra) | set(rb)):
            rel_a.append(ra.get(key, "none"))
            rel_b.append(rb.get(key, "none"))
    f1 = (2 * tp / (n_a + n_b)) if (n_a + n_b) else None
    report["relations"] = {"kappa": cohens_kappa(rel_a, rel_b) if rel_a else None,
                           "linked_pairs": len(rel_a), "f1_overlap": f1}
    return report


# ------------------------------------------------------------------ gold export / sheet
def gold_row(item, sc):
    ev = sc["evaluation_only"]
    active = ev["gold_dialogue_state"]["active"]
    row = {"item": item, "should_ask": "yes" if ev["gold_decision"]["should_ask"] else "no"}
    for slot in SLOTS:
        v = active.get(slot)
        if v is None or v is False or v == []:
            row[slot] = ""
        elif isinstance(v, list):
            row[slot] = "|".join(v)
        elif v is True:
            row[slot] = "yes"
        else:
            row[slot] = str(v)
    row["relations"] = "; ".join(f"{r['source_turn']}>{r['target_turn']}:{r['relation']}:{r['slot']}"
                                 for r in ev["gold_relation_links"])
    return row


def choose_items():
    """15 original + 15 draft scenarios, spread over types, in a mixed order."""
    rng = random.Random(SEED)
    originals = [sc for _, sc in load_scenarios(str(ROOT / "data" / "scenarios"))]
    drafts = [sc for _, sc in load_scenarios(str(ROOT / "data" / "drafts" / "bhavishya"))]

    def spread(pool, k):
        by_type = {}
        for sc in sorted(pool, key=lambda s: s["scenario_id"]):
            by_type.setdefault(sc["evaluation_only"]["scenario_type"], []).append(sc)
        for group in by_type.values():
            rng.shuffle(group)
        picked = []
        while len(picked) < k:
            for t in sorted(by_type):
                if by_type[t] and len(picked) < k:
                    picked.append(by_type[t].pop())
        return picked

    chosen = spread(originals, N_ITEMS // 2) + spread(drafts, N_ITEMS - N_ITEMS // 2)
    rng.shuffle(chosen)
    return [(f"S{i:02d}", sc) for i, sc in enumerate(chosen, 1)]


def make_sheet(out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    items = choose_items()
    db = json.loads((ROOT / "data" / "restaurants.json").read_text())
    lines = ["# Labeling sheet (second annotator)", "",
             "Please label each conversation **on your own, before any discussion**. Do not open the scenario "
             "files, the review sheets or `item_key.csv` - they contain the answers.", "",
             "For each item fill one row of `labels_template.csv`:", "",
             "- **should_ask**: `yes` if the assistant should ask a clarification question before recommending "
             "(because the user's request can be read in more than one way AND no single restaurant in the "
             "table fits every reading); otherwise `no`.",
             "- **cuisine, exclude_cuisine, max_price, location, vegetarian, dinner**: the user's *settled* "
             "requirements at the end of the conversation. Leave a field blank if it was never stated, is still "
             "unclear, or was only suggested by the assistant and not accepted. `Thai|Mexican` = either is fine. "
             "`vegetarian`/`dinner`: `yes` or blank. Lunch = no dinner requirement. `location` is `station` or `mall`.",
             "- **relations**: links between turns, written `source>target:relation:slot` and separated by `;`. "
             "Relations: `revise` (replaces an earlier requirement), `confirm` (accepts an assistant suggestion), "
             "`clarify`. Example: `5>4:confirm:max_price; 5>3:revise:max_price`. Blank if none.", "",
             "## Restaurant table", "",
             "| id | name | cuisine | $/person | near station | near mall | vegetarian | open for dinner |",
             "|---|---|---|---|---|---|---|---|"]
    for r in db:
        lines.append(f"| {r['restaurant_id']} | {r['name']} | {r['cuisine']} | {r['price_per_person']} | "
                     f"{'yes' if r['near_station'] else ''} | {'yes' if r['near_mall'] else ''} | "
                     f"{'yes' if r['vegetarian_options'] else ''} | {'yes' if r['open_for_dinner'] else ''} |")
    for item, sc in items:
        lines += ["", f"## {item}", ""]
        for t in sc["model_visible"]["dialogue_prefix"]:
            lines.append(f"{t['turn']}. **{t['speaker']}**: {t['text']}  ")
        lines += ["", "should_ask: ____  constraints: ____  relations: ____"]
    (out_dir / "labeling_sheet.md").write_text("\n".join(lines) + "\n")
    with open(out_dir / "labels_template.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        for item, _ in items:
            w.writerow({"item": item})
    with open(out_dir / "item_key.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["item", "scenario_id", "origin"])
        for item, sc in items:
            w.writerow([item, sc["scenario_id"], "draft" if sc["scenario_id"].startswith("BB-") else "original"])
    return items


def read_key(out_dir):
    with open(out_dir / "item_key.csv", newline="") as f:
        return {r["item"]: r["scenario_id"] for r in csv.DictReader(f)}


def export_gold(out_path, key_dir):
    key = read_key(key_dir)
    by_id = {sc["scenario_id"]: sc for _, sc in load_scenarios(str(ROOT / "data"))}
    with open(out_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        for item in sorted(key):
            w.writerow(gold_row(item, by_id[key[item]]))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="command", required=True)
    s = sub.add_parser("make-sheet")
    s.add_argument("--out-dir", type=Path, default=ANNOTATION_DIR)
    g = sub.add_parser("export-gold")
    g.add_argument("--out", type=Path, required=True)
    g.add_argument("--key-dir", type=Path, default=ANNOTATION_DIR)
    k = sub.add_parser("kappa")
    k.add_argument("first", type=Path)
    k.add_argument("second", type=Path)
    args = ap.parse_args()
    if args.command == "make-sheet":
        items = make_sheet(args.out_dir)
        print(f"Wrote labeling sheet for {len(items)} items to {args.out_dir}")
    elif args.command == "export-gold":
        export_gold(args.out, args.key_dir)
        print(f"Wrote gold labels to {args.out}")
    else:
        print(json.dumps(agreement(read_labels(args.first), read_labels(args.second)), indent=2))


if __name__ == "__main__":
    main()
