import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { AppContainerComponent } from './app-container/app-container.component';
import { ErrorComponent } from './error/error.component';

const routes: Routes = [  
  { path: 'Main',
    component:AppContainerComponent, 
    children : [
                 
                  { path : 'dashboard', loadChildren: './dashboard/dashboard.module#DashboardModule'},                  
                  { path: '', redirectTo:'dashboard', pathMatch:'full'}
                ]
  },
  { path: 'Error', component:ErrorComponent},  
  {
    path: '',
    redirectTo:'Main',
    pathMatch:'full'
  },
  { path: '**', redirectTo: 'Main'}  
  
];

@NgModule({
  imports: [RouterModule.forRoot(routes, { onSameUrlNavigation: 'reload'})],
  exports: [RouterModule]
})
export class AppRoutingModule { }
