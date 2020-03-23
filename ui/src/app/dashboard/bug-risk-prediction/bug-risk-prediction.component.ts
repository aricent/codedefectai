import { Component, OnInit, ViewChild } from '@angular/core';
import { GlobalService } from 'src/app/global.service';
import { Router, ActivatedRoute, NavigationEnd } from '@angular/router';
import { FileService } from 'src/app/Services/file.service';

import { DatePipe } from '@angular/common';
import { isNullOrUndefined } from 'util';
import * as moment from 'moment';
import { ErrorService } from 'src/app/Services/error.service';
import { Location } from '@angular/common';
import { RouterExtService } from 'src/app/Services/router-ext.service';

@Component({
  selector: 'app-bug-risk-prediction',
  templateUrl: './bug-risk-prediction.component.html',
  styleUrls: ['./bug-risk-prediction.component.css']
})
export class BugRiskPredictionComponent implements OnInit {
  dataSource: any;
  categoryHigh: any;
  categoryLow: any;
  displayedColumns: string[] = ['feature', 'value', 'graphx'];
  mySubscription: any;
  file_name: any;
  prediction: any;
  timeStamp: any;
  file_link: any;
  total: number;
  confidenceScore: any;
  featureDescription = new Map<string, string>();
  previousUrl: any;
  constructor(public _globalService: GlobalService, public _fileService: FileService, public _errorService: ErrorService, private router: Router, private route: ActivatedRoute, private _location: Location, private routerService: RouterExtService) {
    _globalService.loading = true;
    this.getFeatureDescription();
    if (isNullOrUndefined(this._globalService.selectedProject)) {
      this.route.queryParams.subscribe(params => {
        if (params.length < 0) {
          this.router.navigate(['../ProjectDashboard'], { relativeTo: this.route });
        }
        console.log(params)
        this._globalService.getProjects().subscribe(data => {
          let result = data
          let projects = result["result"].projectList;
          this._globalService.projects = data["result"].projectList;
          this._globalService.selectedProject = projects[params["projectId"] - 1];
          this.file_name = params["fileName"];
          this._fileService.commitId = params["commitId"];
          this.getPredictionDetails();
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
      }
      );
    }
    else {
      this.file_link = this._fileService.selectedFile.file_link;
      this.timeStamp = this._fileService.selectedCommit[0].timestamp;
      this.file_name = this._fileService.selectedFile.file_name;
      this.confidenceScore = this._fileService.selectedFile.confidenceScore;
      this.getPredictionDetails();
    }
  }
  ngOnInit() {

  }

  getPredictionDetails() {
    this._globalService.getriskPredictionDetails(this._globalService.selectedProject.Id, this._fileService.commitId, this.file_name).subscribe(data => {

      let result = data["result"];
      console.log(data["response"]);
      if (result.response == "Service is temporarily down. Please try again after sometime...!!!") {
        this._errorService.ErrorNumber = 503;
        this._errorService.ErrorStatus = "Service Unavailable";
        this._errorService.ErrorMessage = result.response;
        this.router.navigate(['../Error']);
      }
      console.log(data);
      this.total = result.features.reduce(function (prev, cur) {
        return prev + cur.coefficient;
      }, 0);
      console.log(this.total);
      this.prediction = result.prediction;
      this.timeStamp = result.timeStamp;
      this.categoryHigh = [];
      this.categoryLow = [];
      for (var i = 0; i < result.features.length; i++) {
        var item = result.features[i];
        var label = item.label;
        console.log(i);
        label === 0 ? this.categoryLow.push(result.features[i]) : this.categoryHigh.push(result.features[i]);

      }
      if (this.prediction === 1) {
        this.dataSource = this.categoryHigh;
      }
      else {
        this.dataSource = this.categoryLow;
      }
      this.dataSource.splice(5);
      console.log(this.dataSource);
      this.file_link = result.file_link;
      this.confidenceScore = result.confidencescore;
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
  getBugWeightStyles(weight: any) {
    let myStyles =
      {
        'display': 'inline-block',
        'height': '25px',
        'background-color': '#e76e3c',
        'width': ((weight * 95) / this.total).toString() + '%',
        'border-top-right-radius': '6px',
        'border-bottom-right-radius': '6px',
        'padding-left': '10px',
        'margin-right': '10px',
        'position': 'relative'
      };
    return myStyles;
  }

  getFloatTextStyle(weight: any) {
    let style = {
      'position': 'absolute',
      'top': '3px',
      'right': (((weight * 95) / this.total) + 2).toString() + '%'
    }
    return style;
  }
  getCleanWeightStyle(weight: any) {
    let myStyles = {

      'display': 'inline-block',
      'height': '25px',
      'background-color': '#16a085',
      'width': ((weight * 95) / this.total).toString() + '%',
      'border-top-right-radius': '6px',
      'border-bottom-right-radius': '6px',
      'padding-left': '10px',
      'margin-right': '10px',
      'position': 'relative'
    };
    return myStyles;
  }
  getFileName(fileName: any) {


    let a = fileName.split('/');
    let filename = String(a[a.length - 1]);
    if (filename.length > 60) {
      return "..." + filename.slice(filename.length - 60, filename.length);
    }
    return filename;

  }
  getFullFileName(fileName: any) {
    let a = fileName.split('/');
    return String(a[a.length - 1]);
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
  loadPreviousPage() {
    if (this.routerService.getPreviousUrl() != this.routerService.getCurrentUrl()) {
      this._location.back();
    }
    else {
      this.router.navigate(['../CommitDetails'], { queryParams: { projectId: this._globalService.selectedProject.Id }, relativeTo: this.route });
    }
  }
  loadCommitDetails() {
    this.router.navigate(['../CommitDetails'], { queryParams: { projectId: this._globalService.selectedProject.Id }, relativeTo: this.route });
  }
  loadHome() {
    this.router.navigate(['/']);
  }
  showFileHistsory(url: any) {
    window.open(url, "_blank");
  }
  getFeatureDescription() {
    this.featureDescription.set('COMMIT_ID', 'NA');
    this.featureDescription.set('AUTHOR_NAME', 'NA');
    this.featureDescription.set('FILE_STATUS', 'NA');
    this.featureDescription.set('LINES_ADDED', 'Total number of lines added in the file');
    this.featureDescription.set('LINES_MODIFIED', 'Total number of lines modified in the file');
    this.featureDescription.set('LINES_DELETED', 'Total number of lines deleted in the file');
    this.featureDescription.set('ND', 'Total number of directories modified in the commit');
    this.featureDescription.set('NF', 'Total number of files modified in the commit');
    this.featureDescription.set('FILES_ENTROPY', 'Number of changes spread across the file in that commit');
    this.featureDescription.set('FILE_AGE', 'Time interval between the changes');
    this.featureDescription.set('NO_OF_DEV', 'Total number of developers that have changed the file');
    this.featureDescription.set('TIMES_FILE_MODIFIED', 'Total number of times the file was modified throughout its life');
    this.featureDescription.set('FILE_SIZE', 'Current size of the file in kilobyte (KB)');
    this.featureDescription.set('DEV_EXP', 'Total number of commits made by the developer');
    this.featureDescription.set('NS', 'Total number of sub modules modified in the commit');
    this.featureDescription.set('SUB_MODULE_STATS', 'Total number of commits made by the developer for the module');
    this.featureDescription.set('Is_fix', 'If the current commit is a bug fix commit');
    this.featureDescription.set('DEV_REXP', 'Developer Experience with higher weightage given to recent changes');
    this.featureDescription.set('FileChanges', 'Average lines changed per change block in the file');
    this.featureDescription.set('COMMIT_TYPE', 'Merge or non-merge commit');
  }
}
