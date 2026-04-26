import { Component, OnInit } from '@angular/core';
import { ProductService } from '../../services/product.service';
import { CartService } from '../../services/cart.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-product-list',
  templateUrl: './product-list.component.html',
  styleUrls: ['./product-list.component.css']
})
export class ProductListComponent implements OnInit {
  products: any[] = [];
  loading = false;
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
    private authService: AuthService
  ) {}

  ngOnInit() {
    this.loadProducts();
    this.loadCategories();
  }

  loadProducts() {
    this.loading = true;
    this.productService.getProducts(this.currentPage, 12, this.searchTerm, this.selectedCategory)
      .subscribe({
        next: (response) => {
          this.products = response.items;
          this.totalPages = response.pages;
          this.totalItems = response.total;
          this.loading = false;
        },
        error: (error) => {
          console.error('Error loading products:', error);
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
      alert('Por favor inicia sesión para agregar productos al carrito');
      return;
    }
    
    this.cartService.addItem(product.id, 1).subscribe({
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