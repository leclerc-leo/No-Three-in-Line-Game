from __future__ import annotations

import unittest
from unittest.mock import MagicMock

from game.convex import grid
from game.players import heuristics


class TestLevelOne(unittest.TestCase):

    def setUp(self: TestLevelOne) -> None:
        self.grid = MagicMock(spec=grid.Grid)
        self.grid.empties = {(0, 0), (1, 1), (2, 2)}
        self.grid.board = self.grid.empties.copy()
        self.grid.played = set()
        self.grid.players = set()
        self.grid.play = MagicMock()

    def test_play(self: TestLevelOne) -> None:
        level_one = heuristics.Heuristic(self.grid, 0, 0)
        choice = level_one.play()
        assert choice in {(0, 0), (1, 1), (2, 2)}
        self.grid.play.assert_called_once_with(*choice)


class TestLevelTwo(unittest.TestCase):

    def setUp(self: TestLevelTwo) -> None:
        self.grid = MagicMock(spec=grid.Grid)
        self.grid.empties = {
            (2, 0),
            (1, 1),
            (0, 2),
            (1, 2),
        }
        self.grid.played = {
            (0, 0),
            (0, 1),
            (1, 0),
            (2, 1),
            (2, 2),
        }
        self.grid.board = self.grid.played.union(self.grid.empties)
        self.grid.players = set()
        self.grid.play = MagicMock()

    def test_play(self: TestLevelTwo) -> None:
        level_two = heuristics.Heuristic(self.grid, 0, 1)
        level_two._allowed = {(1, 2)}
        level_two.availables = {(1, 2)}
        choice = level_two.play()
        assert choice == (1, 2)
        self.grid.play.assert_called_once_with(*choice)


if __name__ == "__main__":
    unittest.main()
