"""Hard spending cap for Claude API calls.

The cap lives in ONE place: configs/budget.yaml (max_usd). Real spend is kept
in results/spend_log.json and survives across runs.

- max_usd == 0: API calls are disabled. Scripts refuse to run and every
  ClaudeClient call is refused before anything is sent.
- max_usd > 0: before each call the guard adds the worst case for that call
  (input tokens estimated from the request, plus the full max_tokens of
  output) to the spend so far; if that could exceed the cap, the call is
  refused. After a call the real cost (from the API's usage numbers) is added
  to the log.

Paths can be overridden with the environment variables BUDGET_CONFIG and
SPEND_LOG (used by the tests).
"""

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = ROOT / "configs" / "budget.yaml"
DEFAULT_SPEND_LOG = ROOT / "results" / "spend_log.json"
DISABLED_MESSAGE = "API calls are disabled (budget cap is $0). Change configs/budget.yaml to enable."
# USD per 1M tokens (input, output) - Anthropic first-party prices, cached 2026-11-03.
PRICES = {"claude-opus-5-5": (4.00, 20.00), "claude-sonnet-5-5": (2.00, 10.00), "claude-haiku-5-5": (0.10, 0.50)}
CHARS_PER_TOKEN_WORST = 2.5   # deliberately pessimistic, so the pre-call check over-estimates input


class BudgetError(RuntimeError):
    """An API call was refused by the spending cap."""


def config_path() -> Path:
    return Path(os.environ.get("BUDGET_CONFIG", DEFAULT_CONFIG))


def spend_log_path() -> Path:
    return Path(os.environ.get("SPEND_LOG", DEFAULT_SPEND_LOG))


def load_cap(path: Path | None = None) -> float:
    """Read max_usd from the small YAML file (no YAML library needed)."""
    path = path or config_path()
    if not path.exists():
        return 0.0  # no config = no spending
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if line.startswith("max_usd:"):
            value = float(line.split(":", 1)[1].strip())
            if value < 0:
                raise ValueError("max_usd must be 0 or more")
            return value
    return 0.0


def api_enabled() -> bool:
    return load_cap() > 0


def require_api_enabled() -> None:
    """Call at the start of any script that could call the API."""
    if not api_enabled():
        raise BudgetError(DISABLED_MESSAGE)


def cost_usd(model: str, input_tokens: int, output_tokens: int) -> float:
    price = PRICES[model]
    return input_tokens / 1e6 * price[0] + output_tokens / 1e6 * price[1]


@dataclass
class SpendGuard:
    cap_usd: float
    log_path: Path

    @classmethod
    def from_config(cls) -> "SpendGuard":
        return cls(load_cap(), spend_log_path())

    # ------------------------------------------------------------- log
    def _read(self) -> dict:
        if self.log_path.exists():
            return json.loads(self.log_path.read_text(encoding="utf-8"))
        return {"total_usd": 0.0, "calls": 0, "entries": []}

    def spent(self) -> float:
        return self._read()["total_usd"]

    def _write(self, log: dict) -> None:
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.log_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(log, indent=2) + "\n", encoding="utf-8")
        tmp.replace(self.log_path)

    # ------------------------------------------------------------- checks
    def worst_case(self, model: str, request_chars: int, max_tokens: int) -> float:
        return cost_usd(model, int(request_chars / CHARS_PER_TOKEN_WORST) + 1, max_tokens)

    def before_call(self, model: str, request_chars: int, max_tokens: int) -> None:
        if self.cap_usd <= 0:
            raise BudgetError(DISABLED_MESSAGE)
        if model not in PRICES:
            raise BudgetError(f"No price known for model {model!r}; refusing because the cost cannot be bounded.")
        spent = self.spent()
        worst = self.worst_case(model, request_chars, max_tokens)
        if spent + worst > self.cap_usd:
            raise BudgetError(
                f"Spending cap reached: ${spent:.4f} spent of ${self.cap_usd:.2f}; the next call could cost up to "
                f"${worst:.4f}. Raise max_usd in configs/budget.yaml to continue."
            )

    def record(self, model: str, input_tokens: int | None, output_tokens: int | None,
               request_chars: int, max_tokens: int, note: str = "") -> float:
        """Add one finished call to the log. Unknown usage is charged at the worst case."""
        if input_tokens is None or output_tokens is None:
            usd = self.worst_case(model, request_chars, max_tokens)
        else:
            usd = cost_usd(model, input_tokens, output_tokens)
        log = self._read()
        log["total_usd"] = round(log["total_usd"] + usd, 6)
        log["calls"] += 1
        log["entries"].append({"time": time.strftime("%Y-%m-%dT%H:%M:%S"), "model": model,
                               "input_tokens": input_tokens, "output_tokens": output_tokens,
                               "usd": round(usd, 6), "note": note})
        self._write(log)
        return usd
