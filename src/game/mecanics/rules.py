from __future__ import annotations

import collections
import functools
import math

LIMIT = 2
"""int: Number of points on the same line before to be consided a 3 in line.

3 - 1 = 2

DO NOT CHANGE THIS VALUE, the program is not designed to handle other values.
"""


@functools.lru_cache(None)
def normalized_slope_intercept(
    x1: int,
    y1: int,
    x2: int,
    y2: int,
) -> tuple[tuple[int, int], tuple[int, int]]:
    """Calculate the normalized slope and intercept between
    two points (x1, y1) and (x2, y2).
    """

    dx, dy = x2 - x1, y2 - y1

    if dx == 0:  # Vertical line
        slope = (1, 0)
        intercept = (x1, 0)

    elif dy == 0:  # Horizontal line
        slope = (0, 1)
        intercept = (0, y1)

    else:
        # Normalize slope
        divisor = math.gcd(dx, dy)
        normalized_dy, normalized_dx = dy // divisor, dx // divisor
        slope = (normalized_dy, normalized_dx)

        # Calculate intercept as a multiple of the slope
        intercept_value = y1 * normalized_dx - x1 * normalized_dy
        intercept = (intercept_value, normalized_dx)

    return slope, intercept


def has_three_in_line(
    played: set[tuple[int, int]],
    *,
    lines: dict[tuple[tuple[int, int], tuple[int, int]], int] | None = None,
    done: set[tuple[int, int]] | None = None,
) -> bool:

    lines = lines or collections.defaultdict(int)
    done = done or set()  # Avoid to check the same pair twice, this would make lines count wrong

    # Check each point as the origin point to compare others
    for p1 in played:
        done.add(p1)

        for p2 in played - done:

            slope, intercept = normalized_slope_intercept(*p1, *p2)
            lines[(slope, intercept)] += 1

            if lines[(slope, intercept)] >= LIMIT:
                # If we find two other points on the same line with p1
                return True

    return False
