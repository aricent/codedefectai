import { Component, OnInit } from '@angular/core';
import { GlobalService } from 'src/app/global.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-nav-course',
  templateUrl: './nav-course.component.html',
  styleUrls: ['./nav-course.component.css']
})
export class NavcourseComponent implements OnInit {

  constructor(public _globalService:GlobalService,private router: Router) { }

  ngOnInit() {
  }
  loadHome()
  {
    this._globalService.viewChange=true;
    this.router.navigate(['/']);   
  }
}
