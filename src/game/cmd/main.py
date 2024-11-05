import pathlib

from game.convexe import grid
from game.mecanics import rules


def main() -> int:
    import logging

    logging.basicConfig(level=logging.INFO)
    output_dir = pathlib.Path("output")
    output_dir.mkdir(exist_ok=True)

    g = grid.Grid(
        {
            (1, 0),
            (1, 1),
            (2, 1),
            (-1, 1),
            (-2, 1),
            (0, 1),
            (1, 2),
            (-1, 2),
        },
    )

    g.display(output_dir)

    # pour simplifier les tests, j'utilise une matrice
    # qu'ensuite je convertis vers les positions avec les valeurs True
    played_matrix = [
        [False, True, False, False, True, False],
        [True, False, False, False, False, True],
        [False, False, True, False, True, False],
        [True, False, False, False, False, False],
        [False, False, False, True, False, True],
        [False, True, True, False, False, False],
    ]
    played_pos = {(i, j) for i, row in enumerate(played_matrix) for j, val in enumerate(row) if val}

    logging.info(
        "3 alignes : %s",
        str(
            rules.get_three_in_line(
                played_pos,
            ),
        ),
    )

    return 0
