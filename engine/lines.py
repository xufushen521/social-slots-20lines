from __future__ import annotations

from typing import Any


def evaluate_lines(
    grid: list[list[str]],
    preset: dict[str, Any],
    bet: float,
    lines: list[list[int]],
) -> list[dict[str, Any]]:
    wins: list[dict[str, Any]] = []
    for line_index, rows in enumerate(lines, start=1):
        symbols = [grid[reel][row] for reel, row in enumerate(rows)]
        symbol = symbols[0]
        match = 1
        for next_symbol in symbols[1:]:
            if next_symbol != symbol:
                break
            match += 1
        if match < preset["grid"]["min_match"]:
            continue
        pay = preset["symbols"][symbol]["pays"][str(match)]
        wins.append(
            {
                "line": line_index,
                "symbol": symbol,
                "match": match,
                "pay": pay,
                "win": pay * bet,
                "symbols": symbols,
            }
        )
    return wins
