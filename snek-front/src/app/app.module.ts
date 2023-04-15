import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { NgxSnakeModule } from 'ngx-snake';

import { AppComponent } from './app.component';
import { HomeComponent } from './components/home/home.component';


@NgModule({
  declarations: [
    AppComponent,
    HomeComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    NgxSnakeModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
