import { Component } from '@angular/core';
import { webSocket, WebSocketSubject } from 'rxjs/webSocket';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent {

  connect(){
    console.log('connect');
    var connection = webSocket("ws://localhost:8000");
    connection.subscribe(
      msg => console.log('message received: ' + msg),
      err => console.log(err),
      () => console.log('complete')
    );


  }

  sendMessage(){
    console.log('sendMessage');
  }

}
