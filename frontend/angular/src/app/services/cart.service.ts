import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { tap } from 'rxjs/operators';
import { environment } from '../environments/environment';

@Injectable({ providedIn: 'root' })
export class CartService {
  private readonly apiUrl = `${environment.apiUrl}/cart`;
  private readonly cartSubject = new BehaviorSubject<any>(null);
  cart$ = this.cartSubject.asObservable();

  constructor(private readonly http: HttpClient) {}

  getCart(): Observable<any> {
    return this.http.get(this.apiUrl).pipe(
      tap(cart => this.cartSubject.next(cart))
    );
  }

  addItem(productId: string, quantity: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/items`, { product_id: productId, quantity }).pipe(
      tap(() => this.refreshCart())
    );
  }

  updateItem(productId: string, quantity: number): Observable<any> {
    return this.http.put(`${this.apiUrl}/items/${productId}`, { product_id: productId, quantity }).pipe(
      tap(() => this.refreshCart())
    );
  }

  removeItem(productId: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}/items/${productId}`).pipe(
      tap(() => this.refreshCart())
    );
  }

  private refreshCart() {
    this.getCart().subscribe();
  }
}