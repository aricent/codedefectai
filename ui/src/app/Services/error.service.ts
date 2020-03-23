import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class ErrorService {
  ErrorMessage:any;
  ErrorNumber:any;
  ErrorStatus:any;
  constructor() { }
}
