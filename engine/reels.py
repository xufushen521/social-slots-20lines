from __future__ import annotations

import random
from typing import Any


def draw_grid(preset: dict[str, Any], rng: random.Random | None = None) -> list[list[str]]:
    rng = rng or random.Random()
    strips = preset["reels"]["strips"]
    rows = preset["grid"]["rows"]
    return [
        [strip[(rng.randrange(len(strip)) + row) % len(strip)] for row in range(rows)]
        for strip in strips
    ]
