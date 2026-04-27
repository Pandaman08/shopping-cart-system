import { Injectable } from '@angular/core';
import { CanActivate, Router } from '@angular/router';

@Injectable({ providedIn: 'root' })
export class CustomerGuard implements CanActivate {
  constructor(private readonly router: Router) {}

  canActivate(): boolean {
    const user = JSON.parse(localStorage.getItem('currentUser') || 'null');

    if (user?.role === 'admin') {
      this.router.navigate(['/admin/dashboard']);
      return false;
    }

    return true;
  }
}