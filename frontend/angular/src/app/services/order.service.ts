import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../environments/environment';

@Injectable({ providedIn: 'root' })
export class OrderService {
  private readonly apiUrl = `${environment.apiUrl}/orders`;

  constructor(private readonly http: HttpClient) {}

  checkout(orderData: any): Observable<any> {
    return this.http.post(this.apiUrl, orderData);
  }

  getMyOrders(): Observable<any> {
    return this.http.get(this.apiUrl);
  }

  getAllOrders(): Observable<any> {
    return this.http.get(`${this.apiUrl}/admin/all`);
  }
}