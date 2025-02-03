from __future__ import annotations

import random
from typing import TYPE_CHECKING, Callable, Literal, TypeVar

from game.players import player

if TYPE_CHECKING:
    from game.convex import grid


T = TypeVar("T")


def _choice(s: set[T]) -> T:
    return random.choice(tuple(s))  # noqa: S311 NOSONAR - to allow for seeds


def _choose_zero(
    player: Heuristic,
) -> tuple[int, int]:

    if player.availables:
        return _choice(player.availables)

    if player.grid.empties:
        return _choice(player.grid.empties)

    msg = "Trying to choose from a grid that is full or has no spots."
    raise ValueError(msg)


def _choice_one(
    player: Heuristic,
) -> tuple[int, int]:

    if player.availables:

        center = (player.grid.width // 2, player.grid.height // 2)

        bests = set()
        best_score = -1

        for pos in player.availables:
            score = sum(
                abs(pos[0] - p[0]) + abs(pos[1] - p[1]) for p in player.played.union({center})
            )

            if score > best_score:
                bests = {pos}
                best_score = score

            elif score == best_score:
                bests.add(pos)

        return _choice(bests)

    return _choose_zero(player)


LevelChoose = Literal[0, 1]
_int_to_choose_func: dict[LevelChoose, Callable[[Heuristic], tuple[int, int]]] = {
    0: _choose_zero,
    1: _choice_one,
}
"""a dict that maps level to the corresponding function

if the level is not able to find a valid move, it will fallback to the previous level
therefore it will always return a valid move unless the grid is full which is impossible
since the game ends if more than 3 points are in line. (Could be possible on a 1x1 or 2x2 grid
or higher if there is a lot of players)
"""


def _available_zero(
    _player: Heuristic,
    _slope: tuple[int, int],
    _intercept: tuple[int, int],
) -> None:
    """All spots on the grid except those played are available to choose from.

    !!! note
        Those spots might not be valid moves.
    """


def _available_one(
    player: Heuristic,
    slope: tuple[int, int],
    intercept: tuple[int, int],
) -> None:

    if slope[0] == 0 or slope[1] == 0:
        player.availables -= player.grid.get_positions(slope, intercept)


def _available_two(
    player: Heuristic,
    slope: tuple[int, int],
    intercept: tuple[int, int],
) -> None:

    _available_one(player, slope, intercept)

    if abs(slope[0]) == 1 and abs(slope[1]) == 1:
        player.availables -= player.grid.get_positions(slope, intercept)


def _available_three(
    player: Heuristic,
    slope: tuple[int, int],
    intercept: tuple[int, int],
) -> None:

    player.availables -= player.grid.get_positions(slope, intercept)


LevelAvailable = Literal[0, 1, 2, 3]
_int_to_available_func: dict[
    LevelAvailable,
    Callable[
        [
            Heuristic,
            tuple[int, int],
            tuple[int, int],
        ],
        None,
    ],
] = {
    0: _available_zero,
    1: _available_one,
    2: _available_two,
    3: _available_three,
}


class Heuristic(player.Player):

    def __init__(
        self: Heuristic,
        pid: str,
        g: grid.Grid,
        level_choosing: LevelChoose,
        level_available: LevelAvailable,
    ) -> None:

        super().__init__(pid, g)

        self._choosing: LevelChoose = level_choosing
        self._available: LevelAvailable = level_available

    def _choose(self: Heuristic) -> tuple[int, int]:
        return _int_to_choose_func[self._choosing](self)

    def _update_availables(
        self: Heuristic,
        slope: tuple[int, int],
        intercept: tuple[int, int],
    ) -> None:

        _int_to_available_func[self._available](self, slope, intercept)
