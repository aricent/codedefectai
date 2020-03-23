import { Component, OnInit } from '@angular/core';
import { GlobalService } from 'src/app/global.service';

@Component({
  selector: 'app-dashboard-container',
  templateUrl: './dashboard-container.component.html',
  styleUrls: ['./dashboard-container.component.css']
})
export class DashboardContainerComponent implements OnInit {

  constructor(public _globalService:GlobalService){

  }

  ngOnInit() {
  }
  hideNotification()
  {
    this._globalService.showNotification=false;
  }

}
