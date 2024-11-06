from game.cmd import main


def test_main() -> None:
    assert main.main() == 0
