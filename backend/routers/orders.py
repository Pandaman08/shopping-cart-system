from fastapi import APIRouter, Depends, HTTPException
from typing import List
from models import OrderCreate, OrderResponse
from auth import get_current_user, get_admin_user
from database.connection import get_db
from datetime import datetime

router = APIRouter(prefix="/api/orders", tags=["orders"])

@router.post("", response_model=dict)
async def create_order(
    order_data: OrderCreate,
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    async with db.acquire() as conn:
        async with conn.transaction():
            # Get active cart
            cart = await conn.fetchrow(
                """
                SELECT c.id, c.user_id, 
                       json_agg(json_build_object(
                           'product_id', ci.product_id,
                           'quantity', ci.quantity,
                           'unit_price', ci.unit_price,
                           'product_name', p.name
                       )) as items
                FROM carts c
                JOIN cart_items ci ON c.id = ci.cart_id
                JOIN products p ON ci.product_id = p.id
                WHERE c.user_id = $1 AND c.status = 'active'
                GROUP BY c.id
                """,
                current_user['id']
            )
            
            if not cart or not cart['items']:
                raise HTTPException(status_code=400, detail="Cart is empty")
            
            # Calculate total
            total = 0
            for item in cart['items']:
                total += item['quantity'] * item['unit_price']
            
            # Check stock for all items
            for item in cart['items']:
                product = await conn.fetchrow(
                    "SELECT stock FROM products WHERE id = $1",
                    item['product_id']
                )
                if product['stock'] < item['quantity']:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Insufficient stock for product {item['product_name']}"
                    )
            
            # Create order
            order = await conn.fetchrow(
                """
                INSERT INTO orders (user_id, cart_id, total_amount, payment_method, 
                                   shipping_address, status)
                VALUES ($1, $2, $3, $4, $5, 'pending')
                RETURNING id, created_at
                """,
                current_user['id'], cart['id'], total,
                order_data.payment_method, order_data.shipping_address
            )
            
            # Create order items and update stock
            for item in cart['items']:
                await conn.execute(
                    """
                    INSERT INTO order_items (order_id, product_id, product_name, 
                                           quantity, unit_price)
                    VALUES ($1, $2, $3, $4, $5)
                    """,
                    order['id'], item['product_id'], item['product_name'],
                    item['quantity'], item['unit_price']
                )
                
                # Update stock
                await conn.execute(
                    "UPDATE products SET stock = stock - $1 WHERE id = $2",
                    item['quantity'], item['product_id']
                )
            
            # Mark cart as completed
            await conn.execute(
                "UPDATE carts SET status = 'completed' WHERE id = $1",
                cart['id']
            )
            
            # Simulate payment processing (in real app, integrate with payment gateway)
            await conn.execute(
                """
                UPDATE orders 
                SET status = 'paid', paid_at = NOW()
                WHERE id = $1
                """,
                order['id']
            )
            
            return {
                "order_id": str(order['id']),
                "total": float(total),
                "status": "paid",
                "created_at": order['created_at'].isoformat()
            }

@router.get("", response_model=List[OrderResponse])
async def get_user_orders(
    current_user=Depends(get_current_user),
    db=Depends(get_db)
):
    async with db.acquire() as conn:
        orders = await conn.fetch(
            """
            SELECT o.*, u.full_name as user_name
            FROM orders o
            JOIN users u ON o.user_id = u.id
            WHERE o.user_id = $1
            ORDER BY o.created_at DESC
            """,
            current_user['id']
        )
        
        result = []
        for order in orders:
            items = await conn.fetch(
                """
                SELECT * FROM order_items
                WHERE order_id = $1
                """,
                order['id']
            )
            
            order_dict = dict(order)
            order_dict['id'] = str(order_dict['id'])
            order_dict['user_id'] = str(order_dict['user_id'])
            order_dict['items'] = [dict(item) for item in items]
            order_dict['items'] = [{**item, 'id': str(item['id'])} for item in order_dict['items']]
            
            result.append(order_dict)
        
        return result

@router.get("/admin/all")
async def get_all_orders(
    admin_user=Depends(get_admin_user),
    db=Depends(get_db)
):
    async with db.acquire() as conn:
        orders = await conn.fetch(
            """
            SELECT o.*, u.full_name as user_name, u.email as user_email
            FROM orders o
            JOIN users u ON o.user_id = u.id
            ORDER BY o.created_at DESC
            """
        )
        
        return [dict(order) for order in orders]