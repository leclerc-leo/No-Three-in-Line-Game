from __future__ import annotations

import unittest
from unittest.mock import MagicMock

import pytest
from game.convex import grid
from game.mecanics import heuristics


class InvalidHeuristics(unittest.TestCase):

    def test_invalid_player_id(self: InvalidHeuristics) -> None:
        with pytest.raises(ValueError, match="player_id must be greater than 0."):
            heuristics.Heuristic(MagicMock(spec=grid.Grid), 0, 1)

    def test_invalid_level(self: InvalidHeuristics) -> None:
        with pytest.raises(
            ValueError,
            match=f"level must be in {set(heuristics._int_to_func.keys())}.",
        ):
            heuristics.Heuristic(MagicMock(spec=grid.Grid), 1, 0)


class TestLevelOne(unittest.TestCase):

    def setUp(self: TestLevelOne) -> None:
        self.grid = MagicMock(spec=grid.Grid)
        self.grid.get_empty_positions.return_value = [(0, 0), (1, 1), (2, 2)]
        self.grid.play = MagicMock()

    def test_play(self: TestLevelOne) -> None:
        level_one = heuristics.Heuristic(self.grid, 1, 1)
        choice = level_one.play()
        assert choice in {(0, 0), (1, 1), (2, 2)}
        self.grid.play.assert_called_once_with(*choice, 1)


class TestLevelTwo(unittest.TestCase):

    def setUp(self: TestLevelTwo) -> None:
        self.grid = MagicMock(spec=grid.Grid)
        self.grid.get_empty_positions.return_value = {
            (2, 0),
            (1, 1),
            (0, 2),
            (1, 2),
        }
        self.grid.get_played_positions.return_value = {
            (0, 0),
            (0, 1),
            (1, 0),
            (2, 1),
            (2, 2),
        }
        self.grid.play = MagicMock()

    def test_play(self: TestLevelTwo) -> None:
        level_two = heuristics.Heuristic(self.grid, 1, 2)
        choice = level_two.play()
        assert choice == (1, 2)
        self.grid.play.assert_called_once_with(*choice, 1)


if __name__ == "__main__":
    unittest.main()
