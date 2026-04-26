from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from models import ProductCreate, ProductUpdate, ProductResponse
from auth import get_current_user, get_admin_user
from database.connection import get_db
import asyncpg

router = APIRouter(prefix="/api/products", tags=["products"])

@router.get("", response_model=dict)
async def get_products(
    category_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db=Depends(get_db)
):
    offset = (page - 1) * limit
    
    async with db.acquire() as conn:
        # Build query
        where_clauses = ["p.is_active = true"]
        params = []
        param_index = 1
        
        if category_id:
            where_clauses.append(f"p.category_id = ${param_index}")
            params.append(category_id)
            param_index += 1
        
        if search:
            where_clauses.append(f"p.name ILIKE $${param_index}")
            params.append(f"%{search}%")
            param_index += 1
        
        where_sql = " AND ".join(where_clauses)
        
        # Get total count
        count_query = f"""
            SELECT COUNT(*) as total
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE {where_sql}
        """
        total = await conn.fetchval(count_query, *params)
        
        # Get products
        query = f"""
            SELECT p.*, c.name as category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE {where_sql}
            ORDER BY p.created_at DESC
            LIMIT ${param_index} OFFSET ${param_index + 1}
        """
        params.extend([limit, offset])
        
        rows = await conn.fetch(query, *params)
        products = [dict(row) for row in rows]
        
        # Convert UUID to string
        for product in products:
            product['id'] = str(product['id'])
        
        return {
            "items": products,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit
        }


@router.get("/categories", response_model=List[dict])
async def get_categories(db=Depends(get_db)):
    async with db.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT id, name, description
            FROM categories
            ORDER BY name ASC
            """
        )
        return [dict(row) for row in rows]

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str, db=Depends(get_db)):
    async with db.acquire() as conn:
        product = await conn.fetchrow(
            """
            SELECT p.*, c.name as category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.id = $1
            """,
            product_id
        )
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        product_dict = dict(product)
        product_dict['id'] = str(product_dict['id'])
        return product_dict

@router.post("", response_model=ProductResponse)
async def create_product(
    product: ProductCreate,
    admin_user=Depends(get_admin_user),
    db=Depends(get_db)
):
    async with db.acquire() as conn:
        result = await conn.fetchrow(
            """
            INSERT INTO products (name, description, price, stock, category_id, image_url)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id, name, description, price, stock, category_id, image_url, is_active, created_at
            """,
            product.name, product.description, product.price,
            product.stock, product.category_id, product.image_url
        )
        
        product_dict = dict(result)
        product_dict['id'] = str(product_dict['id'])
        product_dict['category_name'] = None
        
        return product_dict

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    product: ProductUpdate,
    admin_user=Depends(get_admin_user),
    db=Depends(get_db)
):
    async with db.acquire() as conn:
        # Build dynamic update
        update_fields = []
        params = []
        param_index = 1
        
        if product.name is not None:
            update_fields.append(f"name = ${param_index}")
            params.append(product.name)
            param_index += 1
        
        if product.description is not None:
            update_fields.append(f"description = ${param_index}")
            params.append(product.description)
            param_index += 1
        
        if product.price is not None:
            update_fields.append(f"price = ${param_index}")
            params.append(product.price)
            param_index += 1
        
        if product.stock is not None:
            update_fields.append(f"stock = ${param_index}")
            params.append(product.stock)
            param_index += 1
        
        if product.category_id is not None:
            update_fields.append(f"category_id = ${param_index}")
            params.append(product.category_id)
            param_index += 1
        
        if product.is_active is not None:
            update_fields.append(f"is_active = ${param_index}")
            params.append(product.is_active)
            param_index += 1
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        params.append(product_id)
        query = f"""
            UPDATE products
            SET {', '.join(update_fields)}
            WHERE id = ${param_index}
            RETURNING id, name, description, price, stock, category_id, image_url, is_active, created_at
        """
        
        result = await conn.fetchrow(query, *params)
        
        if not result:
            raise HTTPException(status_code=404, detail="Product not found")
        
        product_dict = dict(result)
        product_dict['id'] = str(product_dict['id'])
        product_dict['category_name'] = None
        
        return product_dict

@router.delete("/{product_id}")
async def delete_product(
    product_id: str,
    admin_user=Depends(get_admin_user),
    db=Depends(get_db)
):
    async with db.acquire() as conn:
        result = await conn.execute(
            "UPDATE products SET is_active = false WHERE id = $1",
            product_id
        )
        
        if result == "UPDATE 0":
            raise HTTPException(status_code=404, detail="Product not found")
        
        return {"message": "Product deleted successfully"}