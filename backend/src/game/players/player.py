from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Literal

from game.mecanics import rules

if TYPE_CHECKING:
    from game.convex import grid


class Player(abc.ABC):

    def __init__(self: Player, pid: str, g: grid.Grid) -> None:

        self.id = pid

        self.grid = g
        self.grid.players.add(self)

        self.played: set[tuple[int, int]] = set()

        self.availables = g.empties.copy()
        self.allowed = g.empties.copy()

        self._busted = False

    @property
    def busted(self: Player) -> bool:
        return self._busted

    @abc.abstractmethod
    def _choose(
        self: Player,
    ) -> tuple[int, int]:
        raise NotImplementedError

    @abc.abstractmethod
    def _update_availables(
        self: Player,
        slope: tuple[int, int],
        intercept: tuple[int, int],
    ) -> None:
        raise NotImplementedError

    def _add_new_pos(
        self: Player,
        new_pos: tuple[int, int],
    ) -> bool:

        if new_pos not in self.allowed or self._busted:
            self._busted = True
            return True

        for p1 in self.played:

            slope, intercept = rules.normalized_slope_intercept(*p1, *new_pos)

            if slope[0] < self.grid.width // 2 or slope[1] < self.grid.height // 2:
                self._update_availables(slope, intercept)
                self.allowed -= self.grid.get_positions(slope, intercept)

        return False

    def has_three_in_line(self: Player, new_pos: tuple[int, int]) -> bool:
        return new_pos not in self.allowed

    def play(
        self: Player,
        choice: tuple[int, int] | None = None,
    ) -> tuple[int, int] | Literal[False]:
        """Play a move on the grid.

        !!! warning
            Absolutly not use grid.play after this method, it's already done here.

            This would break a lot of things.

            The returned value should only be used to display the move or transmit
            it to another player.

        Returns:
            The position played.
        """

        # We make sure to keep the empties up to date in case another player
        # has played before us
        self.availables -= self.grid.played
        self.allowed -= self.grid.played

        if choice is None:
            choice = self._choose()

        self._add_new_pos(choice)
        if self._busted:
            return False

        self.grid.play(*choice)
        self.played.add(choice)

        return choice

    def __hash__(self: Player) -> int:
        return hash(self.id)
