import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { NavcourseComponent } from './nav-course.component';

describe('NavcourseComponent', () => {
  let component: NavcourseComponent;
  let fixture: ComponentFixture<NavcourseComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ NavcourseComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(NavcourseComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
