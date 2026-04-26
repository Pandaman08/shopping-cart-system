import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class ReportService {
  private apiUrl = `${environment.apiUrl}/reports`;

  constructor(private http: HttpClient) {}

  generateOrdersReport(filters: any): Observable<Blob> {
    return this.http.post(`${this.apiUrl}/orders-pdf`, filters, {
      responseType: 'blob'
    });
  }

  generateExecutiveReport(filters: any): Observable<Blob> {
    return this.http.post(`${this.apiUrl}/executive-pdf`, filters, {
      responseType: 'blob'
    });
  }
}