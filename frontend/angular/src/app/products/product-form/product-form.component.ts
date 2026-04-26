import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { ProductService } from '../../services/product.service';

@Component({
  selector: 'app-product-form',
  templateUrl: './product-form.component.html',
  styleUrls: ['./product-form.component.css']
})
export class ProductFormComponent implements OnInit {
  productForm: FormGroup;
  isEdit = false;
  productId: string | null = null;
  loading = false;
  categories: any[] = [];

  constructor(
    private fb: FormBuilder,
    private productService: ProductService,
    private route: ActivatedRoute,
    private router: Router
  ) {
    this.productForm = this.fb.group({
      name: ['', [Validators.required, Validators.minLength(3)]],
      description: ['', Validators.required],
      price: ['', [Validators.required, Validators.min(0.01)]],
      stock: ['', [Validators.required, Validators.min(0)]],
      category_id: [''],
      image_url: ['']
    });
  }

  ngOnInit() {
    this.loadCategories();
    
    this.productId = this.route.snapshot.paramMap.get('id');
    if (this.productId) {
      this.isEdit = true;
      this.loadProduct();
    }
  }

  loadCategories() {
    this.productService.getCategories().subscribe({
      next: (categories) => {
        this.categories = categories;
      },
      error: (error) => console.error('Error loading categories:', error)
    });
  }

  loadProduct() {
    if (this.productId) {
      this.productService.getProduct(this.productId).subscribe({
        next: (product) => {
          this.productForm.patchValue({
            name: product.name,
            description: product.description,
            price: product.price,
            stock: product.stock,
            category_id: product.category_id,
            image_url: product.image_url
          });
        },
        error: (error) => {
          console.error('Error loading product:', error);
          this.router.navigate(['/admin/dashboard']);
        }
      });
    }
  }

  onSubmit() {
    if (this.productForm.invalid) {
      Object.keys(this.productForm.controls).forEach(key => {
        this.productForm.get(key)?.markAsTouched();
      });
      return;
    }

    this.loading = true;
    const productData = this.productForm.value;

    if (this.isEdit && this.productId) {
      this.productService.updateProduct(this.productId, productData).subscribe({
        next: () => {
          alert('Producto actualizado exitosamente');
          this.router.navigate(['/admin/dashboard']);
        },
        error: (error) => {
          alert('Error al actualizar el producto: ' + error.message);
          this.loading = false;
        }
      });
    } else {
      this.productService.createProduct(productData).subscribe({
        next: () => {
          alert('Producto creado exitosamente');
          this.router.navigate(['/admin/dashboard']);
        },
        error: (error) => {
          alert('Error al crear el producto: ' + error.message);
          this.loading = false;
        }
      });
    }
  }
}