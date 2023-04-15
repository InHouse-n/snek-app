import { Component, ViewChild } from '@angular/core';
import { NgxSnakeComponent } from 'ngx-snake';
import { webSocket, WebSocketSubject } from 'rxjs/webSocket';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent {

  @ViewChild(NgxSnakeComponent)
  private _snake!: NgxSnakeComponent;
  private _snakeDirection: number = 1;

  public onRotateButtonPressed() {
    this._snake.actionReset();
  }

  startGame() {
    var connection = webSocket("ws://localhost:8000");
    connection.subscribe({
      next: direction => this.move(<number>direction),
      error: err => console.log(err),
      complete: () => console.log('complete'),
    }
    );

    this._snake.actionStart();    

    this._snake.grid$.subscribe({
      next: grid => connection.next({grid : grid, direction: this._snakeDirection}),
    })
  }

  move(dir: number) {
    switch (dir) {
      case 0:
        this._snake.actionLeft();
        this._snakeDirection = 0;
        break;
      case 1:
        this._snake.actionRight();
        this._snakeDirection = 1;
        break;
      case 2:
        this._snake.actionUp();
        this._snakeDirection = 2;
        break;
      case 3:
        this._snake.actionDown();
        this._snakeDirection = 3;
        break;
    }
  }

  sendMessage() {
    console.log('sendMessage');
  }

}