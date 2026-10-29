from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REGULAR_SYMBOLS = ("K", "Q", "J", "10", "9", "8", "7")
PAY_KEYS = ("3", "4", "5")


def load_config(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        config = json.load(handle)
    validate_config(config)
    return config


def validate_config(config: dict[str, Any]) -> None:
    lines = config.get("lines", [])
    _require(len(lines) == 20, "lines must contain 20 paths")
    _require(len({tuple(line) for line in lines}) == 20, "lines must be unique")
    for line in lines:
        _require(len(line) == 5, "each line must have 5 rows")
        _require(all(row in (0, 1, 2) for row in line), "rows must be 0/1/2")

    presets = config.get("presets", {})
    _require(presets, "presets must be non-empty")
    _require(config.get("default_preset") in presets, "default_preset invalid")
    for name, preset in presets.items():
        validate_preset(name, preset)


def validate_preset(name: str, preset: dict[str, Any]) -> None:
    _require(preset.get("max_win", 0) > 0, f"{name}: max_win")
    grid = preset.get("grid", {})
    _require(grid.get("reels") == 5, f"{name}: reels")
    _require(grid.get("rows") == 3, f"{name}: rows")
    _require(grid.get("min_match") == 3, f"{name}: min_match")

    symbols = preset.get("symbols", {})
    for symbol in REGULAR_SYMBOLS:
        _require(symbol in symbols, f"{name}: missing {symbol}")
        _require(symbols[symbol].get("type") == "regular", f"{name}:{symbol}")
        _require(all(key in symbols[symbol].get("pays", {}) for key in PAY_KEYS), f"{name}:{symbol} pays")

    strips = preset.get("reels", {}).get("strips", [])
    _require(len(strips) == 5, f"{name}: five strips")
    for index, strip in enumerate(strips, start=1):
        _require(len(strip) >= 3, f"{name}: reel {index} short")
        unknown = sorted(set(strip) - set(symbols))
        _require(not unknown, f"{name}: reel {index} unknown {unknown}")

    meter = preset.get("meter", {})
    _require(meter.get("threshold", 0) > 0, f"{name}: meter threshold")
    _require(meter.get("points_multiplier", 0) > 0, f"{name}: meter points")
    _require(meter.get("free_spins", 0) > 0, f"{name}: meter free spins")
    _require(meter.get("free_spin_multiplier", 0) > 0, f"{name}: meter FS multiplier")

    bet = preset.get("bet", {})
    _require(bet.get("levels"), f"{name}: bet levels")
    _require(bet.get("default") in bet["levels"], f"{name}: default bet")


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)
