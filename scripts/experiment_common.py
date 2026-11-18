"""Shared helpers for the experiment scripts: scenario selection and an
OFFLINE cost estimate (no API call is made to estimate anything).

Token estimate: the exact request the Claude strategy would send (system
prompt + JSON payload with the conversation and the full restaurant table +
the JSON output schema) is built locally and its characters are divided by
CHARS_PER_TOKEN. This is an approximation (roughly +/-30%); the free
count_tokens endpoint can give exact numbers, but that is also an API call,
so it is not used without approval.

Output tokens are a guess: Claude Opus 5.5 always thinks (the client asks for
effort=low), and thinking is billed as output. A central and a high guess are
reported.
"""

import json
import math
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.claude_client import DEFAULT_MODEL  # noqa: E402
from src.claude_strategy import ACTION_SCHEMA, PROMPT_VARIANTS  # noqa: E402
from src.data import load_dataset, scenario_path  # noqa: E402
from src.splits import load_split  # noqa: E402

CHARS_PER_TOKEN = 3.5
EXTRA_TOKENS_PER_FOLLOW_UP = 60          # one question + one answer turn added to the context
OUTPUT_TOKENS = {"central": 400, "high": 1500}
# USD per 1M tokens (Anthropic first-party pricing table, cached 2026-11-03).
PRICES = {"claude-opus-5-5": (4.00, 20.00), "claude-sonnet-5-5": (2.00, 10.00), "claude-haiku-5-5": (0.10, 0.50)}


def gold(scenario_id):
    return json.loads(scenario_path(scenario_id).read_text())["evaluation_only"]


def dev_ids(include_drafts=True):
    return sorted(load_split(include_drafts=include_drafts).dev)


def should_ask_dev_ids():
    """Should-ask scenarios in the dev split: original dev + proposed draft dev."""
    return [i for i in dev_ids() if gold(i)["gold_decision"]["should_ask"]]


def request_tokens(scenario_ids, prompt_variant="rule_given", budget=0):
    """Estimated input tokens of the FIRST request for each scenario."""
    _, system_prompt = PROMPT_VARIANTS[prompt_variant]
    dataset = load_dataset(list(scenario_ids))
    out = {}
    for sid in scenario_ids:
        sc = dataset.scenarios[sid]
        payload = {
            "turns": [asdict(t) for t in sc.turns],
            "restaurant_database": [dict(r) for r in sc.restaurants],
            "remaining_budget": budget,
            "allowed_actions": ["ASK", "RECOMMEND"] if budget else ["RECOMMEND"],
        }
        chars = len(system_prompt) + len(json.dumps(payload, ensure_ascii=False)) + len(json.dumps(ACTION_SCHEMA))
        out[sid] = math.ceil(chars / CHARS_PER_TOKEN)
    return out


def cost_table(calls, input_tokens, model=DEFAULT_MODEL):
    """calls and input_tokens are totals; returns central/high estimates."""
    price = PRICES.get(model)
    rows = {}
    for label, out_per_call in OUTPUT_TOKENS.items():
        output_tokens = calls * out_per_call
        cost = None
        if price:
            cost = input_tokens / 1e6 * price[0] + output_tokens / 1e6 * price[1]
        rows[label] = {"input_tokens": input_tokens, "output_tokens": output_tokens,
                       "usd": None if cost is None else round(cost, 2)}
    return rows


def print_estimate(title, calls, input_tokens, model, notes=()):
    print(f"\n=== {title} ===")
    print(f"model: {model}")
    print(f"API calls (upper bound): {calls}")
    for label, row in cost_table(calls, input_tokens, model).items():
        usd = "unknown price" if row["usd"] is None else f"${row['usd']:.2f}"
        print(f"  {label:7s} input ~{row['input_tokens']:,} tok  output ~{row['output_tokens']:,} tok  -> {usd}")
    for note in notes:
        print(f"  note: {note}")
