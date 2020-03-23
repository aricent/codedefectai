import { Injectable } from '@angular/core';
import { of, Observable } from 'rxjs';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { ApplicationInsightsService } from 'src/app/application-insights.service';

@Injectable({
  providedIn: 'root'
})
export class GlobalService {
  projects: any;
  selectedProject: any;
  commitDetails: any;
  individualcommitDetails: any;
  baseUrl = '';
  token = '';
  ProjectDetailsUrl = '/rest/api/system/projects/meta';
  PredictionDataUrl = '/rest/api/project/{projectId}/predictions';
  riskPredictionUrl = '/rest/api/project/{projectId}/commit/{commit_id}/filename/{file_name}/explaination';
  trendAnalysisUrl = '/rest/api/project/{projectId}/trend';
  fileListUrl = '/rest/api/project/{projectId}/commit/{commit_id}';
  showNotification = true;
  loading = false;
  loadBarLoading = false;
  viewChange = false;
  commitTableData: any;
  retainPageIndex: any = 0;
  retainPageSize: any = 10;
  totalLength: any;
  tableDataProjectName: any;
  disclaimerMessage = 'Bug risk predictions are inherently uncertain. Users are urged to make their own assessment using ‘Confidence Score’ and the ‘Top 5 Features’ in the prediction explanation.';
  expandedElement = null;
  gitbaseurl = 'https://github.com/{project_name}/commit/';
  constructor(private http: HttpClient, private applicationInsightsService: ApplicationInsightsService) {
    this.loadBaseUrl();
  }

  resetGitHubUrl() {
    this.gitbaseurl = 'https://github.com/{project_name}/commit/';
  }
  loadBaseUrl() {
    let url = location.origin.toLocaleLowerCase();
    if (location.origin.toLocaleLowerCase().search('localhost') > 0) {
      //this.baseUrl='https://cdptest.westus.cloudapp.azure.com';
      //this.baseUrl = 'http://10.204.238.132:8000';
      this.token = '15461197fbf6db82b421ead90d5c4d1a99559a9f';
      this.baseUrl = 'https://codedefectaiapi.azurewebsites.net';
      
      //  this.token = '15461197fbf6db82b421ead90d5c4d1a99559a9f';
      //  this.baseUrl = 'https://codedefectaiapitest.azurewebsites.net';
      
    }
    else {
      //this.baseUrl = 'http://13.64.25.145';
      // this.token = '503b42e21267da3e9274b3a4c44edeca0409375b';
      // this.baseUrl = 'https://codedefectaiapitest.azurewebsites.net';
      
      //Prod
      this.token='15461197fbf6db82b421ead90d5c4d1a99559a9f';
      this.baseUrl = 'https://codedefectaiapi.azurewebsites.net';

    }
  }
  getProjects() {
    this.applicationInsightsService.logPageView("UI App Insights - Get Projects", window.location.href);
    return this.http.get(this.baseUrl + this.ProjectDetailsUrl);
  }

  getCommitDetails(Id: any, pageIndex: any, pageSize: any, sortType: any, sortDirection: any) {
    this.applicationInsightsService.logPageView("UI App Insights - Get Commit Details", window.location.href);
    return this.http.get(this.baseUrl + this.PredictionDataUrl.replace("{projectId}", Id) + "?page=" + pageIndex + "&items_per_page=" + pageSize + "&sort_type=" + sortType + "&sort_by=" + sortDirection);
  }
  getriskPredictionDetails(projectId: any, commitId: any, fileName: any) {
    this.applicationInsightsService.logPageView("UI App Insights - Getrisk Prediction Details", window.location.href);
    return this.http.get(this.baseUrl + this.riskPredictionUrl.replace("{projectId}", projectId).replace("{commit_id}", commitId).replace("{file_name}", fileName));
  }

  public getTrendAnalysisData(projectId: any) {
    this.applicationInsightsService.logPageView("UI App Insights - Get Trend Analysis Data", window.location.href);
    return this.http.get(this.baseUrl + this.trendAnalysisUrl.replace("{projectId}", projectId));
  }
  public getFilesList(projectId: any, commitId: any) {
    this.applicationInsightsService.logPageView("UI App Insights - Get Files List", window.location.href);
    return this.http.get(this.baseUrl + this.fileListUrl.replace("{projectId}", projectId).replace("{commit_id}", commitId));
  }

}