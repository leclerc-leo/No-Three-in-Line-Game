import { Component, ChangeDetectorRef, OnDestroy } from '@angular/core';
import { FormsModule } from '@angular/forms'
import { socketService } from '../../services/socket.service';
import { NgFor, NgIf } from '@angular/common';
import { Router } from '@angular/router';
import { localService } from '../../services/local.service';
import { gameService } from '../../services/game.service';

type Player = {
  type: -1 | 0 | 1,
  id: string,
  hlvl: number | null
};

@Component({
  selector: 'app-game-lobby',
  imports: [NgFor, FormsModule, NgIf],
  templateUrl: './game-lobby.component.html'
})
export class GameLobbyComponent implements OnDestroy {
  game_id: number;
  players: Player[]= [];
  heuristics: number[];
  player_id: string;
  canCreateGame: boolean = false;

  selectedHeuristic: number = -1;

  constructor(
    private socket: socketService,
    private cdr: ChangeDetectorRef,
    private router: Router,
    private game: gameService
  ) {

    // to expose to the html, there is probably a better way.
    this.game_id = this.game.game_id;
    this.heuristics = this.game.availableHeuristics;
    this.player_id = localService.getPlayerId();

    this.updateHeuristic([[0, localService.getPlayerId(), null]], false)


    this.socket.registerEvent("selection:update_game", this.updateHeuristic.bind(this));
    this.socket.registerEvent("game:game_started", this.gameStarted.bind(this));
  }

  addHeuristic() {
    if (this.game_id == -1) { return; }
    if (this.selectedHeuristic == -1) { return; }
    if (! this.players.some((player) => player.type === -1)) { return; }

    this.socket.emit(
      'selection:add_heuristic',
      this.game_id,
      this.selectedHeuristic,
    );
  }

  removePlayer(player: Player) {
    if (this.game_id == -1) { return; }

    this.socket.emit(
      'selection:remove_player',
      this.game_id,
      player.type,
      player.id,
    );
  }

  updateHeuristic(players: [0 | 1, string, number | null][], update: boolean = true): void {

    this.players = players.map((player) => {
      return {
        type: player[0],
        id: player[1],
        hlvl: player[2],
      }
    });

    this.canCreateGame = this.players.length < 2

    const nb_players = this.players.length
    for (let i = 0; i < 4 - nb_players; i++) {
      this.players.push({type: -1, id: "-1", hlvl: null});
    }

    if (update) { this.cdr.detectChanges(); }
  }

  gameStarted(
    game_infos: {
      board: [boolean, number, number, string[]][],
      lobby: [0 | 1, string, number | null][],
    }
  ): void {
      this.game.board = game_infos.board;
      this.game.players = game_infos.lobby;

      for (let i = 0; i < this.game.players.length; i++) {
        this.game.player_to_id[this.game.players[i][1]] = i;
      }

      this.router.navigate(['/game']);
  }

  startGame() {
    this.socket.emit("selection:start_game", this.game_id);
  }

  ngOnDestroy(): void {
    this.socket.unregisterEvent("selection:update_game");
    this.socket.unregisterEvent("game:game_started");
  }
}
