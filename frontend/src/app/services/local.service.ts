import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class localService {

  constructor() {}

  public static getPlayerId(): string {
    let player_id = localStorage.getItem('player_id');

    if (player_id === null) {
      player_id = Math.random().toString(36).substring(7);
      localStorage.setItem('player_id', player_id);
    }

    return player_id;
  }

}
