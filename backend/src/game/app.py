from __future__ import annotations

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
client_to_game: dict[str, int] = {}

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


@socketio.on("game:play")
def play(lobby_id: int, x: int, y: int) -> None:

    # would be best later to have some king of private key to prevent
    # someone from playing in someone else's turn

    game = games[lobby_id]
    current_player = game[1][game[2]]

    if not isinstance(current_player, Human):
        return

    res = current_player.play((x, y))

    if not res:
        return

    games[lobby_id] = (game[0], game[1], (game[2] + 1) % len(game[1]), -1)

    socketio.emit(
        "game:update",
        game[0].toJSON(),
        to=str(lobby_id),
    )


if __name__ == "__main__":
    socketio.run(app, debug=DEBUG, allow_unsafe_werkzeug=True)

# DO NOT PUT ANYTHING HERE
