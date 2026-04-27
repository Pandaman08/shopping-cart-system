import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { ProductService } from '../../services/product.service';
import { CartService } from '../../services/cart.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-product-detail',
  templateUrl: './product-detail.component.html',
  styleUrls: ['./product-detail.component.css']
})
export class ProductDetailComponent implements OnInit {
  product: any = null;
  quantity = 1;
  loading = true;

  constructor(
    private route: ActivatedRoute,
    private productService: ProductService,
    private cartService: CartService,
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit() {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.loadProduct(id);
    }
  }

  loadProduct(id: string) {
    this.productService.getProduct(id).subscribe({
      next: (product) => {
        this.product = product;
        this.loading = false;
      },
      error: (error) => {
        console.error('Error loading product:', error);
        this.loading = false;
        this.router.navigate(['/products']);
      }
    });
  }

  addToCart() {
    if (!this.authService.isLoggedIn()) {
      this.cartService.queuePendingItem({
        id: this.product.id,
        quantity: this.quantity,
        name: this.product.name,
        price: Number(this.product.price),
        image_url: this.product.image_url
      });

      const goToLogin = confirm('Debes iniciar sesión para finalizar el agregado al carrito. ¿Quieres ir a iniciar sesión ahora?');
      this.router.navigate([goToLogin ? '/login' : '/register'], {
        queryParams: { returnUrl: this.router.url }
      });
      return;
    }

    if (this.quantity > this.product.stock) {
      alert('No hay suficiente stock disponible');
      return;
    }

    this.cartService.addItem(this.product.id, this.quantity, {
      name: this.product.name,
      price: Number(this.product.price),
      image_url: this.product.image_url
    }).subscribe({
      next: () => {
        alert(`${this.quantity}x ${this.product.name} agregado al carrito`);
      },
      error: (error) => {
        alert('Error al agregar al carrito: ' + error.message);
      }
    });
  }

  updateQuantity(change: number) {
    const newQuantity = this.quantity + change;
    if (newQuantity >= 1 && newQuantity <= this.product?.stock) {
      this.quantity = newQuantity;
    }
  }
}