import { Component, OnInit } from '@angular/core';
import { ProductService } from '../../services/product.service';
import { CartService } from '../../services/cart.service';
import { AuthService } from '../../services/auth.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-product-list',
  templateUrl: './product-list.component.html',
  styleUrls: ['./product-list.component.css']
})
export class ProductListComponent implements OnInit {
  products: any[] = [];
  loading = false;
  loadError = '';
  currentPage = 1;
  totalPages = 1;
  totalItems = 0;
  searchTerm = '';
  selectedCategory: number | undefined = undefined;
  categories: any[] = [];
  readonly placeholderImage = 'https://via.placeholder.com/200x200?text=Producto';

  constructor(
    private productService: ProductService,
    private cartService: CartService,
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit() {
    this.loadProducts();
    this.loadCategories();
  }

  loadProducts() {
    this.loading = true;
    this.loadError = '';
    this.productService.getProducts(this.currentPage, 12, this.searchTerm, this.selectedCategory)
      .subscribe({
        next: (response) => {
          const items = Array.isArray(response?.items)
            ? response.items
            : Array.isArray(response?.data)
              ? response.data
              : Array.isArray(response)
                ? response
                : [];

          this.products = items;
          this.totalPages = Number(response?.pages || 1);
          this.totalItems = Number(response?.total || items.length);
          this.loading = false;
        },
        error: (error) => {
          console.error('Error loading products:', error);
          this.loadError = 'No se pudieron actualizar los productos. Intenta nuevamente.';
          this.loading = false;
        }
      });
  }

  loadCategories() {
    this.productService.getCategories().subscribe({
      next: (categories) => {
        this.categories = categories;
      },
      error: (error) => console.error('Error loading categories:', error)
    });
  }

  onSearch() {
    this.currentPage = 1;
    this.loadProducts();
  }

  onCategoryChange() {
    this.currentPage = 1;
    this.loadProducts();
  }

  onPageChange(page: number) {
    this.currentPage = page;
    this.loadProducts();
  }

  addToCart(product: any) {
    if (!this.authService.isLoggedIn()) {
      this.cartService.queuePendingItem({
        id: product.id,
        quantity: 1,
        name: product.name,
        price: Number(product.price),
        image_url: product.image_url
      });

      const goToLogin = confirm('Debes iniciar sesión para finalizar el agregado al carrito. ¿Quieres ir a iniciar sesión ahora?');
      this.router.navigate([goToLogin ? '/login' : '/register'], {
        queryParams: { returnUrl: '/products' }
      });
      return;
    }
    
    this.cartService.addItem(product.id, 1, {
      name: product.name,
      price: Number(product.price),
      image_url: product.image_url
    }).subscribe({
      next: () => {
        alert(`${product.name} agregado al carrito`);
      },
      error: (error) => {
        alert('Error al agregar al carrito: ' + error.message);
      }
    });
  }

  onImageError(event: Event) {
    const target = event.target as HTMLImageElement;
    if (target && target.src !== this.placeholderImage) {
      target.src = this.placeholderImage;
    }
  }
}