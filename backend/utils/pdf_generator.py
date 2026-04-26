from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import io
from datetime import datetime

class PDFReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#2E4053')
        ))
        self.styles.add(ParagraphStyle(
            name='CustomHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            textColor=colors.HexColor('#34495E')
        ))
    
    def generate_orders_report(self, orders, start_date, end_date, include_kpis=True):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
        elements = []
        
        # Title
        title = Paragraph(f"Reporte de Pedidos", self.styles['CustomTitle'])
        elements.append(title)
        
        date_range = Paragraph(f"Período: {start_date} a {end_date}", self.styles['Normal'])
        elements.append(date_range)
        elements.append(Spacer(1, 0.2*inch))
        
        if include_kpis and orders:
            total_orders = len(orders)
            total_revenue = sum(order['total'] for order in orders)
            avg_order = total_revenue / total_orders if total_orders > 0 else 0
            
            kpi_data = [
                ['Total Pedidos', 'Ingresos Totales', 'Ticket Promedio', 'Items Vendidos'],
                [str(total_orders), f"${total_revenue:,.2f}", f"${avg_order:,.2f}", 
                 str(sum(order['items_count'] for order in orders))]
            ]
            
            kpi_table = Table(kpi_data, colWidths=[1.8*inch, 1.8*inch, 1.8*inch, 1.8*inch])
            kpi_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2E4053')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 12),
                ('BOTTOMPADDING', (0,0), (-1,0), 12),
                ('BACKGROUND', (0,1), (-1,-1), colors.beige),
                ('GRID', (0,0), (-1,-1), 1, colors.black)
            ]))
            elements.append(kpi_table)
            elements.append(Spacer(1, 0.3*inch))
        
        # Orders table
        table_data = [['ID', 'Cliente', 'Email', 'Fecha', 'Total', 'Items', 'Estado']]
        for order in orders[:50]:  # Limit to 50 orders for PDF
            table_data.append([
                order['id'][:8],
                order['user_name'],
                order['user_email'],
                order['date'][:10],
                f"${order['total']:,.2f}",
                str(order['items_count']),
                order['status']
            ])
        
        order_table = Table(table_data, repeatRows=1)
        order_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#34495E')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-2), 1, colors.lightgrey),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        
        elements.append(order_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Footer
        footer = Paragraph(f"Generado el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                          self.styles['Normal'])
        elements.append(footer)
        
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_executive_report(self, kpis, top_products, start_date, end_date):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        
        # Title
        title = Paragraph("Reporte Ejecutivo", self.styles['CustomTitle'])
        elements.append(title)
        
        date_range = Paragraph(f"Período: {start_date} a {end_date}", self.styles['Normal'])
        elements.append(date_range)
        elements.append(Spacer(1, 0.3*inch))
        
        # KPIs Section
        elements.append(Paragraph("Indicadores Clave de Rendimiento", self.styles['CustomHeader']))
        
        kpi_data = [
            ['Métrica', 'Valor'],
            ['Total Pedidos', str(kpis['total_orders'])],
            ['Ingresos Totales', f"${kpis['total_revenue']:,.2f}"],
            ['Valor Promedio Pedido', f"${kpis['avg_order_value']:,.2f}"],
            ['Clientes Únicos', str(kpis['unique_customers'])]
        ]
        
        kpi_table = Table(kpi_data, colWidths=[2.5*inch, 2.5*inch])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2E4053')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(kpi_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Top Products
        if top_products:
            elements.append(Paragraph("Top 5 Productos Más Vendidos", self.styles['CustomHeader']))
            
            product_data = [['Producto', 'Cantidad', 'Ingresos']]
            for product in top_products:
                product_data.append([
                    product['name'][:40],
                    str(product['quantity_sold']),
                    f"${product['revenue']:,.2f}"
                ])
            
            product_table = Table(product_data, colWidths=[3*inch, 1.5*inch, 2*inch])
            product_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#34495E')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('ALIGN', (1,0), (2,0), 'CENTER'),
                ('ALIGN', (1,1), (2,-1), 'RIGHT'),
                ('GRID', (0,0), (-1,-1), 1, colors.lightgrey),
                ('TOPPADDING', (0,0), (-1,-1), 6),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ]))
            elements.append(product_table)
        
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()