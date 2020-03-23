import { TestBed } from '@angular/core/testing';

import { RouterExtService } from './router-ext.service';

describe('RouterExtService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: RouterExtService = TestBed.get(RouterExtService);
    expect(service).toBeTruthy();
  });
});
