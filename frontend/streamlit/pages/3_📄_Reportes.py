import streamlit as st
from datetime import datetime, timedelta
import tempfile
import os
from utils.api_client import APIClient

st.set_page_config(page_title="Reportes", page_icon="📄", layout="wide")

if 'token' not in st.session_state:
    st.error("Por favor, inicia sesión primero")
    st.stop()

api_client = APIClient(st.session_state.token)

st.title("📄 Generación de Reportes PDF")
st.markdown("---")

# Filtros comunes
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Fecha inicio", datetime.now() - timedelta(days=30))
with col2:
    end_date = st.date_input("Fecha fin", datetime.now())

st.markdown("---")

# Tipo de reporte
report_type = st.radio("Selecciona el tipo de reporte",
                       ["Reporte de Pedidos", "Reporte Ejecutivo"],
                       horizontal=True)

st.markdown("---")

if report_type == "Reporte de Pedidos":
    st.subheader("Reporte Detallado de Pedidos")
    
    include_kpis = st.checkbox("Incluir KPIs", value=True)
    
    if st.button("📥 Generar Reporte de Pedidos", type="primary"):
        with st.spinner("Generando reporte..."):
            filters = {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "include_kpis": include_kpis
            }
            
            pdf_content = api_client.generate_orders_report(filters)
            
            if pdf_content:
                st.success("✅ Reporte generado exitosamente")
                
                # Botón de descarga
                st.download_button(
                    label="💾 Descargar PDF",
                    data=pdf_content,
                    file_name=f"reporte_pedidos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf"
                )
            else:
                st.error("Error al generar el reporte")

else:  # Reporte Ejecutivo
    st.subheader("Reporte Ejecutivo de Gestión")
    
    col1, col2 = st.columns(2)
    with col1:
        include_kpis = st.checkbox("Incluir KPIs", value=True)
    with col2:
        include_charts = st.checkbox("Incluir gráficos", value=False)
    
    if st.button("📥 Generar Reporte Ejecutivo", type="primary"):
        with st.spinner("Generando reporte ejecutivo..."):
            filters = {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "include_kpis": include_kpis,
                "include_charts": include_charts
            }
            
            pdf_content = api_client.generate_executive_report(filters)
            
            if pdf_content:
                st.success("✅ Reporte ejecutivo generado exitosamente")
                
                st.download_button(
                    label="💾 Descargar PDF Ejecutivo",
                    data=pdf_content,
                    file_name=f"reporte_ejecutivo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf"
                )
            else:
                st.error("Error al generar el reporte ejecutivo")