import { Injectable } from '@angular/core';
import { Router } from '@angular/router';

@Injectable({
  providedIn: 'root'
})
export class gameService {

  public game_id: number = -1;
  public availableHeuristics: number[] = [];
  public board: [boolean, number, number, string[]][] = [];
  public players: [0 | 1, string, number | null][] = [];
  public turn: number = 0;

  public player_to_id: { [player: string]: number } = {};

  constructor(
    private router: Router,
  ) {

    if (this.game_id == -1) { this.router.navigate(['/']); }
  }

  public getPlayerId(player: string): number {
    return this.player_to_id[player];
  }

}
