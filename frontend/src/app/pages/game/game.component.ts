import { ChangeDetectorRef, Component, OnDestroy } from '@angular/core';
import { socketService } from '../../services/socket.service';
import { gameService } from '../../services/game.service';
import { NgClass, NgFor } from '@angular/common';
import { localService } from '../../services/local.service';

@Component({
  selector: 'app-game-lobby',
  imports: [NgFor, NgClass],
  templateUrl: './game.component.html',
  styleUrls: ['./game.component.css']
})
export class GameComponent implements OnDestroy {

  public board_width: number;
  public board_height: number;

  constructor(
    private socket: socketService,
    private cdr: ChangeDetectorRef,
    private game: gameService,
  ) {

    console.log(game);
    console.log(this.game.turn === this.game.getPlayerId(localService.getPlayerId()));

    this.board_width = Math.max(...this.game.board.map((cell) => cell[1] + 1));
    this.board_height = Math.max(...this.game.board.map((cell) => cell[2] + 1));

    this.socket.registerEvent('game:update', this.updateBoard.bind(this));
  }

  public inBoard(cell: [number, number]): boolean {
    return this.game.board.some((boardCell) => boardCell[1] === cell[0] && boardCell[2] === cell[1]);
  }


  public isPlayed(cell: [number, number]): boolean {
    return this.game.board.some((boardCell) => boardCell[1] === cell[0] && boardCell[2] === cell[1] && boardCell[0]);
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
      return;
    }

    if (this.game.turn !== this.game.getPlayerId(localService.getPlayerId())) {
      return;
    }

    this.socket.emit('game:play', this.game.game_id, ...cell);
  }

  private updateBoard(board: [boolean, number, number, string[]][]): void {
    this.game.board = board;
    this.game.turn = (this.game.turn + 1) % this.game.players.length;
    this.cdr.detectChanges();
  }

  ngOnDestroy(): void {
    this.socket.unregisterEvent('game:update');
  }

}
