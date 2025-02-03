import { Routes } from '@angular/router';
import { GameLobbyComponent } from './pages/game-lobby/game-lobby.component';
import { HomeComponent } from './pages/home/home.component';
import { GameComponent } from './pages/game/game.component';
import { PuzzlesComponent } from './pages/puzzles/puzzles.component';

export const routes: Routes = [
  {path: 'puzzles', component: PuzzlesComponent},
  {path: 'game-lobby', component: GameLobbyComponent},
  {path: 'game', component: GameComponent},
  {path: '', component: HomeComponent}
];
