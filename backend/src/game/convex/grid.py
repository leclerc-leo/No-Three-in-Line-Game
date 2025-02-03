from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib.figure
import matplotlib.patches
import matplotlib.pyplot as plt

if TYPE_CHECKING:
    import pathlib

    from game.players import player


def get_positions(
    height: int,
    width: int,
    slope: tuple[int, int],
    intercept: tuple[int, int],
) -> set[tuple[int, int]]:

    result = set()

    if intercept[1] == 0 and slope == (1, 0):  # Vertical line
        for i in range(height):
            result.add((intercept[0], i))
        return result

    if intercept[0] == 0 and slope == (0, 1):  # Horizontal line
        for i in range(width):
            result.add((i, intercept[1]))
        return result

    intercept_value, x_offset = intercept
    normalized_dx, normalized_dy = slope

    for i in range(x_offset, width, normalized_dx):
        result.add((i, (intercept_value + i * normalized_dy) // normalized_dx))

    return result


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
        return get_positions(self.height, self.width, slope, intercept)

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
                        color=colors[hash(player.id) % len(colors)],
                        fill=True,
                    ),
                )

        for x, y in self.board:
            plt.gca().add_patch(matplotlib.patches.Rectangle((x, y), 1, 1, fill=None))

        return plt.gcf()

    def toJSON(self: Grid) -> list[tuple[bool, int, int, list[str]]]:  # noqa: N802

        # players shouldn't be able to play the same position so shouldn't be an issue
        played = [(True, *pos, [player.id]) for player in self.players for pos in player.played]

        allowed = [
            (False, *pos, [player.id for player in self.players if pos in player.allowed])
            for pos in self.board - self.played
        ]

        return played + allowed
