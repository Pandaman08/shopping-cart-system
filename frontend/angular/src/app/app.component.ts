import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from './services/auth.service';
import { CartService } from './services/cart.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  readonly placeholderImage = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="72" height="72"><rect width="72" height="72" fill="%23e2e8f0"/><text x="50%25" y="54%25" dominant-baseline="middle" text-anchor="middle" font-size="10" fill="%2364758b">Sin imagen</text></svg>';
  isLoggedIn = false;
  isAdmin = false;
  cartItemCount = 0;
  currentUserName = '';
  isCartDrawerOpen = false;
  cartItems: Array<{
    id?: string;
    product_id: string;
    product_name?: string;
    product_image?: string | null;
    quantity: number;
    unit_price: number;
    subtotal: number;
  }> = [];
  cartTotal = 0;
  pendingCartActions = new Set<string>();

  get homeRoute(): string {
    return this.isAdmin ? '/admin/dashboard' : '/products';
  }

  constructor(
    private authService: AuthService,
    private cartService: CartService,
    private router: Router
  ) {}

  ngOnInit() {
    this.authService.currentUser$.subscribe(user => {
      this.isLoggedIn = !!user;
      this.isAdmin = user?.role === 'admin';
      this.currentUserName = user?.full_name || 'Usuario';

      if (this.isLoggedIn && !this.isAdmin) {
        this.cartService.getCart().subscribe();
      }

      if (!this.isLoggedIn || this.isAdmin) {
        this.isCartDrawerOpen = false;
      }
    });

    this.cartService.cart$.subscribe(cart => {
      this.cartItemCount = cart?.item_count || 0;
      this.cartItems = cart?.items || [];
      this.cartTotal = Number(cart?.total || 0);
    });
  }

  toggleCartDrawer(): void {
    if (!this.isLoggedIn || this.isAdmin) {
      return;
    }

    this.isCartDrawerOpen = !this.isCartDrawerOpen;
  }

  closeCartDrawer(): void {
    this.isCartDrawerOpen = false;
  }

  increaseItem(item: { id?: string; product_id: string; quantity: number }, event?: Event): void {
    event?.stopPropagation();

    const itemKey = this.getItemActionKey(item);
    if (this.pendingCartActions.has(itemKey)) {
      return;
    }

    this.pendingCartActions.add(itemKey);
    this.applyLocalQuantity(item.product_id, item.quantity + 1);

    this.cartService.updateItem(item.product_id, item.quantity + 1).subscribe({
      next: () => this.pendingCartActions.delete(itemKey),
      error: () => {
        this.pendingCartActions.delete(itemKey);
        this.cartService.getCart().subscribe();
        alert('No se pudo actualizar la cantidad. Intenta nuevamente.');
      }
    });
  }

  decreaseItem(item: { id?: string; product_id: string; quantity: number }, event?: Event): void {
    event?.stopPropagation();

    const itemKey = this.getItemActionKey(item);
    if (this.pendingCartActions.has(itemKey)) {
      return;
    }

    this.pendingCartActions.add(itemKey);

    if (item.quantity <= 1) {
      this.applyLocalRemove(item.product_id);
      this.cartService.removeItem(item.product_id).subscribe({
        next: () => this.pendingCartActions.delete(itemKey),
        error: () => {
          this.pendingCartActions.delete(itemKey);
          this.cartService.getCart().subscribe();
          alert('No se pudo quitar el producto del carrito.');
        }
      });
      return;
    }

    this.applyLocalQuantity(item.product_id, item.quantity - 1);
    this.cartService.updateItem(item.product_id, item.quantity - 1).subscribe({
      next: () => this.pendingCartActions.delete(itemKey),
      error: () => {
        this.pendingCartActions.delete(itemKey);
        this.cartService.getCart().subscribe();
        alert('No se pudo actualizar la cantidad. Intenta nuevamente.');
      }
    });
  }

  removeItem(item: { id?: string; product_id: string }, event?: Event): void {
    event?.stopPropagation();

    const itemKey = this.getItemActionKey(item);
    if (this.pendingCartActions.has(itemKey)) {
      return;
    }

    this.pendingCartActions.add(itemKey);
    this.applyLocalRemove(item.product_id);

    this.cartService.removeItem(item.product_id).subscribe({
      next: () => this.pendingCartActions.delete(itemKey),
      error: () => {
        this.pendingCartActions.delete(itemKey);
        this.cartService.getCart().subscribe();
        alert('No se pudo quitar el producto del carrito.');
      }
    });
  }

  private getItemActionKey(item: { id?: string; product_id: string }): string {
    return item.id || item.product_id;
  }

  private applyLocalQuantity(productId: string, nextQuantity: number): void {
    this.cartItems = this.cartItems.map(item => {
      if (item.product_id !== productId) {
        return item;
      }

      return {
        ...item,
        quantity: nextQuantity,
        subtotal: item.unit_price * nextQuantity
      };
    });

    this.cartTotal = this.cartItems.reduce((sum, item) => sum + item.subtotal, 0);
  }

  private applyLocalRemove(productId: string): void {
    this.cartItems = this.cartItems.filter(item => item.product_id !== productId);
    this.cartItemCount = this.cartItems.length;
    this.cartTotal = this.cartItems.reduce((sum, item) => sum + item.subtotal, 0);
  }

  logout() {
    this.closeCartDrawer();
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}