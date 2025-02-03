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
  public completions: { [dif: string]: [number, number][][] } = {};

  public player_to_id: { [player: string]: number } = {};
  public allowed: {[id : string]: [number, number][]} = {};
  public puzzle: {difficulty: string, index: number} = {difficulty: 'Facile', index: 0};

  constructor(
    private router: Router,
  ) {

    if (this.game_id == -1) { this.router.navigate(['/']); }
  }

  public getPlayerId(player: string): number {
    return this.player_to_id[player];
  }

  public reset(): void {
    this.game_id = -1;
    this.availableHeuristics = [];
    this.board = [];
    this.players = [];
    this.turn = 0;
    this.player_to_id = {};
  }

}
