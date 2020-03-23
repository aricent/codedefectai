import { Component, OnInit } from '@angular/core';
import { GlobalService } from 'src/app/global.service';
import { Router, ActivatedRoute } from '@angular/router';
import { ErrorService } from 'src/app/Services/error.service';
import { isNullOrUndefined } from 'util';


@Component({
  selector: 'app-project-details',
  templateUrl: './project-details.component.html',
  styleUrls: ['./project-details.component.css']
})
export class ProjectDetailsComponent implements OnInit {

  projects:[];
  disclaimer=true;
  constructor(public _globalService:GlobalService, public _errorService:ErrorService, private router: Router,private route: ActivatedRoute) {
    //this._globalService.loading=true;
   }

  ngOnInit() {
    if(isNullOrUndefined(this._globalService.projects))
    {
      this._globalService.loading=true;
      this._globalService.getProjects().subscribe(data => {
        let result=data
        this.projects=result["result"].projectList;
        this._globalService.projects=data["result"].projectList; 
        this._globalService.loading=false;
      },
      err => {
        if(err.status!=null)
            {
              this._errorService.ErrorNumber=err.status;
              this._errorService.ErrorStatus=err.statusText;
              this._errorService.ErrorMessage=err.message;
              this.router.navigate(['../Error']);
            }
      }
      );
   }
   else{
    this.projects=this._globalService.projects;
   }
  }
  loadCommitDetails(project: [])
  {
    this._globalService.selectedProject=project;
    this.router.navigate(['../CommitDetails'],{ queryParams : { projectId:this._globalService.selectedProject.Id} , relativeTo: this.route });
  }
  getpercentage(BuggyPredictions:any,TotalFilesForPrediction) {
    if(TotalFilesForPrediction==0)
    {
      return String(0);
    }
    else
    {
      return String((BuggyPredictions/TotalFilesForPrediction)*100);
    }
  }
  hideDisclaimer()
  {
    this.disclaimer=false;
  }

}
