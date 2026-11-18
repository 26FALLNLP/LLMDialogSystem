"""Dev/test split guard.

Normal runs use the dev split only. Running anything in the test split needs
an explicit final_test=True (the --final-test flag), so the test set is not
used while prompts or systems are still being tuned.

Splits:
  data/splits/split.json                                 frozen split of the original 36 (never edited here)
  data/drafts/bhavishya/draft_split_proposal.json        proposed split for the BB- drafts (not frozen)
"""

import json
from dataclasses import dataclass
from pathlib import Path

from .data import DATA_DIR

FROZEN_SPLIT = Path("splits") / "split.json"
DRAFT_SPLIT = Path("drafts") / "bhavishya" / "draft_split_proposal.json"


class SplitError(ValueError):
    """A run asked for scenarios it is not allowed to use."""


@dataclass(frozen=True)
class Split:
    dev: frozenset[str]
    test: frozenset[str]


def load_split(data_dir: Path = DATA_DIR, include_drafts: bool = True) -> Split:
    data_dir = Path(data_dir)
    dev, test = set(), set()
    files = [data_dir / FROZEN_SPLIT] + ([data_dir / DRAFT_SPLIT] if include_drafts else [])
    for path in files:
        if not path.exists():
            if path == data_dir / FROZEN_SPLIT:
                raise SplitError(f"Missing frozen split file {path}")
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        dev.update(data["dev"])
        test.update(data["test"])
    overlap = dev & test
    if overlap:
        raise SplitError(f"Scenarios in both dev and test: {sorted(overlap)}")
    return Split(frozenset(dev), frozenset(test))


def select_scenarios(
    requested: list[str] | None,
    *,
    run_all: bool = False,
    final_test: bool = False,
    include_drafts: bool = False,
    data_dir: Path = DATA_DIR,
) -> list[str]:
    """Return the scenario IDs a run may use.

    - run_all: every dev scenario (or every test scenario with final_test).
      Draft scenarios are added only with include_drafts.
    - requested IDs: allowed if they are in dev; test IDs need final_test.
      IDs in no split are refused, so new scenarios get a split before use.
    """
    full = load_split(data_dir, include_drafts=True)
    if run_all:
        chosen = load_split(data_dir, include_drafts=include_drafts)
        pool = chosen.test if final_test else chosen.dev
        return sorted(pool)
    ids = list(dict.fromkeys(requested or []))
    if not ids:
        raise SplitError("No scenarios requested.")
    unknown = [i for i in ids if i not in full.dev and i not in full.test]
    if unknown:
        raise SplitError(f"Not in any split (add them to a split first): {', '.join(unknown)}")
    blocked = [i for i in ids if i in full.test]
    if blocked and not final_test:
        raise SplitError(
            f"In the TEST split: {', '.join(blocked)}. Normal runs use dev only; "
            "pass --final-test for the final evaluation."
        )
    return ids
