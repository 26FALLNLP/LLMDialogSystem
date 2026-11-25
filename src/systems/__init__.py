"""The dialogue systems S1-S5 and a factory for the runner.

S1 is Xianhao's ClaudeStrategy (src/claude_strategy.py); S2-S5 are in strategies.py.
"""

from ..claude_strategy import ClaudeStrategy
from .strategies import MemoryLinksAskStrategy, MemoryLinksStrategy, MemoryNoLinksStrategy, SummaryStrategy

SYSTEMS = {
    "s1": ClaudeStrategy,
    "s2": SummaryStrategy,
    "s3": MemoryLinksStrategy,
    "s4": MemoryNoLinksStrategy,
    "s5": MemoryLinksAskStrategy,
}
# Output-token cap per model call. S1 keeps its original 2048; the memory systems
# return the whole memory as JSON, so they get more room.
MAX_TOKENS = {"s1": 2048, "s2": 4096, "s3": 8192, "s4": 8192, "s5": 8192}


def build_strategy(name: str, client, prompt_variant: str = "rule_given"):
    try:
        cls = SYSTEMS[name]
    except KeyError:
        raise ValueError(f"Unknown system {name!r}; choose {sorted(SYSTEMS)}") from None
    return cls(client, prompt_variant)
