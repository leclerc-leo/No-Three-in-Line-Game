from __future__ import annotations

import secrets
from typing import TYPE_CHECKING, Callable

from game.players import player

if TYPE_CHECKING:
    from game.convex import grid


def _level_one(
    g: grid.Grid,
    _player: Heuristic,
) -> tuple[int, int]:

    return secrets.choice(tuple(g.empties))


def _level_two(
    g: grid.Grid,
    player: Heuristic,
) -> tuple[int, int]:

    filtered = player.empties

    # if there are no empty positions left, we fallback to the previous heuristic
    return secrets.choice(tuple(filtered)) if filtered else _level_one(g, player)


def _level_three(
    g: grid.Grid,
    player: Heuristic,
) -> tuple[int, int]:

    # To be implemented later, same as level two but with diagonals

    return _level_two(g, player)


def _level_four(
    g: grid.Grid,
    player: Heuristic,
) -> tuple[int, int]:

    picked: tuple[int, int] | None = None

    while picked is None and player.empties:
        # retrieve in O(n) a random element from a set
        # Improvement in O(1) doesn't seems to be possible in python using sets
        picked = secrets.choice(tuple(player.empties))

        # If the picked position does not create a 3 in line, we return it
        if not player.has_three_in_line(picked):
            return picked

        picked = None

    return _level_three(g, player)


def _level_five(
    g: grid.Grid,
    player: Heuristic,
) -> tuple[int, int]:

    # To be implemented later, same as level four but with tries to block the opponent

    return _level_four(g, player)


_int_to_level_func: dict[int, Callable[[grid.Grid, Heuristic], tuple[int, int]]] = {
    1: _level_one,
    2: _level_two,
    3: _level_three,
    4: _level_four,
    5: _level_five,
}
"""a dict that maps level to the corresponding function

if the level is not able to find a valid move, it will fallback to the previous level
therefore it will always return a valid move unless the grid is full which is impossible
since the game ends if more than 3 points are in line. (Could be possible on a 1x1 or 2x2 grid
or higher if there is a lot of players)
"""


class Heuristic(player.Player):

    def __init__(self: Heuristic, g: grid.Grid, level: int) -> None:

        if level not in _int_to_level_func:
            msg = f"level must be in {set(_int_to_level_func.keys())}."
            raise ValueError(msg)

        super().__init__(g)

        self._level = level

    def _choose(self: Heuristic) -> tuple[int, int]:

        return _int_to_level_func[self._level](self._grid, self)
