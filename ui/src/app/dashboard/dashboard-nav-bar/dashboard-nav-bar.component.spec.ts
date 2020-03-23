import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { DashboardNavBarComponent } from './dashboard-nav-bar.component';

describe('DashboardNavBarComponent', () => {
  let component: DashboardNavBarComponent;
  let fixture: ComponentFixture<DashboardNavBarComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ DashboardNavBarComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(DashboardNavBarComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
