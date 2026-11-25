"""Dev/test split guard.

Normal runs use the dev split only. Running anything in the test split needs
final_test=True (the --final-test flag), so the test set is not used while
prompts or systems are still being tuned. The split file is
data/splits/split.json, made by `python -m src.make_split`.
"""

import json
from dataclasses import dataclass
from pathlib import Path

from .data import DATA_DIR

SPLIT_FILE = Path("splits") / "split.json"


class SplitError(ValueError):
    """A run asked for scenarios it is not allowed to use."""


@dataclass(frozen=True)
class Split:
    dev: frozenset[str]
    test: frozenset[str]


def load_split(data_dir: Path = DATA_DIR) -> Split:
    path = Path(data_dir) / SPLIT_FILE
    if not path.exists():
        raise SplitError(f"Missing split file {path}; run `python -m src.make_split` first.")
    data = json.loads(path.read_text(encoding="utf-8"))
    dev, test = frozenset(data["dev"]), frozenset(data["test"])
    if dev & test:
        raise SplitError(f"Scenarios in both dev and test: {sorted(dev & test)}")
    return Split(dev, test)


def select_scenarios(
    requested: list[str] | None,
    *,
    run_all: bool = False,
    final_test: bool = False,
    include_drafts: bool = True,
    data_dir: Path = DATA_DIR,
) -> list[str]:
    """Scenario IDs a run may use.

    - run_all: every dev scenario, or every test scenario with final_test.
      BB- drafts are left out with include_drafts=False.
    - requested IDs: dev IDs are allowed; test IDs need final_test; IDs in no
      split are refused, so new scenarios get a split before anyone runs them.
    """
    split = load_split(data_dir)
    if run_all:
        pool = split.test if final_test else split.dev
        return sorted(i for i in pool if include_drafts or not i.startswith("BB-"))
    ids = list(dict.fromkeys(requested or []))
    if not ids:
        raise SplitError("No scenarios requested.")
    unknown = [i for i in ids if i not in split.dev and i not in split.test]
    if unknown:
        raise SplitError(f"Not in any split (add them to the split first): {', '.join(unknown)}")
    blocked = [i for i in ids if i in split.test]
    if blocked and not final_test:
        raise SplitError(
            f"In the TEST split: {', '.join(blocked)}. Normal runs use dev only; "
            "pass --final-test for the final evaluation."
        )
    return ids
