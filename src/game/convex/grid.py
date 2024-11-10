from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib.figure
import matplotlib.patches
import matplotlib.pyplot as plt

if TYPE_CHECKING:
    import pathlib

    from game.players import player


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

        self.players: set[player.Player] = set()

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

    def get_positions(
        self: Grid,
        slope: tuple[int, int],
        intercept: tuple[int, int],
    ) -> set[tuple[int, int]]:

        if intercept[1] == 0 and slope == (1, 0):  # Vertical line
            return {
                (intercept[0], y) for y in range(self.height) if (intercept[0], y) in self.board
            }

        if intercept[0] == 0 and slope == (0, 1):  # Horizontal line
            return {(x, intercept[1]) for x in range(self.width) if (x, intercept[1]) in self.board}

        intercept_value, x_offset = intercept
        normalized_dx, normalized_dy = slope

        # find the first point that is on the line
        x = x_offset
        y = (intercept_value + x * normalized_dy) // normalized_dx

        positions = set()

        # possible to optimize since we know the dimension of the board
        while 0 <= x < self.width:

            if (x, y) in self.board:
                positions.add((x, y))

            x += normalized_dx
            y += normalized_dy

        return positions

    def to_image(
        self: Grid,
    ) -> matplotlib.figure.Figure:

        plt.figure()
        plt.axis("off")

        plt.gca().set_aspect("equal", adjustable="box")

        plt.plot(0, 0, "k.", markersize=1)

        for player in self.players:
            colors = ["red", "green", "blue", "purple", "orange", "pink", "brown"]

            for x, y in player.played:
                plt.gca().add_patch(
                    matplotlib.patches.Circle(
                        (x + 0.5, y + 0.5),
                        0.4,
                        color=colors[player.id % len(colors)],
                        fill=True,
                    ),
                )

        for x, y in self.board:
            plt.gca().add_patch(matplotlib.patches.Rectangle((x, y), 1, 1, fill=None))

        return plt.gcf()
