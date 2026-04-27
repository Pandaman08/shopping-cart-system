import { Component, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { ProductService } from '../services/product.service';
import { CartService } from '../services/cart.service';
import { AuthService } from '../services/auth.service';
import { Subscription, catchError, finalize, of, timeout } from 'rxjs';

interface Product {
  id: string;
  name: string;
  description: string;
  price: number;
  stock: number;
  image_url: string;
  category_name: string;
  is_active: boolean;
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit, OnDestroy {
  products: Product[] = [];
  filteredProducts: Product[] = [];
  categories: string[] = [];
  skeletonCards = Array.from({ length: 8 });
  selectedCategory: string | null = null;
  searchQuery: string = '';
  isLoading: boolean = true;
  sortBy: 'name' | 'price' | 'stock' = 'name';
  isLoggedIn = false;
  isAdmin = false;
  currentUserName = 'Usuario';
  private authSubscription?: Subscription;

  constructor(
    private productService: ProductService,
    private cartService: CartService,
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.authSubscription = this.authService.currentUser$.subscribe(user => {
      this.isLoggedIn = !!user;
      this.isAdmin = user?.role === 'admin';
      this.currentUserName = user?.full_name || 'Usuario';
    });
    this.loadProducts();
  }

  ngOnDestroy(): void {
    this.authSubscription?.unsubscribe();
  }

  loadProducts(): void {
    this.isLoading = true;
    this.productService.getProducts(1, 100)
      .pipe(
        timeout(15000),
        catchError((error) => {
          console.error('Error loading products:', error);
          return of({ data: [] });
        }),
        finalize(() => {
          this.isLoading = false;
        })
      )
      .subscribe((response: any) => {
        // Acepta distintos formatos comunes de respuesta de API.
        const products = Array.isArray(response)
          ? response
          : Array.isArray(response?.data)
            ? response.data
            : Array.isArray(response?.items)
              ? response.items
              : [];

        this.products = products;
        this.extractCategories();
        this.applyFilters();
      });
  }

  extractCategories(): void {
    const uniqueCategories = new Set<string>();
    this.products.forEach(product => {
      if (product.category_name) {
        uniqueCategories.add(product.category_name);
      }
    });
    this.categories = Array.from(uniqueCategories).sort();
  }

  filterByCategory(category: string | null): void {
    this.selectedCategory = category;
    this.applyFilters();
  }

  applyFilters(): void {
    let result = [...this.products];

    // Filtrar por categoría
    if (this.selectedCategory) {
      result = result.filter(p => p.category_name === this.selectedCategory);
    }

    // Filtrar por búsqueda
    if (this.searchQuery.trim()) {
      const query = this.searchQuery.toLowerCase();
      result = result.filter(p =>
        p.name.toLowerCase().includes(query) ||
        p.description?.toLowerCase().includes(query)
      );
    }

    // Ordenar
    result.sort((a, b) => {
      if (this.sortBy === 'price') {
        return a.price - b.price;
      } else if (this.sortBy === 'stock') {
        return b.stock - a.stock;
      } else {
        return a.name.localeCompare(b.name);
      }
    });

    this.filteredProducts = result;
  }

  onSearchChange(event: Event): void {
    const target = event.target as HTMLInputElement;
    this.searchQuery = target.value;
    this.applyFilters();
  }

  clearSearch(): void {
    this.searchQuery = '';
    this.applyFilters();
  }

  clearAllFilters(): void {
    this.selectedCategory = null;
    this.searchQuery = '';
    this.sortBy = 'name';
    this.applyFilters();
  }

  onSortChange(event: Event): void {
    const target = event.target as HTMLSelectElement;
    this.sortBy = target.value as 'name' | 'price' | 'stock';
    this.applyFilters();
  }

  addToCart(product: Product): void {
    if (!this.isLoggedIn) {
      this.cartService.queuePendingItem({
        id: product.id,
        quantity: 1,
        name: product.name,
        price: Number(product.price),
        image_url: product.image_url
      });

      const goToLogin = confirm('Debes iniciar sesión para finalizar el agregado al carrito. ¿Quieres ir a iniciar sesión ahora?');
      this.router.navigate([goToLogin ? '/login' : '/register'], {
        queryParams: { returnUrl: '/dashboard' }
      });
      return;
    }

    this.cartService.addItem(product.id, 1, {
      name: product.name,
      price: product.price,
      image_url: product.image_url
    }).subscribe({
      next: () => {
        alert(`${product.name} añadido al carrito`);
      },
      error: (error) => {
        console.error('Error adding to cart:', error);
        alert('Error al añadir al carrito');
      }
    });
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }

  getImageUrl(imageUrl: string | null): string {
    if (!imageUrl) {
      return 'https://via.placeholder.com/300x300?text=Sin+imagen';
    }
    // Si la URL es relativa, añadir la URL base del backend
    if (imageUrl.startsWith('/api/')) {
      return 'http://127.0.0.1:8000' + imageUrl;
    }
    return imageUrl;
  }

  getStockStatusClass(stock: number): string {
    if (stock === 0) {
      return 'text-red-600 bg-red-50';
    } else if (stock < 10) {
      return 'text-yellow-600 bg-yellow-50';
    }
    return 'text-green-600 bg-green-50';
  }

  getStockStatusText(stock: number): string {
    if (stock === 0) {
      return 'Agotado';
    } else if (stock < 10) {
      return `Solo ${stock} disponible`;
    }
    return 'En stock';
  }

  getCategoryCount(category: string): number {
    return this.products.filter(product => product.category_name === category).length;
  }

  getOutOfStockCount(): number {
    return this.products.filter(product => product.stock === 0).length;
  }

  get hasActiveFilters(): boolean {
    return Boolean(this.selectedCategory || this.searchQuery.trim() || this.sortBy !== 'name');
  }
}
