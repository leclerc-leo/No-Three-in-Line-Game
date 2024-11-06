from __future__ import annotations

import functools
import itertools

# _is_on_same_line and get_three_in_line are inspied by the following code:
# Inspired by https://github.com/vjdad4m/no3inline/blob/main/no3inline/find_3_in_line.cu


@functools.lru_cache(maxsize=None)
def _is_on_same_line(
    x: tuple[int, int],
    y: tuple[int, int],
    z: tuple[int, int],
) -> bool:
    # Check if three points are on the same line by computing cross-products
    return (x[0] - y[0]) * (x[1] - z[1]) == (x[0] - z[0]) * (x[1] - y[1])


def get_three_in_line(
    played: set[tuple[int, int]],
    board: set[tuple[int, int]] | None = None,
) -> list[tuple[tuple[int, int], ...]]:

    # Maybe possible to use the board to optimize the function
    board = board or set()

    results: list[tuple[tuple[int, int], ...]] = []

    # Use set to ensure unique combinations of 3 points
    for comb in set(itertools.combinations(played, 3)):

        # Check if these three points are on the same line
        if _is_on_same_line(*comb):

            results.append(comb)  # noqa: PERF401

    return results
