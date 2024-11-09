from game.mecanics import rules


def test_get_three_in_line_no_lines() -> None:

    played = {(0, 0), (1, 1), (2, 0)}

    assert not rules.has_three_in_line(played)


def test_get_three_in_line_horizontal() -> None:

    played = {(0, 0), (1, 0), (2, 0)}

    assert rules.has_three_in_line(played)


def test_get_three_in_line_vertical() -> None:

    played = {(0, 0), (0, 1), (0, 2)}

    assert rules.has_three_in_line(played)


def test_get_three_in_line_diagonal() -> None:

    played = {(0, 0), (1, 1), (2, 2)}

    assert rules.has_three_in_line(played)


def test_get_three_in_line_multiple_lines() -> None:

    played = {(0, 0), (1, 1), (2, 2), (0, 1), (0, 2)}

    assert rules.has_three_in_line(played)
