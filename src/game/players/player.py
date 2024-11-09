from __future__ import annotations

import abc
import collections
from typing import TYPE_CHECKING

from game.mecanics import rules

if TYPE_CHECKING:
    from game.convex import grid


class Player(abc.ABC):

    def __init__(self: Player, g: grid.Grid) -> None:

        self._grid = g
        self._played: set[tuple[int, int]] = set()

        self._lines: collections.defaultdict[tuple[tuple[int, int], tuple[int, int]], int] = (
            collections.defaultdict(int)
        )

        self._empties = g.board.copy() - g.played

    @property
    def lines(self: Player) -> dict[tuple[tuple[int, int], tuple[int, int]], int]:
        return self._lines.copy()

    @property
    def empties(self: Player) -> set[tuple[int, int]]:
        return self._empties.copy()

    @abc.abstractmethod
    def _choose(
        self: Player,
    ) -> tuple[int, int]:
        raise NotImplementedError

    def _has_three_in_line(
        self: Player,
        new_pos: tuple[int, int],
        *,
        add_to_played: bool = False,
    ) -> bool:

        # Saving is done by giving the reference to the original dict
        lines = self._lines if add_to_played else self._lines.copy()

        for p1 in self._played:

            slope, intercept = rules.normalized_slope_intercept(*p1, *new_pos)
            lines[(slope, intercept)] += 1
            # we should return a list of detected slope and intercept
            # to then remove them from the empties if we are adding to played

            if lines[(slope, intercept)] >= rules.LIMIT:
                self._empties -= {new_pos}

                if slope[0] == 0:
                    self._empties -= {(x, new_pos[1]) for x in range(self._grid.width)}

                elif slope[1] == 0:
                    self._empties -= {(new_pos[0], y) for y in range(self._grid.height)}

                return True

        return False

    def has_three_in_line(self: Player, new_pos: tuple[int, int]) -> bool:
        return self._has_three_in_line(new_pos)

    def is_busted(self: Player) -> bool:
        return any(val >= rules.LIMIT for val in self._lines.values())

    def play(self: Player) -> tuple[int, int]:
        """Play a move on the grid.

        !!! Warning
            Absolutly not use grid.play after this method, it's already done here.

            This would break a lot of things.

            The returned value should only be used to display the move or transmit
            it to another player.

        Returns:
            The position played.
        """

        # We make sure to keep the empties up to date in case another player
        # has played before us
        self._empties -= self._grid.played

        choice = self._choose()

        # Update everything related to the played move
        self._empties -= {choice}
        _ = self._has_three_in_line(choice, add_to_played=True)
        self._grid.play(*choice)
        self._played.add(choice)

        return choice
