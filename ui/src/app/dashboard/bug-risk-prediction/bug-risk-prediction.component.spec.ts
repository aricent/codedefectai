import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { BugRiskPredictionComponent } from './bug-risk-prediction.component';

describe('BugRiskPredictionComponent', () => {
  let component: BugRiskPredictionComponent;
  let fixture: ComponentFixture<BugRiskPredictionComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ BugRiskPredictionComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(BugRiskPredictionComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
