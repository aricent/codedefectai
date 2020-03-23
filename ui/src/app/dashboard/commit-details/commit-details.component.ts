import { Component, OnInit, ViewChild, AfterViewInit, ElementRef } from '@angular/core';
import { MatSort, MatTableDataSource, MatPaginator, PageEvent } from '@angular/material';
import { GlobalService } from '../../global.service';
import { Router, ActivatedRoute, NavigationEnd } from '@angular/router';
import { isNullOrUndefined } from 'util';
import { animate, state, style, transition, trigger } from '@angular/animations';
import { FileService } from 'src/app/Services/file.service';
import { DatePipe } from '@angular/common';
import * as moment from 'moment';
import { ErrorService } from 'src/app/Services/error.service';
import { RouterExtService } from 'src/app/Services/router-ext.service';


@Component({
  selector: 'app-commit-details',
  templateUrl: './commit-details.component.html',
  styleUrls: ['./commit-details.component.css'],
  animations: [
    trigger('detailExpand', [
      state('collapsed', style({ 'height': '0px', 'minHeight': '0', 'display': 'none' })),
      state('expanded', style({ 'height': '*' })),
      transition('expanded <=> collapsed', animate('225ms cubic-bezier(0.4, 0.0, 0.2, 1)')),
    ]),
  ],
})
export class CommitDetailsComponent implements OnInit {
  dataSource: any;

  displayedColumns: string[] = ['commitId', 'timestamp', 'file_name', 'confidenceScore', 'prediction', 'commitDetails'];
  expandabledisplayedColumns: string[] = ['timestamp', 'fileName', 'confidenceScore', 'prediction', 'commitDetails'];
  data: any;

  expandedElement: any;

  

  @ViewChild(MatPaginator) paginator: MatPaginator;
  @ViewChild(MatSort) sort: MatSort;
  positionOptions: any;
  position: any;
  fetchingData = false;
  pageEvent: PageEvent;
  pageSize: number = 10;
  pageIndex: number = 0;
  sortType: string = "timestamp";
  sortBy: string = "desc";
  totalLength: any;
  PIvar: number = 0;
  Dashboardview = false;


  constructor(public _globalService: GlobalService, public _fileService: FileService, public _errorService: ErrorService, private datePipe: DatePipe, private router: Router, private route: ActivatedRoute, private routerService: RouterExtService) {
    this.dataSource = null;
    this._globalService.loading = true;
    if (isNullOrUndefined(this._globalService.selectedProject)) {
      this.fetchingData = true;
      this.route.queryParams.subscribe(params => {
        if (params.length < 0) {
          if (isNullOrUndefined(this._globalService.selectedProject)) {
            this.router.navigate(['../ProjectDashboard'], { relativeTo: this.route });
          }
        }
        this._globalService.getProjects().subscribe(data => {
          let result = data
          let projects = result["result"].projectList;
          this._globalService.projects = data["result"].projectList;
          this._globalService.selectedProject = projects[params["projectId"] - 1];
          this.getCommitList(this._globalService.selectedProject.Id, this.pageIndex + 1, this.pageSize, this.sortType, this.sortBy);
        },
          err => {
            if (err.status != null) {
              this._errorService.ErrorNumber = err.status;
              this._errorService.ErrorStatus = err.statusText;
              this._errorService.ErrorMessage = err.message;
              this.router.navigate(['../Error']);
            }
          }
        );
      });
    }
    else {
      if (!isNullOrUndefined(this._globalService.commitDetails) && !isNullOrUndefined(this._globalService.tableDataProjectName) && (this._globalService.viewChange) && this._globalService.tableDataProjectName == this._globalService.selectedProject.ProjectName) {
        console.log(this.routerService.getCurrentUrl())
        this._globalService.viewChange = false;
      }
      else {
        this.getCommitList(this._globalService.selectedProject.Id, this.pageIndex + 1, this.pageSize, this.sortType, this.sortBy);
      }

    }

  }

  ngOnInit() {
    if (!this.fetchingData && !isNullOrUndefined(this._globalService.commitTableData) && !isNullOrUndefined(this._globalService.tableDataProjectName) && this._globalService.tableDataProjectName == this._globalService.selectedProject.ProjectName) {
      this.dataSource = this._globalService.commitTableData;
    }
  }
  ngAfterViewInit() {
    if (!this.fetchingData && !isNullOrUndefined(this._globalService.commitTableData) && !isNullOrUndefined(this._globalService.tableDataProjectName) && this._globalService.tableDataProjectName == this._globalService.selectedProject.ProjectName) {

      console.log(this._globalService.commitTableData.sort);
      console.log(this._globalService.commitTableData.paginator);
      this.pageSize = this._globalService.retainPageSize;
      this.pageIndex = this._globalService.retainPageIndex;
      this.totalLength = this._globalService.totalLength;

      //Retain Paginator

      // this.paginator.pageIndex=this._globalService.commitTableData.paginator.pageIndex;
      // this.paginator.pageSize=this._globalService.commitTableData.paginator.pageSize;
      // this.paginator.showFirstLastButtons=true;
      // this.paginator.hidePageSize=false;
      // this.paginator.disabled=false;
      // this.paginator.length=this._globalService.commitTableData.paginator.length;
      // this.dataSource.paginator = this.paginator;

      //Retain Sort
      // this.sort.direction = this._globalService.commitTableData.sort.direction;
      // this.sort.active = this._globalService.commitTableData.sort.active;
      //this.sort.sortables=this._globalService.commitTableData.sort.sortables;
      //this.sort.disabled=this._globalService.commitTableData.sort.disabled; 
      // this.sort.initialized = this._globalService.commitTableData.sort.initialized;
      // this.dataSource.sort = this.sort;
      this._globalService.loading = false;
    }
  }

  getCommitList(Id: any, pageIndex: any, pageSize: any, sortType: any, sortBy: any) {
    this._globalService.resetGitHubUrl();
    this._globalService.getCommitDetails(Id, pageIndex, pageSize, sortType, sortBy).subscribe(data => {
      console.log(data);
      let result = data["result"];
      this._globalService.tableDataProjectName = this._globalService.selectedProject.ProjectName;


      this._globalService.commitDetails = result;
      this._globalService.projects = data["result"].projectList;
      this._globalService.gitbaseurl = this._globalService.gitbaseurl.replace('{project_name}', result.project_name);
      this.data = result.predictionListing;
      this.dataSource = new MatTableDataSource(this.data);

      console.log(result);
      this._globalService.commitTableData = this.dataSource;
      this.PIvar = 0;
      this.totalLength = result.total_commit_count;
      this._globalService.totalLength = result.total_commit_count;
      this._globalService.loading = false;
    },
      err => {
        if (err.status != null) {
          this._errorService.ErrorNumber = err.status;
          this._errorService.ErrorStatus = err.statusText;
          this._errorService.ErrorMessage = err.message;
          this.router.navigate(['../Error']);
        }
      });
  }



  expandedElementfn(row: any) {
    if (this._globalService.expandedElement == row) {
      this._globalService.expandedElement = null;
    }
    else {
      this._globalService.expandedElement = row;
    }
  }

  viewAllFiles(row: any) {

    this._fileService.selectedCommit = row.preds;
    this._fileService.commitId = row.commitId;
    this._globalService.viewChange = true;
    this.router.navigate(['../committedFiles'], { queryParams: { projectId: this._globalService.selectedProject.Id, commitId: this._fileService.commitId }, relativeTo: this.route });
  }

  //Open file in GIT
  viewFile(url: any) {
    window.open(url, "_blank");
  }


  loadBugRiskPrediction(row: any) {
    // console.log(Object.keys(row).length);
    if (isNullOrUndefined(row.total_count)) {
      this._fileService.selectedCommit = this._globalService.expandedElement.preds;
      this._fileService.commitId = this._globalService.expandedElement.commitId;
      this._fileService.selectedFile = row;
    }
    else {
      this._fileService.selectedCommit = row.preds;
      this._fileService.commitId = row.commitId;
      this._fileService.selectedFile = row.preds[0];
    }

    // if (Object.keys(row).length > 4) {
    //   this._fileService.selectedCommit = this._globalService.expandedElement.preds;
    //   this._fileService.commitId = this._globalService.expandedElement.commitId;
    //   this._fileService.selectedFile = row;
    // }
    // else {
    //   this._fileService.selectedCommit = row.preds;
    //   this._fileService.commitId = row.commitId;
    //   this._fileService.selectedFile = row.preds[0];
    // }
    this._globalService.viewChange = true;
    this.router.navigate(['../bugPrediction'], { queryParams: { projectId: this._globalService.selectedProject.Id, commitId: this._fileService.commitId, fileName: this._fileService.selectedFile.file_name }, relativeTo: this.route });
  }

  viewFileByCommitId(base: any, commitId: any) {
    window.open(base + commitId, "_blank");
  }

  getBuggyCount(row: any) {
    return row.preds.filter(x => x.prediction == 1).length;
  }

  getDate(timestamp: any) {
    var momentDate = moment(timestamp);
    if (!momentDate.isValid()) return timestamp;
    return momentDate.format("YYYY-MM-DD");
  }

  getTime(timestamp: any) {
    var momentDate = moment(timestamp);
    if (!momentDate.isValid()) return timestamp;
    return momentDate.format("hh:mm:ss");

  }

  getAMPM(timestamp: any) {
    var momentDate = moment(timestamp);
    if (!momentDate.isValid()) return timestamp;
    return momentDate.format("A");
  }
  getFileName(fileName: any) {
    let a = fileName.split('/');
    let fname = String(a[a.length - 1]);
    if (fname.length < 60) {
      return fname;
    }
    return "..." + fname.slice(fname.length - 50, fname.length);
  }
  getFilepath(file: any) {

  }

  getDataSource(predictions: any) {
    if (predictions.length > 5) {
      return predictions.slice(0, 5);
    }
    return predictions;
  }

  padZero(n: any) {
    return (n < 10) ? ("0" + String(n)) : String(n);
  }

  public getServerData(event?: PageEvent) {
    this._globalService.loading = true;
    console.log(event.pageIndex);
    this.PIvar = 1;
    this._globalService.retainPageSize = event.pageSize;
    this._globalService.retainPageIndex = event.pageIndex;
    this.getCommitList(this._globalService.selectedProject.Id, event.pageIndex + 1, this._globalService.retainPageSize, this.sortType, this.sortBy);
  }

  public sortData(event) {
    this._globalService.loading = true;
    console.log(event);
    this.sortType = event.active;
    this.sortBy = event.direction;
    // if (event.direction == "") {
    //   event.direction = this.sortBy;
    // }
    console.log(this._globalService.retainPageSize);
    console.log(this._globalService.retainPageIndex);
    this.getCommitList(this._globalService.selectedProject.Id, this._globalService.retainPageIndex + 1, this._globalService.retainPageSize, this.sortType, event.direction);

  }
}
