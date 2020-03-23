import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { CommittedFilesListComponent } from './committed-files-list.component';

describe('CommittedFilesListComponent', () => {
  let component: CommittedFilesListComponent;
  let fixture: ComponentFixture<CommittedFilesListComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ CommittedFilesListComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(CommittedFilesListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
