import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { TrendAnalysisComponent } from './trend-analysis.component';

describe('TrendAnalysisComponent', () => {
  let component: TrendAnalysisComponent;
  let fixture: ComponentFixture<TrendAnalysisComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ TrendAnalysisComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(TrendAnalysisComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
