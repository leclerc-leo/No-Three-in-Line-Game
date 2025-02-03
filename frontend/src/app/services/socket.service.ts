import { ApplicationRef, inject, Injectable } from '@angular/core';
import { first } from 'rxjs';
import { io, Socket } from 'socket.io-client';

@Injectable({
  providedIn: 'root'
})
export class socketService {

  private socket: Socket;

  constructor() {
    // https://www.reddit.com/r/Angular2/comments/1dpdbxy/socketioclient_causing_internal_server_error_page/
    this.socket = io('http://localhost:5000', { autoConnect: false });

    inject(ApplicationRef).isStable.pipe(
      first((isStable) => isStable))
    .subscribe(() => { this.socket.connect() });
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  public registerEvent(event: string, callback: (...args: any[]) => void): void {
    this.socket.on(event, callback);
  }

  public unregisterEvent(event: string): void {
    this.socket.off(event);
  }

  public emit(event: string, ...args: unknown[]): void {
    this.socket.emit(event, ...args);
  }

  public disconnect(): void { this.socket.disconnect(); }
}
