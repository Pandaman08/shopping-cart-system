from fastapi import APIRouter, Depends, Query
from datetime import date, datetime, timedelta
from auth import get_admin_user
from database.connection import get_db

router = APIRouter(prefix="/api/statistics", tags=["statistics"])

@router.get("/sales/daily")
async def daily_sales(
    date: str | None = Query(None),
    admin_user=Depends(get_admin_user),
    db=Depends(get_db)
):
    if not date:
        target_date = datetime.now().date()
    else:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    
    async with db.acquire() as conn:
        result = await conn.fetchrow(
            """
            SELECT 
                COALESCE(SUM(total_amount), 0) as total_sales,
                COUNT(*) as orders_count,
                COALESCE(AVG(total_amount), 0) as average_ticket
            FROM orders
            WHERE DATE(created_at) = $1::DATE AND status = 'paid'
            """,
            target_date
        )
        
        return dict(result)

@router.get("/sales/timeline")
async def sales_timeline(
    days: int = Query(30, ge=1, le=365),
    admin_user=Depends(get_admin_user),
    db=Depends(get_db)
):
    days_text = str(days)

    async with db.acquire() as conn:
        results = await conn.fetch(
            """
            SELECT 
                DATE(created_at) as date,
                COALESCE(SUM(total_amount), 0) as total_sales,
                COUNT(*) as orders_count
            FROM orders
            WHERE created_at >= NOW() - (($1 || ' days')::INTERVAL)
                AND status = 'paid'
            GROUP BY DATE(created_at)
            ORDER BY date ASC
            """,
            days_text
        )
        
        return [dict(row) for row in results]

@router.get("/top-products")
async def top_products(
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(10, ge=1, le=50),
    admin_user=Depends(get_admin_user),
    db=Depends(get_db)
):
    days_text = str(days)

    async with db.acquire() as conn:
        results = await conn.fetch(
            """
            SELECT 
                p.id,
                p.name,
                SUM(oi.quantity) as total_quantity,
                SUM(oi.subtotal) as total_revenue
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.id
            JOIN products p ON oi.product_id = p.id
            WHERE o.created_at >= NOW() - (($1 || ' days')::INTERVAL)
                AND o.status = 'paid'
            GROUP BY p.id, p.name
            ORDER BY total_quantity DESC
            LIMIT $2
            """,
            days_text, limit
        )
        
        return [dict(row) for row in results]

@router.get("/products/by-category")
async def products_by_category(
    admin_user=Depends(get_admin_user),
    db=Depends(get_db)
):
    async with db.acquire() as conn:
        results = await conn.fetch(
            """
            SELECT 
                c.name as category,
                COUNT(p.id) as count,
                COALESCE(SUM(oi.subtotal), 0) as revenue
            FROM categories c
            LEFT JOIN products p ON c.id = p.category_id AND p.is_active = true
            LEFT JOIN order_items oi ON p.id = oi.product_id
            LEFT JOIN orders o ON oi.order_id = o.id AND o.status = 'paid'
            GROUP BY c.id, c.name
            ORDER BY count DESC
            """
        )
        
        return [dict(row) for row in results]

@router.get("/customer/avg-purchase")
async def average_purchase_per_customer(
    admin_user=Depends(get_admin_user),
    db=Depends(get_db)
):
    async with db.acquire() as conn:
        # Average purchase per user
        avg_result = await conn.fetchrow(
            """
            SELECT 
                COALESCE(AVG(user_total), 0) as average
            FROM (
                SELECT user_id, SUM(total_amount) as user_total
                FROM orders
                WHERE status = 'paid'
                GROUP BY user_id
            ) as user_totals
            """
        )
        
        # Frequency distribution
        freq_results = await conn.fetch(
            """
            SELECT 
                CASE 
                    WHEN order_count = 1 THEN '1 compra'
                    WHEN order_count BETWEEN 2 AND 5 THEN '2-5 compras'
                    WHEN order_count BETWEEN 6 AND 10 THEN '6-10 compras'
                    ELSE '10+ compras'
                END as range,
                COUNT(*) as count
            FROM (
                SELECT user_id, COUNT(*) as order_count
                FROM orders
                WHERE status = 'paid'
                GROUP BY user_id
            ) as user_orders
            GROUP BY range
            ORDER BY MIN(order_count)
            """
        )
        
        return {
            "average": float(avg_result['average']),
            "frequency_distribution": [dict(row) for row in freq_results]
        }