from __future__ import annotations

import collections
import secrets
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from game.convex.grid import Grid


def _level_one(
    grid: Grid,
    _player_id: int,
    _player_played: set[tuple[int, int]],
) -> tuple[int, int]:

    return secrets.choice(tuple(grid.get_empty_positions()))


def _level_two(
    grid: Grid,
    player_id: int,
    player_played: set[tuple[int, int]],
) -> tuple[int, int]:

    empties = grid.get_empty_positions()
    all_played = grid.get_played_positions()

    # find all columns and rows with 2 points
    columns = {
        e
        for e, c in collections.Counter(y for _, y in all_played).items()
        if c == 2  # noqa: PLR2004
    }
    rows = {
        e
        for e, c in collections.Counter(x for x, _ in all_played).items()
        if c == 2  # noqa: PLR2004
    }

    # we then remove all the empty positions that are in these columns and rows
    filtered = empties.copy()
    filtered -= {e for e in empties if e[0] in rows or e[1] in columns}

    # if there are no empty positions left, we fallback to the previous heuristic
    return (
        secrets.choice(tuple(filtered)) if filtered else _level_one(grid, player_id, player_played)
    )


_int_to_func: dict[int, Callable[[Grid, int, set[tuple[int, int]]], tuple[int, int]]] = {
    1: _level_one,
    2: _level_two,
}


class Heuristic:

    def __init__(self: Heuristic, grid: Grid, player_id: int, level: int) -> None:
        if player_id < 1:
            msg = "player_id must be greater than 0."
            raise ValueError(msg)

        if level not in _int_to_func:
            msg = f"level must be in {set(_int_to_func.keys())}."
            raise ValueError(msg)

        self.grid = grid
        self.player_id = player_id
        self.played: set[tuple[int, int]] = set()
        self.level = level

    def play(self: Heuristic) -> tuple[int, int]:

        choice = _int_to_func[self.level](self.grid, self.player_id, self.played)

        self.grid.play(*choice, self.player_id)
        self.played.add(choice)

        return choice
