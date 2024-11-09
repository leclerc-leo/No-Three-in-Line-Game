from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib.figure
import matplotlib.patches
import matplotlib.pyplot as plt

if TYPE_CHECKING:
    import pathlib


def _create(
    instructions: list[tuple[int, int]],
) -> set[tuple[int, int]]:
    """Create a convex grid from instructions.

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
        instructions: The instructions to create the grid.

    Returns:
        The created grid.
    """

    grid = {(0, 0)}

    for x_offset, y_offset in instructions:
        new_grid = grid.copy()

        for x, y in grid:
            new_grid.add((x + x_offset, y + y_offset))

        grid = new_grid

    # Normalize the grid to only have positive coordinates
    min_x = sum(x for x, _ in instructions if x < 0)
    min_y = sum(y for _, y in instructions if y < 0)

    return {(x - min_x, y - min_y) for x, y in grid}


class Grid:

    def __init__(
        self: Grid,
        instructions: list[tuple[int, int]],
    ) -> None:

        self.board = _create(instructions)

        self.width = max(x for x, _ in self.board) + 1
        self.height = max(y for _, y in self.board) + 1

        self.empties = self.board.copy()
        self.played: set[tuple[int, int]] = set()

    def play(
        self: Grid,
        x: int,
        y: int,
    ) -> None:

        if (x, y) not in self.board:
            msg = f"Position {(x, y)} is out of the board."
            raise ValueError(msg)

        if (x, y) in self.played:
            msg = f"Position {(x, y)} is already played."
            raise ValueError(msg)

        self.empties.remove((x, y))
        self.played.add((x, y))

    def display(
        self: Grid,
        folder: pathlib.Path,
    ) -> None:

        fig = self.to_image()

        fig.savefig(folder / "grid.png")

    def to_image(
        self: Grid,
    ) -> matplotlib.figure.Figure:

        plt.figure()
        plt.axis("off")

        plt.gca().set_aspect("equal", adjustable="box")

        plt.plot(0, 0, "k.", markersize=1)

        for x, y in self.played:
            plt.gca().add_patch(matplotlib.patches.Rectangle((x, y), 1, 1, color="red", fill=True))

        for x, y in self.empties:
            plt.gca().add_patch(matplotlib.patches.Rectangle((x, y), 1, 1, color="blue", fill=True))

        for x, y in self.board:
            plt.gca().add_patch(matplotlib.patches.Rectangle((x, y), 1, 1, fill=None))

        return plt.gcf()

    def __copy__(
        self: Grid,
    ) -> Grid:

        grid = Grid.__new__(Grid)
        grid.board = self.board.copy()
        grid.width = self.width
        grid.height = self.height
        grid.empties = self.empties.copy()
        grid.played = self.played.copy()

        return grid

    def __deepcopy__(
        self: Grid,
        memo: dict[int, Grid],
    ) -> Grid:

        grid = Grid.__new__(Grid)
        memo[id(self)] = grid

        grid.board = self.board.copy()
        grid.width = self.width
        grid.height = self.height
        grid.empties = self.empties.copy()
        grid.played = self.played.copy()

        return grid
