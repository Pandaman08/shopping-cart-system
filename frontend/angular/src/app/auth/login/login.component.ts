import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { CartService } from '../../services/cart.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {
  loginForm: FormGroup;
  errorMessage = '';
  loading = false;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private cartService: CartService,
    private router: Router,
    private route: ActivatedRoute
  ) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]]
    });
  }

  onSubmit() {
    if (this.loginForm.invalid) {
      return;
    }

    this.loading = true;
    this.errorMessage = '';

    this.authService.login(this.loginForm.value).subscribe({
      next: (response) => {
        const defaultRoute = response?.user?.role === 'admin' ? '/admin/dashboard' : '/products';
        const returnUrl = this.route.snapshot.queryParamMap.get('returnUrl') || defaultRoute;

        this.cartService.syncPendingItems().subscribe({
          next: () => this.router.navigateByUrl(returnUrl),
          error: () => this.router.navigateByUrl(returnUrl)
        });
      },
      error: (error) => {
        this.errorMessage = error.error?.detail || 'Error al iniciar sesión';
        this.loading = false;
      }
    });
  }
}