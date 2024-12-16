import re

import pytest
from game.convex import grid


def test_no_instructions() -> None:

    g = grid.Grid([])

    assert g.board == {(0, 0)}


def test_one_instruction() -> None:

    g = grid.Grid([(1, 0)])

    assert g.board == {(0, 0), (1, 0)}


def test_multiples_instructions() -> None:

    g = grid.Grid(
        [
            (1, 0),
            (1, 0),
            (0, 1),
            (0, 2),
        ],
    )

    assert g.board == {(x, y) for x in range(3) for y in range(4)}


def test_associativity() -> None:

    instructions = [
        (1, 0),
        (1, 1),
        (2, 1),
        (-1, 1),
        (-2, 1),
        (0, 1),
        (1, 2),
        (-1, 2),
    ]

    g1 = grid.Grid(instructions)
    g2 = grid.Grid(list(reversed(instructions)))

    assert g1.board == g2.board


def test_play_out_of_grid() -> None:
    g = grid.Grid([(1, 0), (0, 1)])
    with pytest.raises(ValueError, match=re.escape("Position (2, 2) is out of the board.")):
        g.play(2, 2)


def test_play_already_played_position() -> None:
    g = grid.Grid([(1, 0), (0, 1)])
    g.play(1, 0)
    with pytest.raises(ValueError, match=re.escape("Position (1, 0) is already played.")):
        g.play(1, 0)
