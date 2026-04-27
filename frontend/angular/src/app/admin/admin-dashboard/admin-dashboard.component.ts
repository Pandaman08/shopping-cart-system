import { Component, OnInit } from '@angular/core';
import { ProductService } from '../../services/product.service';
import { OrderService } from '../../services/order.service';

@Component({
  selector: 'app-admin-dashboard',
  templateUrl: './admin-dashboard.component.html',
  styleUrls: ['./admin-dashboard.component.css']
})
export class AdminDashboardComponent implements OnInit {
  products: any[] = [];
  orders: any[] = [];
  loadingProducts = true;
  loadingOrders = true;
  categoryBreakdown: Array<{ label: string; value: number; percent: number }> = [];
  orderStatusBreakdown: Array<{ label: string; value: number; percent: number }> = [];

  constructor(
    private productService: ProductService,
    private orderService: OrderService
  ) {}

  ngOnInit() {
    this.loadProducts();
    this.loadOrders();
  }

  loadProducts() {
    this.productService.getProducts(1, 50).subscribe({
      next: (response) => {
        this.products = response.items;
        this.categoryBreakdown = this.buildCategoryBreakdown(this.products);
        this.loadingProducts = false;
      },
      error: (error) => {
        console.error('Error loading products:', error);
        this.loadingProducts = false;
      }
    });
  }

  loadOrders() {
    this.orderService.getAllOrders().subscribe({
      next: (orders) => {
        this.orders = orders;
        this.orderStatusBreakdown = this.buildStatusBreakdown(this.orders);
        this.loadingOrders = false;
      },
      error: (error) => {
        console.error('Error loading orders:', error);
        this.loadingOrders = false;
      }
    });
  }

  deleteProduct(id: string) {
    if (confirm('¿Eliminar este producto permanentemente?')) {
      this.productService.deleteProduct(id).subscribe({
        next: () => {
          alert('Producto eliminado');
          this.loadProducts();
        },
        error: (error) => alert('Error al eliminar: ' + error.message)
      });
    }
  }

  get totalRevenue(): number {
    return this.orders.reduce((sum, order) => sum + Number(order.total_amount || 0), 0);
  }

  get totalProducts(): number {
    return this.products.length;
  }

  get lowStockProducts(): number {
    return this.products.filter(product => Number(product.stock) > 0 && Number(product.stock) < 10).length;
  }

  get outOfStockProducts(): number {
    return this.products.filter(product => Number(product.stock) === 0).length;
  }

  get totalOrders(): number {
    return this.orders.length;
  }

  get paidOrders(): number {
    return this.orders.filter(order => ['paid', 'shipped', 'delivered'].includes(order.status)).length;
  }

  get averageTicket(): number {
    return this.totalOrders ? this.totalRevenue / this.totalOrders : 0;
  }

  private buildCategoryBreakdown(products: any[]): Array<{ label: string; value: number; percent: number }> {
    const counts = new Map<string, number>();

    products.forEach(product => {
      const category = product.category_name || 'Sin categoría';
      counts.set(category, (counts.get(category) || 0) + 1);
    });

    const total = products.length || 1;
    return Array.from(counts.entries())
      .map(([label, value]) => ({
        label,
        value,
        percent: Math.max((value / total) * 100, 6)
      }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 6);
  }

  private buildStatusBreakdown(orders: any[]): Array<{ label: string; value: number; percent: number }> {
    const counts = new Map<string, number>();

    orders.forEach(order => {
      const status = order.status || 'unknown';
      counts.set(status, (counts.get(status) || 0) + 1);
    });

    const total = orders.length || 1;
    return Array.from(counts.entries())
      .map(([label, value]) => ({
        label,
        value,
        percent: Math.max((value / total) * 100, 8)
      }))
      .sort((a, b) => b.value - a.value);
  }
}