import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LoginComponent } from './auth/login/login.component';
import { RegisterComponent } from './auth/register/register.component';
import { ProductListComponent } from './products/product-list/product-list.component';
import { ProductDetailComponent } from './products/product-detail/product-detail.component';
import { ProductFormComponent } from './products/product-form/product-form.component';
import { CartComponent } from './cart/cart.component';
import { CheckoutComponent } from './orders/checkout/checkout.component';
import { AdminDashboardComponent } from './admin/admin-dashboard/admin-dashboard.component';
import { ReportsComponent } from './admin/reports/reports.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { AuthGuard } from './guards/auth.guard';
import { AdminGuard } from './guards/admin.guard';
import { CustomerGuard } from './guards/customer.guard';

const routes: Routes = [
  { path: '', redirectTo: '/products', pathMatch: 'full' },
  { path: 'dashboard', component: DashboardComponent, canActivate: [CustomerGuard] },
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  { path: 'products', component: ProductListComponent, canActivate: [CustomerGuard] },
  { path: 'products/:id', component: ProductDetailComponent, canActivate: [CustomerGuard] },
  { path: 'cart', component: CartComponent, canActivate: [AuthGuard, CustomerGuard] },
  { path: 'checkout', component: CheckoutComponent, canActivate: [AuthGuard, CustomerGuard] },
  { path: 'orders', redirectTo: '/products', pathMatch: 'full' },
  { path: 'admin/products/new', component: ProductFormComponent, canActivate: [AdminGuard] },
  { path: 'admin/products/edit/:id', component: ProductFormComponent, canActivate: [AdminGuard] },
  { path: 'admin/dashboard', component: AdminDashboardComponent, canActivate: [AdminGuard] },
  { path: 'admin/reports', component: ReportsComponent, canActivate: [AdminGuard] }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }