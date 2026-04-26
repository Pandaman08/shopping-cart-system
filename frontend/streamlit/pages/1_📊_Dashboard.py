import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.api_client import APIClient

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

if 'token' not in st.session_state:
    st.error("Por favor, inicia sesión primero")
    st.stop()

api_client = APIClient(st.session_state.token)

st.title("📊 Dashboard de Ventas")
st.markdown("---")

# Métricas principales
col1, col2, col3, col4 = st.columns(4)

# Ventas del día
today_data = api_client.get_statistics_daily()
col1.metric("💰 Ventas del día", f"${today_data.get('total_sales', 0):,.2f}")
col2.metric("📦 Pedidos hoy", today_data.get('orders_count', 0))
col3.metric("🎫 Ticket promedio", f"${today_data.get('average_ticket', 0):,.2f}")

# Productos más vendidos
top_products = api_client.get_top_products(days=30, limit=1)
if top_products:
    col4.metric("⭐ Producto estrella", top_products[0]['name'])

st.markdown("---")

# Gráficos
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Evolución de Ventas - Últimos 30 días")
    timeline = api_client.get_sales_timeline(days=30)
    if timeline:
        df = pd.DataFrame(timeline)
        fig = px.line(df, x='date', y='total_sales', 
                      title='Ventas diarias',
                      labels={'total_sales': 'Ventas ($)', 'date': 'Fecha'})
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos disponibles")

with col2:
    st.subheader("📊 Distribución por Categoría")
    categories = api_client.get_products_by_category()
    if categories:
        df = pd.DataFrame(categories)
        fig = px.pie(df, values='count', names='category', 
                     title='Productos por categoría')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos disponibles")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("👥 Comportamiento de Clientes")
    customer_stats = api_client.get_customer_statistics()
    
    if customer_stats:
        st.metric("Promedio de compra por usuario", 
                 f"${customer_stats.get('average', 0):,.2f}")
        
        st.markdown("### Frecuencia de compras")
        freq_data = customer_stats.get('frequency_distribution', [])
        if freq_data:
            df_freq = pd.DataFrame(freq_data)
            st.bar_chart(df_freq.set_index('range')['count'])
    else:
        st.info("No hay datos disponibles")

with col2:
    st.subheader("🏆 Top Productos")
    top_products = api_client.get_top_products(days=30, limit=5)
    if top_products:
        df_top = pd.DataFrame(top_products)
        fig = px.bar(df_top, x='name', y='total_quantity', 
                     title='Productos más vendidos',
                     labels={'total_quantity': 'Unidades vendidas', 'name': 'Producto'})
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos disponibles")

st.markdown("---")

if st.button("🔄 Actualizar datos"):
    st.rerun()