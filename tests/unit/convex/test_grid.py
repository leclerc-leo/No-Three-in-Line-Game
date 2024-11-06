from game.convex import grid


def test_no_instructions() -> None:

    g = grid.Grid([])

    assert g.g == {(0, 0): 0}


def test_one_instruction() -> None:

    g = grid.Grid([(1, 0)])

    assert g.g == {(0, 0): 0, (1, 0): 0}


def test_multiples_instructions() -> None:

    g = grid.Grid(
        [
            (1, 0),
            (1, 0),
            (0, 1),
            (0, 2),
        ],
    )

    assert g.g == {(x, y): 0 for x in range(3) for y in range(4)}


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

    assert g1.g == g2.g
