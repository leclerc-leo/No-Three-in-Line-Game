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
  }
}
