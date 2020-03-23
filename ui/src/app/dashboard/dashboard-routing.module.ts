import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { DashboardContainerComponent } from './dashboard-container/dashboard-container.component';
import { CommitDetailsComponent } from './commit-details/commit-details.component';
import { BugRiskPredictionComponent } from './bug-risk-prediction/bug-risk-prediction.component';
import { CommittedFilesListComponent } from './committed-files-list/committed-files-list.component';
import { TrendAnalysisComponent } from './trend-analysis/trend-analysis.component';
import { ProjectDetailsComponent } from './project-details/project-details.component';

const routes: Routes = [
  { path: '', component :DashboardContainerComponent,
    children: [
      { path: 'ProjectDashboard', component: ProjectDetailsComponent},
      { path: 'CommitDetails', component:CommitDetailsComponent},
      { path:'bugPrediction', component:BugRiskPredictionComponent},
      { path:'committedFiles', component: CommittedFilesListComponent },
      { path:'trendAnalysis', component: TrendAnalysisComponent },
      { path: '',  redirectTo:'ProjectDashboard'}     
    ]
  }
];


@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class DashboardRoutingModule { }
