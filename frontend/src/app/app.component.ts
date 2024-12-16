import { Component, OnDestroy } from '@angular/core';
import { RouterModule } from '@angular/router';
import { socketService } from './services/socket.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  imports: [RouterModule],
  providers: [socketService],
})
export class AppComponent implements OnDestroy {

  constructor(private socket: socketService) {}

  ngOnDestroy() {
    this.socket.disconnect();
  }
}
