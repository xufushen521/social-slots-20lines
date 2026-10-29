from __future__ import annotations

import math
import random
from typing import Any

from .lines import evaluate_lines
from .reels import draw_grid


def meter_points(wins: list[dict[str, Any]], preset: dict[str, Any]) -> int:
    multiplier = preset["meter"]["points_multiplier"]
    return sum(max(1, round(item["pay"] * multiplier)) for item in wins)


def simulate_preset(
    preset: dict[str, Any],
    lines: list[list[int]],
    spins: int = 1_000_000,
    bet: float = 1.0,
    seed: int = 20261028,
) -> dict[str, Any]:
    rng = random.Random(seed)
    max_win = preset["max_win"] * bet
    meter = preset["meter"]
    meter_value = 0
    total_win = 0.0
    base_win = 0.0
    feature_win = 0.0
    sum_squares = 0.0
    hits = 0
    actual_max = 0.0
    meter_triggers = 0
    fs_wins_total = 0.0

    for _ in range(spins):
        grid = draw_grid(preset, rng)
        wins = evaluate_lines(grid, preset, bet, lines)
        spin_win = sum(item["win"] for item in wins)
        base_win += spin_win
        meter_value += meter_points(wins, preset)

        if meter_value >= meter["threshold"]:
            for _ in range(meter["free_spins"]):
                fs_grid = draw_grid(preset, rng)
                fs_wins = evaluate_lines(fs_grid, preset, bet, lines)
                fs_win = sum(item["win"] for item in fs_wins) * meter["free_spin_multiplier"]
                fs_wins_total += fs_win
                feature_win += fs_win
                spin_win += fs_win
            meter_triggers += 1
            meter_value = 0

        spin_win = min(spin_win, max_win)
        total_win += spin_win
        sum_squares += spin_win * spin_win
        hits += spin_win > 0
        actual_max = max(actual_max, spin_win)

    mean = total_win / spins
    variance = max(0.0, sum_squares / spins - mean * mean)
    return {
        "spins": spins,
        "total_rtp": mean,
        "base_rtp": base_win / spins,
        "feature_contribution": feature_win / spins,
        "hit_rate": hits / spins,
        "sd": math.sqrt(variance),
        "max_win": actual_max,
        "meter_trigger_rate": meter_triggers / spins,
        "avg_feature_win": fs_wins_total / meter_triggers if meter_triggers else 0.0,
    }
