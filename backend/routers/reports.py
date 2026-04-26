from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel
from auth import get_admin_user
from database.connection import get_db
from services.pdf_generator import PDFReportGenerator

router = APIRouter(prefix="/api/reports", tags=["reports"])

class ReportFilters(BaseModel):
    start_date: date
    end_date: date
    include_kpis: bool = True
    include_charts: bool = False

@router.post("/orders-pdf")
async def generate_orders_report(
    filters: ReportFilters,
    admin_user=Depends(get_admin_user),
    db=Depends(get_db)
):
    async with db.acquire() as conn:
        # Get orders data
        orders = await conn.fetch(
            """
            SELECT 
                o.id,
                o.total_amount,
                o.status,
                o.created_at,
                o.paid_at,
                u.full_name as user_name,
                u.email as user_email,
                COUNT(oi.id) as items_count
            FROM orders o
            JOIN users u ON o.user_id = u.id
            LEFT JOIN order_items oi ON o.id = oi.order_id
            WHERE DATE(o.created_at) BETWEEN $1 AND $2
                AND o.status = 'paid'
            GROUP BY o.id, u.full_name, u.email
            ORDER BY o.created_at DESC
            """,
            filters.start_date, filters.end_date
        )
        
        # Get detailed items
        orders_list = []
        for order in orders:
            items = await conn.fetch(
                """
                SELECT product_name, quantity, unit_price, subtotal
                FROM order_items
                WHERE order_id = $1
                """,
                order['id']
            )
            
            orders_list.append({
                'id': str(order['id']),
                'user_name': order['user_name'],
                'user_email': order['user_email'],
                'total': float(order['total_amount']),
                'status': order['status'],
                'date': order['created_at'].isoformat(),
                'items_count': order['items_count'],
                'items': [dict(item) for item in items]
            })
        
        # Generate PDF
        generator = PDFReportGenerator()
        pdf_content = generator.generate_orders_report(
            orders_list,
            filters.start_date.isoformat(),
            filters.end_date.isoformat(),
            include_kpis=filters.include_kpis
        )
        
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=reporte_pedidos_{datetime.now().strftime('%Y%m%d')}.pdf"
            }
        )

@router.post("/executive-pdf")
async def generate_executive_report(
    filters: ReportFilters,
    admin_user=Depends(get_admin_user),
    db=Depends(get_db)
):
    async with db.acquire() as conn:
        # Get KPIs
        kpis = await conn.fetchrow(
            """
            SELECT 
                COUNT(*) as total_orders,
                COALESCE(SUM(total_amount), 0) as total_revenue,
                COALESCE(AVG(total_amount), 0) as avg_order_value,
                COUNT(DISTINCT user_id) as unique_customers
            FROM orders
            WHERE DATE(created_at) BETWEEN $1 AND $2
                AND status = 'paid'
            """,
            filters.start_date, filters.end_date
        )
        
        # Get top products
        top_products = await conn.fetch(
            """
            SELECT 
                p.name,
                SUM(oi.quantity) as quantity_sold,
                SUM(oi.subtotal) as revenue
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.id
            JOIN products p ON oi.product_id = p.id
            WHERE DATE(o.created_at) BETWEEN $1 AND $2
                AND o.status = 'paid'
            GROUP BY p.id, p.name
            ORDER BY revenue DESC
            LIMIT 5
            """,
            filters.start_date, filters.end_date
        )
        
        generator = PDFReportGenerator()
        pdf_content = generator.generate_executive_report(
            kpis=dict(kpis),
            top_products=[dict(p) for p in top_products],
            start_date=filters.start_date.isoformat(),
            end_date=filters.end_date.isoformat()
        )
        
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=reporte_ejecutivo_{datetime.now().strftime('%Y%m%d')}.pdf"
            }
        )