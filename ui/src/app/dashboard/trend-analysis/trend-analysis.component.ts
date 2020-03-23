import { Component, OnInit } from '@angular/core';
import { GlobalService } from 'src/app/global.service';
import { isNullOrUndefined } from 'util';
import { Router, ActivatedRoute } from '@angular/router';
import { ErrorService } from 'src/app/Services/error.service';

declare var Plotly:any;

@Component({
  selector: 'app-trend-analysis',
  templateUrl: './trend-analysis.component.html',
  styleUrls: ['./trend-analysis.component.css']
})
export class TrendAnalysisComponent implements OnInit {
  public boxPlot = [];
  public univariateData;
  public optionSelected;
  options:any
  graphloading=false;
  constructor(public _globalService:GlobalService,private _errorService:ErrorService, private router: Router,private route: ActivatedRoute) {
    
    if(isNullOrUndefined(this._globalService.selectedProject))
    {
      this.graphloading=true;
      _globalService.loading=true;
      this.route.queryParams.subscribe( params => 
        {
          if(params.length<0)
          {
            if(isNullOrUndefined(this._globalService.selectedProject))
            {
              this.router.navigate(['../ProjectDashboard'], { relativeTo: this.route });
            }
          }
          console.log(params)
          this._globalService.getProjects().subscribe(data => {
            let result=data
            let projects=result["result"].projectList;
            this._globalService.projects=data["result"].projectList; 
            this._globalService.selectedProject=projects[params["projectId"]-1];
            this.plotBoxPlot();
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
           );
    }
  }

  ngOnInit() {
    
  }
  ngAfterViewInit() {
    if(!this.graphloading)
    {
      this.plotBoxPlot();
    }
  }


  public plotBoxPlot() {
    this._globalService.getTrendAnalysisData(this._globalService.selectedProject.Id).subscribe(
      data => {
        console.log(data);
        let result=data["result"]
        let HighRiskData=result.HighBugRisk;
        let LowRiskData=result.LowBugRisk;
        let trance=[];
        for (let i = 0; i <HighRiskData.length; i ++) {
          trance[i]={
            y: [HighRiskData[i].minimum, HighRiskData[i].firstQuartile,HighRiskData[i].firstQuartile,HighRiskData[i].median,HighRiskData[i].thirdQuartile,HighRiskData[i].thirdQuartile,HighRiskData[i].maximum],
            type: 'box',
            marker: { color: '#EAEAEA'},
            name: '<span style="color:#e76e3c">'+String(HighRiskData[i].name+'(H)').split(' ').join('<br />')+'</span>',
            fillcolor:'#e76e3c',
            boxpoints:false,
            line:{width:1},
          }
        }
        for (let i = 0; i <LowRiskData.length; i ++) {
          trance[i+HighRiskData.length]={
            y: [LowRiskData[i].minimum, LowRiskData[i].firstQuartile,LowRiskData[i].firstQuartile,LowRiskData[i].median,LowRiskData[i].thirdQuartile,LowRiskData[i].thirdQuartile,LowRiskData[i].maximum],
            type: 'box',
            marker: { color: '#EAEAEA'},
            name: '<span style="color:#16a085">'+String(LowRiskData[i].name+'(L)').split(' ').join('<br />')+' </span>',
            fillcolor:'#16a085',
            boxpoints:false,
            line:{
              width:1
            },
          }
        }
        
        let layout = {
          boxgap:0.2,
          height:'500px',
          xaxis: {
            zeroline:false,            
            showline:true,
            color:'#e9e9f0',
            marker: { color: "black" },
            tickcolor:'black',
            tickfont:{
              color:'#43425d',
              family: 'SourceSansPro',
              size:'11px'
            },
            showlegend:false
          },
          yaxis: {
            zeroline:false,
            title: '<span style="font-weight:600;font-size:11px;">WEIGHT</span>',
            titlefont:{
              color:'#43425d',
              family: 'SourceSansPro',
              size:'10px'
            },
            showgrid:true,
            gridcolor:'#F7F7F7',
            showline: true,
            showticklabels: true,
            color:'#e9e9f0',
            tickfont:{
              color:'#43425d',
              family: 'SourceSansPro',
              size:'13px'
            },
            tickcolor:'black',
          },
          showlegend:false
        };
        Plotly.newPlot('boxPlot', trance, layout,{modeBarButtonsToRemove: ['resetScale2d'], responsive: true});
        this._globalService.loading=false;
        this.graphloading=false;
      },
      err => {
        console.log(err);
        if(err.status!=null)
        {
          this._errorService.ErrorNumber=err.status;
          this._errorService.ErrorStatus=err.statusText;
          this._errorService.ErrorMessage=err.message;
          this.router.navigate(['../Error']);
        } 
      });
  }
  loadCommitDetails()
  {
    this.router.navigate(['../CommitDetails'],{ queryParams : {projectId:this._globalService.selectedProject.Id}, relativeTo: this.route });    
  }
  
}
