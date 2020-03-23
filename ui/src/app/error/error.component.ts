import { Component, OnInit } from '@angular/core';
import { ErrorService } from '../Services/error.service';
import { Router, ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-error',
  templateUrl: './error.component.html',
  styleUrls: ['./error.component.css']
})
export class ErrorComponent implements OnInit {

  constructor(public _errorService:ErrorService,private router: Router,private route: ActivatedRoute) { }

  ngOnInit() {
  }
  loadHome()
  {
    this.router.navigate(['/']); 
  }

}
