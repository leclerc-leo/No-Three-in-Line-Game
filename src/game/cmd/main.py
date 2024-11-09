import pathlib

from game.convex import grid
from game.mecanics import rules


def main() -> int:
    import logging

    logging.basicConfig(level=logging.INFO)
    output_dir = pathlib.Path("output")
    output_dir.mkdir(exist_ok=True)

    g = grid.Grid(
        [
            (1, 0),
            (1, 1),
            (2, 1),
            (-1, 1),
            (-2, 1),
            (0, 1),
            (1, 2),
            (-1, 2),
        ],
    )

    g.display(output_dir)

    # To make it easier, we indicate position with a matrix of True/False
    # where True means a position is played
    played_matrix = [
        [False, True, False, False, True, False],
        [True, False, False, False, False, True],
        [False, False, True, False, True, False],
        [True, False, False, False, False, False],
        [False, False, False, True, False, True],
        [False, True, True, False, False, False],
    ]

    played = {(i, j) for i, row in enumerate(played_matrix) for j, val in enumerate(row) if val}

    logging.info(
        "3 alignes : %s",
        str(rules.has_three_in_line(played)),
    )

    return 0
