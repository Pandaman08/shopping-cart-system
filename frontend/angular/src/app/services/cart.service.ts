import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, from, of, throwError } from 'rxjs';
import { catchError, concatMap, map, switchMap, tap, toArray } from 'rxjs/operators';
import { environment } from '../environments/environment';

interface CartItem {
  product_id: string;
  product_name?: string;
  product_image?: string | null;
  quantity: number;
  unit_price: number;
  subtotal: number;
}

interface CartState {
  id: string;
  user_id: string;
  items: CartItem[];
  total: number;
  item_count: number;
  created_at: string;
  updated_at: string;
}

interface PendingCartItem {
  product_id: string;
  quantity: number;
  name?: string;
  price?: number;
  image_url?: string | null;
}

@Injectable({ providedIn: 'root' })
export class CartService {
  private readonly apiUrl = `${environment.apiUrl}/cart`;
  private readonly pendingItemsKey = 'pendingCartItems';
  private readonly cartSubject = new BehaviorSubject<CartState | null>(null);
  cart$ = this.cartSubject.asObservable();

  constructor(private readonly http: HttpClient) {}

  getCart(): Observable<any> {
    return this.http.get(this.apiUrl).pipe(
      tap(cart => this.cartSubject.next(cart))
    );
  }

  addItem(
    productId: string,
    quantity: number,
    optimisticProduct?: { name?: string; price?: number; image_url?: string | null }
  ): Observable<any> {
    const previousCart = this.cartSubject.value;
    const optimisticCart = this.buildOptimisticAdd(previousCart, productId, quantity, optimisticProduct);
    this.cartSubject.next(optimisticCart);

    return this.http.post(`${this.apiUrl}/items`, { product_id: productId, quantity }).pipe(
      switchMap(() => this.getCart()),
      catchError((error) => {
        this.cartSubject.next(previousCart);
        return throwError(() => error);
      })
    );
  }

  queuePendingItem(product: { id: string; quantity: number; name?: string; price?: number; image_url?: string | null }): void {
    const pending = this.getPendingItems();
    const index = pending.findIndex(item => item.product_id === product.id);

    if (index >= 0) {
      pending[index].quantity += product.quantity;
    } else {
      pending.push({
        product_id: product.id,
        quantity: product.quantity,
        name: product.name,
        price: product.price,
        image_url: product.image_url || null
      });
    }

    localStorage.setItem(this.pendingItemsKey, JSON.stringify(pending));
  }

  syncPendingItems(): Observable<void> {
    const pending = this.getPendingItems();

    if (!pending.length) {
      return of(void 0);
    }

    return from(pending).pipe(
      concatMap(item =>
        this.http.post(`${this.apiUrl}/items`, {
          product_id: item.product_id,
          quantity: item.quantity
        })
      ),
      toArray(),
      tap(() => this.clearPendingItems()),
      switchMap(() => this.getCart()),
      map(() => void 0),
      catchError((error) => {
        console.error('Error syncing pending cart items:', error);
        return throwError(() => error);
      })
    );
  }

  getPendingItemsCount(): number {
    return this.getPendingItems().reduce((acc, item) => acc + item.quantity, 0);
  }

  updateItem(productId: string, quantity: number): Observable<any> {
    return this.http.put(`${this.apiUrl}/items/${productId}`, { product_id: productId, quantity }).pipe(
      switchMap(() => this.getCart())
    );
  }

  removeItem(productId: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}/items/${productId}`).pipe(
      switchMap(() => this.getCart())
    );
  }

  getCurrentCartSnapshot(): CartState | null {
    return this.cartSubject.value;
  }

  private getPendingItems(): PendingCartItem[] {
    const raw = localStorage.getItem(this.pendingItemsKey);
    if (!raw) {
      return [];
    }

    try {
      const parsed = JSON.parse(raw);
      return Array.isArray(parsed) ? parsed : [];
    } catch {
      return [];
    }
  }

  private clearPendingItems(): void {
    localStorage.removeItem(this.pendingItemsKey);
  }

  private buildOptimisticAdd(
    cart: CartState | null,
    productId: string,
    quantity: number,
    optimisticProduct?: { name?: string; price?: number; image_url?: string | null }
  ): CartState {
    const now = new Date().toISOString();

    if (!cart) {
      const unitPrice = Number(optimisticProduct?.price ?? 0);
      return {
        id: 'optimistic-cart',
        user_id: 'current-user',
        created_at: now,
        updated_at: now,
        items: [
          {
            product_id: productId,
            product_name: optimisticProduct?.name || 'Producto',
            product_image: optimisticProduct?.image_url || null,
            quantity,
            unit_price: unitPrice,
            subtotal: unitPrice * quantity
          }
        ],
        total: unitPrice * quantity,
        item_count: 1
      };
    }

    const items = [...cart.items];
    const existingIndex = items.findIndex(item => item.product_id === productId);

    if (existingIndex >= 0) {
      const current = items[existingIndex];
      const nextQuantity = current.quantity + quantity;
      items[existingIndex] = {
        ...current,
        quantity: nextQuantity,
        subtotal: current.unit_price * nextQuantity
      };
    } else {
      const unitPrice = Number(optimisticProduct?.price ?? 0);
      items.push({
        product_id: productId,
        product_name: optimisticProduct?.name || 'Producto',
        product_image: optimisticProduct?.image_url || null,
        quantity,
        unit_price: unitPrice,
        subtotal: unitPrice * quantity
      });
    }

    const total = items.reduce((acc, item) => acc + item.subtotal, 0);

    return {
      ...cart,
      items,
      total,
      item_count: items.length,
      updated_at: now
    };
  }
}