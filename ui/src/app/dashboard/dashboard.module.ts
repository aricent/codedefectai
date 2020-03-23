import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { DashboardRoutingModule } from './dashboard-routing.module';
import { DashboardContainerComponent } from './dashboard-container/dashboard-container.component';
import { CommitDetailsComponent } from './commit-details/commit-details.component';
import { MatTableModule } from '@angular/material';
import { MatPaginatorModule,MatSortModule,MatProgressBarModule,MatSelectModule,MatInputModule,MatTooltipModule } from '@angular/material';
import { BugRiskPredictionComponent } from './bug-risk-prediction/bug-risk-prediction.component';
import { DashboardNavBarComponent } from './dashboard-nav-bar/dashboard-nav-bar.component';
import { CommittedFilesListComponent } from './committed-files-list/committed-files-list.component';
import { NavcourseComponent } from './nav-course/nav-course.component';
import { LoaderComponent } from './loader/loader.component';
import { TrendAnalysisComponent } from './trend-analysis/trend-analysis.component';
import { ProjectDetailsComponent } from './project-details/project-details.component';


@NgModule({
  declarations: [DashboardContainerComponent, CommitDetailsComponent, BugRiskPredictionComponent, DashboardNavBarComponent, CommittedFilesListComponent, NavcourseComponent, LoaderComponent, TrendAnalysisComponent, ProjectDetailsComponent],
  imports: [
    CommonModule,
    DashboardRoutingModule,
    MatTableModule,
    MatPaginatorModule,
    MatSortModule,
    MatProgressBarModule,
    MatSelectModule,
    MatInputModule,
    MatTooltipModule
  ]
})
export class DashboardModule { }
