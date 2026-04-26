import streamlit as st
import requests
from datetime import datetime
import os

st.set_page_config(
    page_title="Sistema de Ventas",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar estado de sesión
if 'token' not in st.session_state:
    st.session_state.token = None
if 'user' not in st.session_state:
    st.session_state.user = None

# API base URL
API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000/api")

# Sidebar para autenticación
with st.sidebar:
    st.image("https://via.placeholder.com/150x100?text=Logo", use_column_width=True)
    st.title("🛒 Sistema de Ventas")
    
    if not st.session_state.token:
        st.markdown("### Autenticación")
        
        auth_choice = st.radio("", ["Iniciar Sesión", "Registrarse"])
        
        if auth_choice == "Iniciar Sesión":
            email = st.text_input("Email")
            password = st.text_input("Contraseña", type="password")
            
            if st.button("Iniciar Sesión", type="primary"):
                try:
                    response = requests.post(f"{API_BASE}/auth/login", 
                                           json={"email": email, "password": password})
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.token = data['access_token']
                        st.session_state.user = data['user']
                        st.success("¡Login exitoso!")
                        st.rerun()
                    else:
                        st.error("Credenciales inválidas")
                except Exception as e:
                    st.error(f"Error de conexión: {e}")
        
        else:  # Registro
            full_name = st.text_input("Nombre completo")
            email = st.text_input("Email")
            password = st.text_input("Contraseña", type="password")
            confirm_password = st.text_input("Confirmar contraseña", type="password")
            
            if st.button("Registrarse", type="primary"):
                if password != confirm_password:
                    st.error("Las contraseñas no coinciden")
                elif not all([full_name, email, password]):
                    st.error("Todos los campos son requeridos")
                else:
                    try:
                        response = requests.post(f"{API_BASE}/auth/register",
                                               json={"full_name": full_name, 
                                                     "email": email, 
                                                     "password": password})
                        if response.status_code == 200:
                            data = response.json()
                            st.session_state.token = data['access_token']
                            st.session_state.user = data['user']
                            st.success("¡Registro exitoso!")
                            st.rerun()
                        else:
                            st.error(response.json().get('detail', 'Error en registro'))
                    except Exception as e:
                        st.error(f"Error de conexión: {e}")
    
    else:
        # Usuario autenticado
        st.markdown(f"### 👤 {st.session_state.user.get('full_name', 'Usuario')}")
        st.markdown(f"Email: {st.session_state.user.get('email', '')}")
        st.markdown(f"Rol: {st.session_state.user.get('role', 'cliente')}")
        
        st.markdown("---")
        st.markdown("### 📊 Navegación")
        
        # Menú según rol
        if st.button("📊 Dashboard Principal"):
            st.switch_page("pages/1_📊_Dashboard.py")
        
        if st.button("📈 Análisis Avanzado"):
            st.switch_page("pages/2_📈_Analytics.py")
        
        if st.button("📄 Generar Reportes"):
            st.switch_page("pages/3_📄_Reportes.py")
        
        st.markdown("---")
        
        if st.button("🚪 Cerrar Sesión", type="secondary"):
            st.session_state.token = None
            st.session_state.user = None
            st.rerun()

# Contenido principal
if not st.session_state.token:
    st.markdown("""
    # 🛒 Bienvenido al Sistema de Ventas
    
    ### Accede para visualizar:
    - 📊 Dashboard interactivo con métricas clave
    - 📈 Análisis avanzado de ventas
    - 📄 Generación de reportes PDF
    - 📦 Gestión de productos y pedidos
    
    ### Credenciales de prueba:
    - **Admin**: admin@example.com / admin123
    - **Cliente**: cliente1@example.com / cliente123
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("💡 **Tip:** Usa el menú lateral para iniciar sesión")
    with col2:
        st.success("✅ Sistema listo para usar")
else:
    st.markdown(f"""
    # ¡Bienvenido, {st.session_state.user.get('full_name', 'Usuario')}!
    
    ### Selecciona una opción del menú lateral para comenzar
    
    ### Accesos rápidos:
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Dashboard", use_container_width=True):
            st.switch_page("pages/1_📊_Dashboard.py")
    
    with col2:
        if st.button("📈 Analytics", use_container_width=True):
            st.switch_page("pages/2_📈_Analytics.py")
    
    with col3:
        if st.button("📄 Reportes", use_container_width=True):
            st.switch_page("pages/3_📄_Reportes.py")
    
    st.markdown("---")
    st.caption(f"Último acceso: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")