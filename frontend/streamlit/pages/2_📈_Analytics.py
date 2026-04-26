import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.api_client import APIClient

st.set_page_config(page_title="Analytics", page_icon="📈", layout="wide")

if 'token' not in st.session_state:
    st.error("Por favor, inicia sesión primero")
    st.stop()

api_client = APIClient(st.session_state.token)

st.title("📈 Análisis Avanzado")
st.markdown("---")

# Filtros
col1, col2 = st.columns(2)
with col1:
    days = st.slider("Últimos días", 7, 90, 30)
with col2:
    analysis_type = st.selectbox("Tipo de análisis", 
                                 ["Ventas", "Productos", "Clientes"])

st.markdown("---")

if analysis_type == "Ventas":
    # Gráfico de tendencia
    timeline = api_client.get_sales_timeline(days=days)
    if timeline:
        df = pd.DataFrame(timeline)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['date'], y=df['total_sales'],
                                 mode='lines+markers',
                                 name='Ventas',
                                 line=dict(color='blue', width=2)))
        fig.add_trace(go.Bar(x=df['date'], y=df['orders_count'],
                             name='Pedidos', yaxis='y2',
                             marker_color='orange'))
        
        fig.update_layout(
            title='Evolución de Ventas',
            xaxis_title='Fecha',
            yaxis_title='Ventas ($)',
            yaxis2=dict(title='Número de pedidos', overlaying='y', side='right'),
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Estadísticas
        col1, col2, col3 = st.columns(3)
        col1.metric("Total ventas", f"${df['total_sales'].sum():,.2f}")
        col2.metric("Total pedidos", df['orders_count'].sum())
        col3.metric("Promedio diario", f"${df['total_sales'].mean():,.2f}")
    else:
        st.info("No hay datos disponibles")

elif analysis_type == "Productos":
    st.subheader("Análisis de Productos")
    
    top_products = api_client.get_top_products(days=days, limit=10)
    if top_products:
        df = pd.DataFrame(top_products)
        
        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(df, x='name', y='total_quantity',
                        title='Cantidad vendida',
                        labels={'total_quantity': 'Unidades', 'name': 'Producto'})
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(df, x='name', y='total_revenue',
                        title='Ingresos generados',
                        labels={'total_revenue': 'Ingresos ($)', 'name': 'Producto'})
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Tabla detallada
        st.subheader("Detalle de productos")
        st.dataframe(df[['name', 'total_quantity', 'total_revenue']])
    else:
        st.info("No hay datos disponibles")

else:  # Clientes
    st.subheader("Análisis de Clientes")
    
    customer_stats = api_client.get_customer_statistics()
    if customer_stats:
        col1, col2 = st.columns(2)
        col1.metric("Promedio de compra", f"${customer_stats.get('average', 0):,.2f}")
        
        freq_data = customer_stats.get('frequency_distribution', [])
        if freq_data:
            df_freq = pd.DataFrame(freq_data)
            fig = px.pie(df_freq, values='count', names='range',
                        title='Distribución de frecuencia de compras')
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos disponibles")