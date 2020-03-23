import { Component, OnInit, ViewChild, ElementRef } from '@angular/core';
import { GlobalService } from '../global.service';

@Component({
  selector: 'app-footer',
  templateUrl: './footer.component.html',
  styleUrls: ['./footer.component.css']
})
export class FooterComponent implements OnInit {
  @ViewChild('footer') myDiv: ElementRef;

  
  constructor(private _globalService:GlobalService) { }

  ngOnInit() {
  }
  ngAfterViewInit() {
    // this.myDiv.nativeElement.style.position=document.body.clientHeight > window.innerHeight ? "inherit" : "fixed";
  }
  
  viewFile(url:any)
  {
    window.open(url, "_blank");    
  }

}
