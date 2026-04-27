import { Component, OnDestroy, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { CartService } from '../services/cart.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-cart',
  templateUrl: './cart.component.html',
  styleUrls: ['./cart.component.css']
})
export class CartComponent implements OnInit, OnDestroy {
  cart: any = null;
  loading = true;
  private cartSubscription?: Subscription;

  constructor(
    private cartService: CartService,
    private router: Router
  ) {}

  ngOnInit() {
    this.cartSubscription = this.cartService.cart$.subscribe(cart => {
      if (cart) {
        this.cart = cart;
        this.loading = false;
      }
    });
    this.loadCart();
  }

  ngOnDestroy() {
    this.cartSubscription?.unsubscribe();
  }

  loadCart() {
    this.cartService.getCart().subscribe({
      next: (cart) => {
        this.cart = cart;
        this.loading = false;
      },
      error: (error) => {
        console.error('Error loading cart:', error);
        this.loading = false;
      }
    });
  }

  updateQuantity(item: any, change: number) {
    const newQuantity = item.quantity + change;
    if (newQuantity >= 1) {
      this.cartService.updateItem(item.product_id, newQuantity).subscribe({
        next: (cart) => {
          this.cart = cart;
          this.loading = false;
        },
        error: (error) => alert('Error al actualizar cantidad: ' + error.message)
      });
    }
  }

  removeItem(productId: string) {
    if (confirm('¿Eliminar este producto del carrito?')) {
      this.cartService.removeItem(productId).subscribe({
        next: (cart) => {
          this.cart = cart;
          this.loading = false;
        },
        error: (error) => alert('Error al eliminar: ' + error.message)
      });
    }
  }

  clearCart() {
    if (confirm('¿Vaciar completamente el carrito?')) {
      // Implementar método clearCart en el servicio si es necesario
      this.cart.items.forEach((item: any) => {
        this.cartService.removeItem(item.product_id).subscribe();
      });
      setTimeout(() => this.loadCart(), 500);
    }
  }

  proceedToCheckout() {
    if (this.cart && this.cart.items.length > 0) {
      this.router.navigate(['/checkout']);
    }
  }
}