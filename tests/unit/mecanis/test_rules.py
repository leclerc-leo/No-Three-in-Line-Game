from game.mecanics import rules


def test_not_a_line() -> None:

    assert not rules._is_on_same_line(
        (0, 0),
        (1, 1),
        (2, 0),
    )


def test_horizontal_lines() -> None:

    assert rules._is_on_same_line(
        (0, 0),
        (1, 0),
        (2, 0),
    )

    assert rules._is_on_same_line(
        (0, 0),
        (3, 0),
        (10, 0),
    )


def test_vertical_lines() -> None:

    assert rules._is_on_same_line(
        (0, 0),
        (0, 1),
        (0, 2),
    )

    assert rules._is_on_same_line(
        (0, 0),
        (0, 3),
        (0, 10),
    )


def test_diagonal_lines() -> None:

    assert rules._is_on_same_line(
        (0, 0),
        (1, 1),
        (2, 2),
    )

    assert rules._is_on_same_line(
        (0, 0),
        (3, 3),
        (10, 10),
    )

def test_discrete_diagonal_lines() -> None:

    assert rules._is_on_same_line(
        (0, 0),
        (1, 2),
        (2, 4),
    )

    assert rules._is_on_same_line(
        (0, 0),
        (6, 3),
        (20, 10),
    )
