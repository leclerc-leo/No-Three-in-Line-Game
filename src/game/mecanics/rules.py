from __future__ import annotations

import itertools


# @functools.lru_cache(maxsize=None)
def _is_on_same_line(
    x: tuple[int, int],
    y: tuple[int, int],
    z: tuple[int, int],
) -> bool:
    # Check if three points are on the same line by computing cross-products
    return (x[0] - y[0]) * (x[1] - z[1]) == (x[0] - z[0]) * (x[1] - y[1])


def get_three_in_line(
    # Possible d'optimiser en utilisant la carte principalement grace aux bords
    played: set[tuple[int, int]],
    board: set[tuple[int, int]] | None = None,
    n: int = 3,
) -> list[tuple[tuple[int, int], ...]]:

    board = board or set()

    results: list[tuple[tuple[int, int], ...]] = []

    # Use set to ensure unique combinations of 3 points
    for comb in set(itertools.combinations(played, n)):

        # Check if these three points are on the same line
        if _is_on_same_line(*comb):

            results.append(comb)  # noqa: PERF401 - plus comprehensible

    # Convert results to an array if there are results, otherwise return an empty array

    return results
