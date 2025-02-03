from __future__ import annotations

import json
import pathlib
import random
from typing import Literal

import flask
import flask_socketio

from game.convex import grid
from game.players import heuristics, player

DEBUG = True

HUMAN: Literal[0] = 0
HEURISTIC: Literal[1] = 1

app = flask.Flask(__name__)
app.config["SECRET_KEY"] = "5VZwb6O0NJgNBsBkXgO4VFgXkhbfIPmaW5P"  # noqa: S105 - dev purposes only

socketio = flask_socketio.SocketIO(
    app,
    debug=DEBUG,
    cors_allowed_origins="*",
)


class Human(player.Player):

    def __init__(
        self: Human,
        pid: str,
        g: grid.Grid,
    ) -> None:

        super().__init__(pid, g)

    def _choose(self: Human) -> tuple[int, int]:
        return (-1, -1)

    def _update_availables(
        self: Human,
        slope: tuple[int, int],
        intercept: tuple[int, int],
    ) -> None:
        pass


lobbies: dict[int, list[tuple[Literal[0, 1], str, int | None]]] = {}
""" Represents the state of games before they are started.

    There is a list of the players which are represented by
    - the type of player (0 for human, 1 for heuristic)
    - the player's id (unique player identifier or generated heuristic id)
    - the heuristic level (None if the player is a human)
"""
games: dict[int, tuple[grid.Grid, list[player.Player], int, int]] = {}
""" Represents the state of games after they are started.

    There is a tuple of
    - the grid
    - the list of players (in order of play)
    - the current player index
    - the current turn start time (in milliseconds, to be used for timeouts)
"""
solo_games: dict[int, tuple[str, int]] = {}

client_to_game: dict[str, int] = {}

puzzles_games: dict[str, list[list[tuple[int, int]]]] = {}
with (pathlib.Path(__file__).parent / "puzzles.json").open() as f:
    p_data = json.load(f)
    """
    The puzzles data is a dictionary with the following structure:
    {
        "Facile": [ # difficulty
            [(x, y), (x, y), ...], # puzzles
            ...
        ],
        "Moyen": [
            ...
        ],
        "Difficile": [
            ...
        ]
    }
    """

    puzzles_games = {dif: [list(puzzles[1:]) for puzzles in p_data[dif]] for dif in p_data}

puzzles_completions: dict[str, dict[str, list[list[tuple[int, int]]]]] = {}

heuristics_levels: dict[int, tuple[Literal[0, 1], Literal[3]]] = {
    0: (0, 3),
    1: (1, 3),
}


@socketio.on("selection:create_game")
def create_game(client_id: str) -> None:

    lobby_id: int | None = None
    i = 0

    while lobby_id is None or lobby_id in lobbies:
        lobby_id = int(abs(hash(str(lobbies) + str(i))) // 1e9)
        i += 1

    lobbies[lobby_id] = [(HUMAN, client_id, None)]
    client_to_game[client_id] = lobby_id

    socketio.emit(
        "selection:game_created",
        {
            "game_id": lobby_id,
            "heuristics": list(heuristics_levels.keys()),
        },
    )

    flask_socketio.join_room(str(lobby_id))


@socketio.on("selection:add_heuristic")
def add_heuristic(lobby_id: int, level: int) -> None:

    if lobby_id not in lobbies:
        return

    heur_ids = {hid for (typ, hid, _) in lobbies[lobby_id] if typ == HEURISTIC}

    heur_id = 0
    while str(heur_id) in heur_ids:
        heur_id += 1

    lobbies[lobby_id].append((1, str(heur_id), level))

    # send an update to all players in the room
    socketio.emit("selection:update_game", lobbies[lobby_id], to=str(lobby_id))


@socketio.on("selection:remove_player")
def remove_player(lobby_id: int, typ: int, pid: str) -> None:

    lobbies[lobby_id] = [e for e in lobbies[lobby_id] if not (e[0] == typ and e[1] == pid)]

    socketio.emit("selection:update_game", lobbies[lobby_id], to=str(lobby_id))


@socketio.on("selection:start_game")
def start_game(lobby_id: int) -> None:

    lobby = lobbies.pop(lobby_id)
    random.shuffle(lobby)

    play_grid = grid.Grid([(1, 0), (1, 1), (2, 1), (-1, 1), (-2, 1), (0, 1), (1, 2)])

    players: list[player.Player] = []
    for member in lobby:

        if member[0] == HEURISTIC and member[2] is not None and member[2] in heuristics_levels:

            heur = heuristics.Heuristic(member[1], play_grid, *heuristics_levels[member[2]])
            players.append(heur)

        else:
            players.append(Human(member[1], play_grid))

    games[lobby_id] = (play_grid, players, 0, -1)

    socketio.emit(
        "game:game_started",
        {"board": play_grid.toJSON(), "lobby": lobby},
        to=str(lobby_id),
    )


def end_solo(lobby_id: int) -> None:

    difficulty, dif_index = solo_games.pop(lobby_id)
    puzzle_grid, [player], _, _ = games.pop(lobby_id)

    if difficulty not in puzzles_completions[player.id]:
        puzzles_completions[player.id][difficulty] = []

    if dif_index >= len(puzzles_completions[player.id][difficulty]):
        puzzles_completions[player.id][difficulty].append([])

    completion = puzzles_completions[player.id][difficulty][dif_index]

    if len(completion) < len(player.played):
        puzzles_completions[player.id][difficulty][dif_index] = list(player.played)

    socketio.emit(
        "game:solo_end",
        {
            "best_score": len(completion),
            "score": len(player.played),
            "completions": puzzles_completions[player.id],
            "board": puzzle_grid.toJSON(),
        },
        to=str(lobby_id),
    )

    flask_socketio.leave_room(str(lobby_id))


@socketio.on("game:play")
def play(lobby_id: int, x: int, y: int) -> None:

    def handle_end() -> None:
        if len(game[1]) == 1:
            end_solo(lobby_id)

    # would be best later to have some king of private key to prevent
    # someone from playing in someone else's turn

    if lobby_id not in games:
        return

    game = games[lobby_id]
    current_player = game[1][game[2]]

    if not isinstance(current_player, Human):
        return

    res = current_player.play((x, y))

    if not res:
        # choose wrong square (shouldn't happen)
        handle_end()
        return

    games[lobby_id] = (game[0], game[1], (game[2] + 1) % len(game[1]), -1)

    if len(current_player.allowed) == 0:
        # player has no more moves
        handle_end()
        return

    socketio.emit(
        "game:update",
        {
            "board": game[0].toJSON(),
            "allowed": list(current_player.allowed),
        },
        to=str(lobby_id),
    )


@socketio.on("selection:puzzles")
def puzzles(
    client_id: str,
    difficulty: str = "Facile",
    index: int = 0,
    competitif: bool = False,  # noqa: FBT002, FBT001
) -> None:

    play_grid = grid.Grid(puzzles_games[difficulty][index])

    lobby_id = int(abs(hash(str(puzzles_completions) + str(client_id)) // 1e9))
    lobbies[lobby_id] = [(HUMAN, client_id, None)]

    p = Human(client_id, play_grid)
    games[lobby_id] = (play_grid, [p], 0, -1)
    solo_games[lobby_id] = (difficulty, index)

    if client_id not in puzzles_completions:
        puzzles_completions[client_id] = {
            dif: [[] for _ in puzzles_games[dif]] for dif in puzzles_games
        }

    if not competitif:
        for _ in range(4):
            p.play(random.choice(list(p.allowed)))  # noqa: S311

    socketio.emit(
        "selection:puzzles",
        {
            "game_id": lobby_id,
            "board": play_grid.toJSON(),
            "completions": puzzles_completions[client_id],
            "allowed": list(p.allowed),
            "puzzle": {"difficulty": difficulty, "index": index},
        },
    )

    flask_socketio.join_room(str(lobby_id))


@socketio.on("game:leave")
def leave(lobby_id: int) -> None:

    if lobby_id in games:
        games.pop(lobby_id)
    if lobby_id in solo_games:
        solo_games.pop(lobby_id)
    if lobby_id in lobbies:
        lobbies.pop(lobby_id)

    flask_socketio.leave_room(str(lobby_id))


if __name__ == "__main__":
    socketio.run(app, debug=DEBUG, allow_unsafe_werkzeug=True)

# DO NOT PUT ANYTHING HERE
