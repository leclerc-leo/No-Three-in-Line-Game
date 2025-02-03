import { Component, OnDestroy } from '@angular/core';
import { socketService } from '../../services/socket.service';
import { Router } from '@angular/router';
import { localService } from '../../services/local.service';
import { gameService } from '../../services/game.service';

@Component({
  selector: 'app-game-lobby',
  imports: [],
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css'],
})
export class HomeComponent implements OnDestroy {

  constructor(
    private socket: socketService,
    private router: Router,
    private game: gameService,
  ) {
    this.socket.registerEvent('selection:game_created',
      (game_infos: {game_id: number, heuristics: number[]}) =>
      {

      this.game.game_id = game_infos.game_id;
      this.game.availableHeuristics = game_infos.heuristics;
      this.router.navigate(['/game-lobby']);
    });

    this.socket.registerEvent('selection:puzzles',
      (game_infos: {
        game_id: number,
        board: [boolean, number, number, string[]][],
        completions: {[dif: string]: [number, number][][],},
        allowed: [number, number][],
        puzzle: {difficulty: string, index: number},
      }) =>
      {
        this.game.game_id = game_infos.game_id;
        this.game.board = game_infos.board;
        this.game.allowed[localService.getPlayerId()] = game_infos.allowed;
        this.game.completions = game_infos.completions;
        this.game.puzzle = game_infos.puzzle;
        console.log(this.game.completions);

        this.game.player_to_id = {
          [localService.getPlayerId()]: 0,
        };
        this.game.players = [[0, localService.getPlayerId(), null]];

        this.router.navigate(['/puzzles']);
      }
    );
  }

  createGame() {
    this.socket.emit(
      'selection:create_game',
      localService.getPlayerId(),
    );
  }

  joinGame() {
    // TODO LATER
    console.log('joinGame');
  }

  ngOnDestroy(): void {
    this.socket.unregisterEvent('selection:game_created');
    this.socket.unregisterEvent('selection:puzzles');
  }

  puzzles(): void {
    this.socket.emit(
      'selection:puzzles',
      localService.getPlayerId(),
    );
  }
}
