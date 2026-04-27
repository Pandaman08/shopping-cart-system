from fastapi import APIRouter, Depends, HTTPException
from models import CartItemCreate, CartResponse
from auth import get_current_user
from database.connection import get_db
from services.cache_service import get_cache, CacheService
import json

router = APIRouter(prefix="/api/cart", tags=["cart"])

async def get_or_create_cart(user_id: str, conn, cache: CacheService):
    # Try cache first
    cached_cart = await cache.get(f"cart:{user_id}")
    if cached_cart:
        return json.loads(cached_cart)
    
    # Get from database
    cart = await conn.fetchrow(
        """
        SELECT id, user_id, created_at, updated_at
        FROM carts
        WHERE user_id = $1 AND status = 'active'
        """,
        user_id
    )
    
    if not cart:
        cart = await conn.fetchrow(
            """
            INSERT INTO carts (user_id, status)
            VALUES ($1, 'active')
            RETURNING id, user_id, created_at, updated_at
            """,
            user_id
        )
    
    cart_dict = dict(cart)
    cart_dict['id'] = str(cart_dict['id'])
    cart_dict['user_id'] = str(cart_dict['user_id'])
    
    # Get items
    items = await conn.fetch(
        """
        SELECT ci.id, ci.product_id, ci.quantity, ci.unit_price,
             p.name as product_name, p.price as current_price, p.image_url as product_image
        FROM cart_items ci
        JOIN products p ON ci.product_id = p.id
        WHERE ci.cart_id = $1
        """,
        cart['id']
    )
    
    cart_items = []
    total = 0
    for item in items:
        subtotal = item['quantity'] * item['unit_price']
        total += subtotal
        cart_items.append({
            'id': str(item['id']),
            'product_id': str(item['product_id']),
            'product_name': item['product_name'],
            'product_image': item['product_image'],
            'product_price': float(item['unit_price']),
            'quantity': item['quantity'],
            'unit_price': float(item['unit_price']),
            'subtotal': float(subtotal)
        })
    
    result = {
        **cart_dict,
        'items': cart_items,
        'total': float(total),
        'item_count': len(cart_items)
    }
    
    # Cache for 5 minutes
    await cache.set(f"cart:{user_id}", json.dumps(result, default=str), expire=300)
    
    return result

@router.get("", response_model=CartResponse)
async def get_cart(
    current_user=Depends(get_current_user),
    db=Depends(get_db),
    cache=Depends(get_cache)
):
    async with db.acquire() as conn:
        cart = await get_or_create_cart(current_user['id'], conn, cache)
        return cart

@router.post("/items")
async def add_to_cart(
    item: CartItemCreate,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
    cache=Depends(get_cache)
):
    async with db.acquire() as conn:
        async with conn.transaction():
            # Get product
            product = await conn.fetchrow(
                "SELECT id, name, price, stock FROM products WHERE id = $1 AND is_active = true",
                item.product_id
            )
            
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
            
            if product['stock'] < item.quantity:
                raise HTTPException(status_code=400, detail="Insufficient stock")
            
            # Get active cart
            cart = await conn.fetchrow(
                "SELECT id FROM carts WHERE user_id = $1 AND status = 'active'",
                current_user['id']
            )
            
            if not cart:
                cart = await conn.fetchrow(
                    "INSERT INTO carts (user_id, status) VALUES ($1, 'active') RETURNING id",
                    current_user['id']
                )
            
            # Check if item already in cart
            existing = await conn.fetchrow(
                """
                SELECT id, quantity FROM cart_items
                WHERE cart_id = $1 AND product_id = $2
                """,
                cart['id'], item.product_id
            )
            
            if existing:
                new_quantity = existing['quantity'] + item.quantity
                await conn.execute(
                    """
                    UPDATE cart_items
                    SET quantity = $1, unit_price = $2
                    WHERE id = $3
                    """,
                    new_quantity, product['price'], existing['id']
                )
            else:
                await conn.execute(
                    """
                    INSERT INTO cart_items (cart_id, product_id, quantity, unit_price)
                    VALUES ($1, $2, $3, $4)
                    """,
                    cart['id'], item.product_id, item.quantity, product['price']
                )
            
            # Invalidate cache
            await cache.delete(f"cart:{current_user['id']}")
            
            return {"message": "Product added to cart"}

@router.put("/items/{product_id}")
async def update_cart_item(
    product_id: str,
    item: CartItemCreate,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
    cache=Depends(get_cache)
):
    async with db.acquire() as conn:
        async with conn.transaction():
            # Get product
            product = await conn.fetchrow(
                "SELECT price, stock FROM products WHERE id = $1 AND is_active = true",
                product_id
            )
            
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
            
            if product['stock'] < item.quantity:
                raise HTTPException(status_code=400, detail="Insufficient stock")
            
            # Get active cart
            cart = await conn.fetchrow(
                "SELECT id FROM carts WHERE user_id = $1 AND status = 'active'",
                current_user['id']
            )
            
            if not cart:
                raise HTTPException(status_code=404, detail="Cart not found")
            
            result = await conn.execute(
                """
                UPDATE cart_items
                SET quantity = $1, unit_price = $2
                WHERE cart_id = $3 AND product_id = $4
                """,
                item.quantity, product['price'], cart['id'], product_id
            )
            
            if result == "UPDATE 0":
                raise HTTPException(status_code=404, detail="Item not found in cart")
            
            # Invalidate cache
            await cache.delete(f"cart:{current_user['id']}")
            
            return {"message": "Cart updated"}

@router.delete("/items/{product_id}")
async def remove_from_cart(
    product_id: str,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
    cache=Depends(get_cache)
):
    async with db.acquire() as conn:
        # Get active cart
        cart = await conn.fetchrow(
            "SELECT id FROM carts WHERE user_id = $1 AND status = 'active'",
            current_user['id']
        )
        
        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found")
        
        await conn.execute(
            "DELETE FROM cart_items WHERE cart_id = $1 AND product_id = $2",
            cart['id'], product_id
        )
        
        # Invalidate cache
        await cache.delete(f"cart:{current_user['id']}")
        
        return {"message": "Item removed from cart"}