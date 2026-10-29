from __future__ import annotations

from math import prod
from typing import Any


def symbol_probability(preset: dict[str, Any], symbol: str, reel_index: int) -> float:
    strip = preset["reels"]["strips"][reel_index]
    return strip.count(symbol) / len(strip)


def exact_line_rtp(preset: dict[str, Any]) -> float:
    """Total base RTP with paytable expressed as total-bet multiple per line."""
    total = 0.0
    for symbol, info in preset["symbols"].items():
        if info.get("type") != "regular":
            continue
        probs = [symbol_probability(preset, symbol, reel) for reel in range(5)]
        pays = info["pays"]
        exactly_3 = prod(probs[:3]) * (1 - probs[3])
        exactly_4 = prod(probs[:4]) * (1 - probs[4])
        exactly_5 = prod(probs)
        total += pays["3"] * exactly_3 + pays["4"] * exactly_4 + pays["5"] * exactly_5
    return total * 20
