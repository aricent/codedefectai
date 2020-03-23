import { Component, OnInit } from '@angular/core';
import { GlobalService } from 'src/app/global.service';
import { Router, ActivatedRoute } from '@angular/router';
import { isNullOrUndefined } from 'util';
import { FileService } from 'src/app/Services/file.service';

@Component({
  selector: 'app-dashboard-nav-bar',
  templateUrl: './dashboard-nav-bar.component.html',
  styleUrls: ['./dashboard-nav-bar.component.css']
})
export class DashboardNavBarComponent implements OnInit {

  constructor(public _globalService:GlobalService,private _fileService:FileService, private router: Router,private route: ActivatedRoute) {
   
   }

  ngOnInit() {
  }
  loadTrends()
  {
    this._globalService.loading=true;
    this._globalService.viewChange=true;
    this.router.navigate(['../trendAnalysis'],{queryParams:{ projectId : this._globalService.selectedProject.Id}, relativeTo: this.route });
  }

}
