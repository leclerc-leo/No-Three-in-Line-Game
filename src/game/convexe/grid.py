from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib.patches
import matplotlib.pyplot as plt

if TYPE_CHECKING:
    import pathlib


def _create(
    instructions: set[tuple[int, int]],
) -> set[tuple[int, int]]:
    """Crée une grille à partir d'instructions.

    !!! Example
        ```pycon
        >>> from pas_3_alignes.convexe import grid
        >>> g = grid.create(
        ...     {
        ...         (1, 0),
        ...         (1, 1),
        ...         (2, 1),
        ...     },
        ... )
        >>> g
        {(0, 0), (1, 0), (1, 1), (2, 1), (3, 1), (3, 2), (4, 2)}
        ```

    Args:
        instructions: Les instructions pour créer la grille.

    Returns:
        La grille créée à partir des instructions.
    """

    grid = {(0, 0)}

    for x_offset, y_offset in instructions:
        new_grid = grid.copy()

        for x, y in grid:
            new_grid.add((x + x_offset, y + y_offset))

        grid = new_grid

    # On normalise les coordonnées pour qu'elles soient toutes positives
    min_x = sum(x for x, _ in instructions if x < 0)
    min_y = sum(y for _, y in instructions if y < 0)

    return {(x - min_x, y - min_y) for x, y in grid}


class Grid:

    def __init__(
        self: Grid,
        instructions: set[tuple[int, int]],
    ) -> None:
        self.g = _create(instructions)

    def display(
        self: Grid,
        folder: pathlib.Path,
        played: set[tuple[int, int]] | None = None,
    ) -> None:

        played = played or set()  # permet de s'assurer que player est un set

        for x, y in self.g:
            plt.gca().add_patch(matplotlib.patches.Rectangle((x, y), 1, 1, fill=None))

        # zip(*self.g) est un tuple de deux listes (x, y)
        plt.scatter(*zip(*self.g))  # type: ignore[arg-type]

        plt.savefig(folder / "grid.png")
