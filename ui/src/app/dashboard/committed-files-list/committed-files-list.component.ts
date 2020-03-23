import { Component, OnInit, ViewChild } from '@angular/core';


import {MatSort, MatTableDataSource, MatPaginator} from '@angular/material';
import { GlobalService } from 'src/app/global.service';
import { Router, ActivatedRoute, NavigationEnd } from '@angular/router';
import { FileService } from 'src/app/Services/file.service';
import { isNullOrUndefined } from 'util';
import { DatePipe,Location } from '@angular/common';
import * as moment from 'moment';
import { ErrorService } from 'src/app/Services/error.service';


@Component({
  selector: 'app-committed-files-list',
  templateUrl: './committed-files-list.component.html',
  styleUrls: ['./committed-files-list.component.css']
})
export class CommittedFilesListComponent implements OnInit {

  
  // dataSource:any;  
  displayedColumns: string[] = [ 'file_name','confidencescore','prediction', 'fileHistory'];
  dataSource : any;
  mySubscription: any;
  projectId:any;
  @ViewChild(MatPaginator) paginator: MatPaginator;
  @ViewChild(MatSort) sort: MatSort;
  fileList: any;
  fetchingData=false;
  constructor(public _globalService:GlobalService, public _fileService:FileService, public _errorService:ErrorService, private datePipe: DatePipe, private router: Router,private route: ActivatedRoute,private _location: Location) {
    
    if(isNullOrUndefined(this._globalService.selectedProject) || isNullOrUndefined(this._fileService.selectedCommit))
    { 
      _globalService.loading=true;
      this.route.queryParams.subscribe( params => 
        {
          if(params.length<0)
          {
            this.router.navigate(['../ProjectDashboard'], { relativeTo: this.route });
          }
          _fileService.commitId=params["commitId"];
          this.projectId=params["projectId"]
          this.getFilesList(this.projectId,_fileService.commitId);
        });
    }
    else{
      this.projectId=this._globalService.selectedProject.Id;
      this.getFilesList(this.projectId,_fileService.commitId);
    }
  }
  ngOnInit() {
    
  }
  ngAfterViewInit() {
    if(!this._globalService.loading)
    {
      this.getCommitList();
    }
    
  }
  getFilesList(id:any,commitId:any)
  {
    this._globalService.getFilesList(id,commitId).subscribe(data => {
      console.log(data);
      let result=data["result"];
      this._fileService.selectedCommit=result.predictionListing[0].preds;
      this.getCommitList();
    },
    err => {
     if(err.status!=null)
     {
       this._errorService.ErrorNumber=err.status;
       this._errorService.ErrorStatus=err.statusText;
       this._errorService.ErrorMessage=err.message;
       this.router.navigate(['../Error']); 
     } 
    });
  }
  getCommitList()
  {
    this.fileList=this._fileService.selectedCommit;   
    this.dataSource =new MatTableDataSource(this.fileList);
    this.dataSource.paginator = this.paginator;
    this.dataSource.sort = this.sort;
    this._globalService.loading=false;  
    
  }

  
  viewFile(url:any)
  {
    window.open(url, "_blank");    
  }
  getFileName(fileName:any){
    let a= fileName.split('/');
    let fname=String(a[a.length-1]);
    if(fname.length<60)
    {
      return fileName;
    }
    return "..."+fname.slice(fname.length-50,fname.length);
  }
  
  padZero(n:any) {
    return (n < 10) ? ("0" + String(n)) : String(n);
  }  
  getDate(timestamp:any)
  {
    var momentDate = moment(timestamp);
    if (!momentDate.isValid()) return timestamp;
    return momentDate.format("YYYY-MM-DD");
}
  
  getTime(timestamp:any){
    var momentDate = moment(timestamp);
    if (!momentDate.isValid()) return timestamp;
    return momentDate.format("hh:mm:ss");

  }
  getAMPM(timestamp:any)
  {
    var momentDate = moment(timestamp);
    if (!momentDate.isValid()) return timestamp;
    return momentDate.format("A");
  }

  loadBugRiskPrediction(row:any){
    this._fileService.selectedFile=row;  
    this.router.navigate(['../bugPrediction'],{ queryParams : {projectId : this.projectId,commitId:this._fileService.commitId,fileName:this._fileService.selectedFile.file_name}, relativeTo: this.route });
  }
  loadCommitDetails()
  {
    this.router.navigate(['../CommitDetails'],{ queryParams : {projectId:this.projectId}, relativeTo: this.route });    
  }
  navigateBack() {
    this._location.back();
  }
}
