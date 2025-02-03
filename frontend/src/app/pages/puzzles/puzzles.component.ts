import { ChangeDetectorRef, Component, OnDestroy } from '@angular/core';
import { socketService } from '../../services/socket.service';
import { localService } from '../../services/local.service';
import { gameService } from '../../services/game.service';
import { NgClass, NgFor, NgIf } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-puzzles',
  imports: [NgFor, NgClass, NgIf, FormsModule],
  templateUrl: './puzzles.component.html',
  styleUrls: ['./puzzles.component.css'],
})
export class PuzzlesComponent implements OnDestroy {

  public board_width: number;
  public board_height: number;
  public has_ended: boolean = false;

  public score: number = 0;
  public best_score: number;
  public old_best_score: number;

  public timer: number = -1;
  private timer_interval: NodeJS.Timeout | null = null;

  public competitif: boolean = false;

  constructor(
    private socket: socketService,
    private cdr: ChangeDetectorRef,
    public game: gameService,
  ) {

    this.best_score = this.game.completions[this.game.puzzle.difficulty][this.game.puzzle.index].length;
    this.old_best_score = this.best_score;

    this.board_width = Math.max(...this.game.board.map((cell) => cell[1] + 1));
    this.board_height = Math.max(...this.game.board.map((cell) => cell[2] + 1));

    this.socket.registerEvent('game:update', this.updateBoard.bind(this));
    this.socket.registerEvent('game:solo_end', this.endGame.bind(this));

    this.socket.registerEvent('selection:puzzles',
      (game_infos: {
        game_id: number,
        board: [boolean, number, number, string[]][],
        completions: {[dif: string]: [number, number][][],},
        allowed: [number, number][],
        puzzle: {difficulty: string, index: number},
      }) =>
      {
        this.timer = -1;
        if (this.timer_interval !== null) clearInterval(this.timer_interval);
        this.timer_interval = null;

        this.has_ended = false;
        this.score = 0;
        this.game.game_id = game_infos.game_id;
        this.game.board = game_infos.board;
        this.game.allowed[localService.getPlayerId()] = game_infos.allowed;
        this.game.completions = game_infos.completions;
        this.game.puzzle = game_infos.puzzle;

        this.best_score = this.game.completions[this.game.puzzle.difficulty][this.game.puzzle.index].length;
        this.old_best_score = this.best_score;

        this.game.player_to_id = {
          [localService.getPlayerId()]: 0,
        };
        this.game.players = [[0, localService.getPlayerId(), null]];

        this.board_width = Math.max(...this.game.board.map((cell) => cell[1] + 1));
        this.board_height = Math.max(...this.game.board.map((cell) => cell[2] + 1));

        this.cdr.detectChanges();
      }
    );
  }

  public startGame(): void {
    this.timer = 0;
    this.timer_interval = setInterval(() => {
      this.timer += 1;
      this.cdr.detectChanges();
    }, 1000);

    this.score = this.game.board.filter((cell) => cell[0]).length;
    this.cdr.detectChanges();
  }

  public displayTimer(): string {
    if (this.timer === -1) {
      return '00 : 00';
    }

    const minutes = Math.floor(this.timer / 60);
    const seconds = this.timer % 60;
    return `${minutes.toString().padStart(2, '0')} : ${seconds.toString().padStart(2, '0')}`;
  }

  public inBest(cell: [number, number]): boolean {
    const best_grid = this.game.completions[this.game.puzzle.difficulty][this.game.puzzle.index];

    if (best_grid.length === 0) return false;

    return best_grid.some((boardCell) => boardCell[0] === cell[0] && boardCell[1] === cell[1]);
  }

  public inBoard(cell: [number, number]): boolean {
    const res = this.game.board.some((boardCell) => boardCell[1] === cell[0] && boardCell[2] === cell[1])
    return res;
  }


  public isPlayed(cell: [number, number]): boolean {
    return this.game.board.some((boardCell) => boardCell[1] === cell[0] && boardCell[2] === cell[1] && boardCell[0]);
  }

  public isAllowed(cell: [number, number]): boolean {
    const player_allowed = this.game.allowed[this.game.players[0][1]];

    if (player_allowed === undefined) return false;

    return player_allowed.some((allowed) => allowed[0] === cell[0] && allowed[1] === cell[1]);
  }

  public getCellPlayer(cell: [number, number]): number {
    for (const boardCell of this.game.board) {
      if (boardCell[1] === cell[0] && boardCell[2] === cell[1]) {
        return this.game.player_to_id[boardCell[3][0]];
      }
    }
    return 5;
  }

  public play(cell: [number, number]): void {

    if (!this.inBoard(cell) || this.isPlayed(cell)) {
      console.log('play: not in board or already played');
      return;
    }

    if (this.game.turn !== this.game.getPlayerId(localService.getPlayerId())) {
      console.log('play: not your turn', this.game.turn, this.game.getPlayerId(localService.getPlayerId()));
      return;
    }

    this.score += 1;

    this.socket.emit('game:play', this.game.game_id, ...cell);
  }

  public select(
    dif: string,
    index: number,
  ): void {

    this.socket.emit('game:leave', this.game.game_id);

    this.socket.emit(
      'selection:puzzles',
      localService.getPlayerId(),
      dif,
      index,
      this.competitif,
    );
  }

  private updateBoard(infos : {
      board: [boolean, number, number, string[]][],
      allowed: [number, number][],
    }): void {

    this.game.board = infos.board;
    this.game.allowed[this.game.players[this.game.turn][1]] = infos.allowed;
    this.game.turn = (this.game.turn + 1) % this.game.players.length;
    this.cdr.detectChanges();
  }

  private endGame(infos : {
    best_score: number,
    score: number,
    completions: { [dif: string]: [number, number][][] },
    board: [boolean, number, number, string[]][],
  }): void {
    this.game.completions = infos.completions;
    this.game.board = infos.board;
    this.game.allowed = {};
    this.has_ended = true;
    this.old_best_score = infos.best_score;
    this.score = infos.score;

    this.best_score = infos.best_score > infos.score ? infos.best_score : infos.score;

    if (this.timer_interval !== null) clearInterval(this.timer_interval);
    this.timer_interval = null;

    this.cdr.detectChanges();
    this.game.reset();
  }

  ngOnDestroy(): void {
    if (this.timer_interval !== null) clearInterval(this.timer_interval);
    this.socket.unregisterEvent('game:update');
    this.socket.unregisterEvent('game:solo_end');
    this.socket.unregisterEvent('selection:puzzles');

    this.socket.emit('game:leave', this.game.game_id);
  }

}
