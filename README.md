# 📦 Sistema de Carrito de Compras - Documentación Completa

## 📋 Tabla de Contenidos
- [Descripción General](#descripción-general)
- [Arquitectura del Sistema](#arquitectura-del-sistema)
- [Requisitos Previos](#requisitos-previos)
- [Instalación Paso a Paso](#instalación-paso-a-paso)
- [Configuración del Entorno](#configuración-del-entorno)
- [Ejecución del Proyecto](#ejecución-del-proyecto)
- [Solución de Problemas Comunes](#solución-de-problemas-comunes)
- [Credenciales de Prueba](#credenciales-de-prueba)
- [Endpoints de la API](#endpoints-de-la-api)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Despliegue en Producción](#despliegue-en-producción)

---

## 🚀 Descripción General

Sistema completo de comercio electrónico con:
- **Backend**: API RESTful con FastAPI (Python)
- **Frontend Principal**: Aplicación SPA con Angular 17
- **Dashboard Administrativo**: Interfaz analítica con Streamlit
- **Base de Datos**: PostgreSQL con caché Redis

### Características Principales
✅ Autenticación JWT (roles: cliente/admin)
✅ CRUD completo de productos
✅ Carrito de compras en tiempo real
✅ Procesamiento de pedidos
✅ Reportes PDF personalizados
✅ Dashboard con métricas y gráficos interactivos
✅ Estadísticas avanzadas de ventas

---

## 📌 Requisitos Previos

### Software Necesario
| Herramienta | Versión | Descarga |
|------------|---------|----------|
| **Node.js** | v18.x o superior | [https://nodejs.org/](https://nodejs.org/) |
| **Python** | 3.11 o superior | [https://www.python.org/](https://www.python.org/) |
| **PostgreSQL** | 15.x o superior | [https://www.postgresql.org/](https://www.postgresql.org/) |
| **Redis** | 7.x o superior | [https://redis.io/](https://redis.io/) |
| **Docker** (opcional) | 24.x o superior | [https://www.docker.com/](https://www.docker.com/) |

### Verificar Instalaciones
```bash
# Verificar Node.js
node --version  # Debería mostrar v18.x o superior

# Verificar npm
npm --version    # Debería mostrar 9.x o superior

# Verificar Python
python --version # Debería mostrar 3.11 o superior

# Verificar PostgreSQL
psql --version   # Debería mostrar 15.x o superior

# Verificar Redis
redis-server --version
```

---

## 🔧 Instalación Paso a Paso

### 1. Clonar el Repositorio
```bash
# Clonar el proyecto
git clone https://github.com/tu-usuario/shopping-cart-system.git

# Entrar al directorio
cd shopping-cart-system
```

### 2. Configurar Base de Datos PostgreSQL

#### Opción A: Usando terminal (Linux/Mac)
```bash
# Acceder a PostgreSQL
sudo -u postgres psql

# Dentro de PostgreSQL, ejecutar:
CREATE DATABASE cartdb;
CREATE USER cartuser WITH PASSWORD 'cartpass123';
GRANT ALL PRIVILEGES ON DATABASE cartdb TO cartuser;
\q

# Ejecutar seeders
python scripts/seed_data.py
```

#### Opción B: Usando pgAdmin (Windows)
1. Abre pgAdmin
2. Crea una nueva base de datos llamada `cartdb`
3. Ejecuta el script `scripts/seed_data.py` desde la terminal

### 3. Configurar Backend (FastAPI)

```bash
# Navegar al backend
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Crear archivo .env
cat > .env << EOF
DATABASE_URL=postgresql://cartuser:cartpass123@localhost:5432/cartdb
REDIS_URL=redis://localhost:6379
SECRET_KEY=mi-clave-secreta-super-segura-cambiar-en-produccion-2024
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
CORS_ORIGINS=["http://localhost:4200","http://localhost:8501"]
EOF
```

### 4. Configurar Frontend Angular

```bash
# Navegar al frontend Angular
cd ../frontend/angular

# Instalar Angular CLI globalmente (opcional pero recomendado)
npm install -g @angular/cli@17

# Instalar dependencias
npm install

# Si hay errores, limpiar caché e instalar de nuevo
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

### 5. Configurar Dashboard Streamlit

```bash
# Navegar al dashboard
cd ../streamlit

# Crear entorno virtual (si no existe)
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

---

## ⚙️ Configuración del Entorno

### Variables de Entorno Backend (`.env`)
```env
# Base de datos
DATABASE_URL=postgresql://cartuser:cartpass123@localhost:5432/cartdb

# Redis
REDIS_URL=redis://localhost:6379

# Seguridad
SECRET_KEY=tu-clave-secreta-muy-segura-aqui
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS
CORS_ORIGINS=["http://localhost:4200","http://localhost:8501"]

# Email (opcional para notificaciones)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-email@gmail.com
SMTP_PASSWORD=tu-contraseña
```

### Variables de Entorno Angular (`environment.ts`)
```typescript
// src/environments/environment.ts
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api'
};
```

---

## 🎯 Ejecución del Proyecto

### Opción 1: Ejecutar Todo con Docker (Recomendado para producción)

```bash
# En la raíz del proyecto
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose down
```

### Opción 2: Ejecutar Manualmente (Recomendado para desarrollo)

#### Terminal 1: Iniciar Redis
```bash
# En una terminal nueva
redis-server

# En Windows (usando WSL):
sudo service redis-server start
```

#### Terminal 2: Iniciar Backend
```bash
cd backend
source venv/bin/activate  # o venv\Scripts\activate en Windows
uvicorn main:app --reload --port 8000

# El backend estará disponible en: http://localhost:8000
# Documentación API: http://localhost:8000/docs
```

#### Terminal 3: Iniciar Frontend Angular
```bash
cd frontend/angular
npm start
# o
ng serve --open

# La aplicación estará en: http://localhost:4200
```

#### Terminal 4: Iniciar Dashboard Streamlit
```bash
cd frontend/streamlit
source venv/bin/activate
streamlit run streamlit_app.py

# El dashboard estará en: http://localhost:8501
```

---

## 🐛 Solución de Problemas Comunes

### Problema 1: Error "psycopg2" no se instala

**Solución:**
```bash
# En Linux/Mac
sudo apt-get install libpq-dev python3-dev
pip install psycopg2-binary

# En Windows
pip install psycopg2-binary
```

### Problema 2: Error de conexión a PostgreSQL

**Solución:**
```bash
# Verificar que PostgreSQL está corriendo
sudo systemctl status postgresql  # Linux
# o
pg_ctl -D /usr/local/var/postgres status  # Mac

# Verificar credenciales en .env
# Asegurar que el usuario y contraseña son correctos
```

### Problema 3: Angular no encuentra @angular/core

**Solución:**
```bash
cd frontend/angular
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
npm install @angular/core@17.3.0
```

### Problema 4: Error CORS en el navegador

**Solución:**
```bash
# Verificar que en backend/.env tienes:
CORS_ORIGINS=["http://localhost:4200","http://localhost:8501"]

# Reiniciar el backend
```

### Problema 5: Redis no conecta

**Solución:**
```bash
# Instalar Redis en Windows (usando WSL2)
wsl --install
# Luego dentro de WSL:
sudo apt-get update
sudo apt-get install redis-server

# En Mac:
brew install redis
brew services start redis

# Verificar conexión
redis-cli ping  # Debería responder PONG
```

### Problema 6: Error de puertos en uso

**Solución:**
```bash
# Ver qué está usando el puerto 8000 (backend)
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Matar el proceso (Linux/Mac)
kill -9 <PID>

# Cambiar puerto en uvicorn
uvicorn main:app --reload --port 8001
```

### Problema 7: Seeders no ejecutan correctamente

**Solución:**
```bash
# Verificar que PostgreSQL está corriendo
# Ejecutar seeders manualmente
cd scripts
python seed_data.py

# Si hay error de conexión, modificar la URL en seed_data.py
DATABASE_URL = "postgresql://tu_usuario:tu_contraseña@localhost:5432/cartdb"
```

---

## 👥 Credenciales de Prueba

Después de ejecutar el seeder, puedes usar estas cuentas:

### Administrador
```yaml
Email: admin@example.com
Contraseña: admin123
```

### Clientes de Prueba
```yaml
Cliente 1:
  Email: cliente1@example.com
  Contraseña: cliente123

Cliente 2:
  Email: cliente2@example.com
  Contraseña: cliente123

Cliente 3:
  Email: cliente3@example.com
  Contraseña: cliente123
```

---

## 📡 Endpoints de la API

### Documentación Automática (Swagger)
```bash
http://localhost:8000/docs
```

### Endpoints Principales

#### Autenticación
```http
POST   /api/auth/register     # Registrar usuario
POST   /api/auth/login        # Iniciar sesión
```

#### Productos
```http
GET    /api/products          # Listar productos
GET    /api/products/{id}     # Obtener producto
POST   /api/products          # Crear producto (admin)
PUT    /api/products/{id}     # Actualizar producto (admin)
DELETE /api/products/{id}     # Eliminar producto (admin)
```

#### Carrito
```http
GET    /api/cart              # Ver carrito
POST   /api/cart/items        # Agregar producto
PUT    /api/cart/items/{id}   # Actualizar cantidad
DELETE /api/cart/items/{id}   # Eliminar producto
```

#### Pedidos
```http
POST   /api/orders            # Crear pedido
GET    /api/orders            # Mis pedidos
GET    /api/orders/admin/all  # Todos los pedidos (admin)
```

#### Estadísticas (admin)
```http
GET    /api/statistics/sales/daily        # Ventas diarias
GET    /api/statistics/sales/timeline     # Evolución ventas
GET    /api/statistics/top-products       # Productos más vendidos
GET    /api/statistics/customer/avg-purchase  # Promedio por cliente
```

#### Reportes (admin)
```http
POST   /api/reports/orders-pdf     # Reporte de pedidos
POST   /api/reports/executive-pdf  # Reporte ejecutivo
```

---

## 📁 Estructura del Proyecto

```
shopping-cart-system/
│
├── backend/                    # Backend FastAPI
│   ├── auth/                   # Autenticación JWT
│   ├── routers/                # Endpoints API
│   ├── models/                 # Modelos Pydantic
│   ├── services/               # Servicios (PDF, Email, Cache)
│   ├── database/               # Conexión DB
│   ├── main.py                 # Punto de entrada
│   └── requirements.txt
│
├── frontend/
│   ├── angular/                # Frontend Angular
│   │   ├── src/app/
│   │   │   ├── auth/          # Login/Registro
│   │   │   ├── products/      # Gestión productos
│   │   │   ├── cart/          # Carrito compras
│   │   │   ├── orders/        # Pedidos
│   │   │   ├── admin/         # Panel admin
│   │   │   ├── services/      # Servicios HTTP
│   │   │   ├── models/        # Interfaces
│   │   │   └── guards/        # Protección rutas
│   │   ├── package.json
│   │   └── angular.json
│   │
│   └── streamlit/              # Dashboard Streamlit
│       ├── pages/              # Múltiples páginas
│       ├── utils/              # Utilidades
│       └── streamlit_app.py
│
├── scripts/                    # Scripts utilitarios
│   ├── seed_data.py           # Poblar base de datos
│   └── backup_db.sh           # Backup automático
│
├── docker-compose.yml         # Orquestación Docker
└── README.md                  # Esta documentación
```

---

## 🚢 Despliegue en Producción

### Opción 1: Despliegue con Docker (Recomendado)

```bash
# 1. Construir imágenes
docker-compose build

# 2. Ejecutar en background
docker-compose up -d

# 3. Verificar estado
docker-compose ps

# 4. Ver logs
docker-compose logs -f backend

# 5. Escalar servicios (si es necesario)
docker-compose up -d --scale backend=3
```

### Opción 2: Despliegue Manual en Servidor Linux

#### Backend (FastAPI)
```bash
# Usar Gunicorn + Uvicorn para producción
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000

# O con systemd (crear servicio)
sudo nano /etc/systemd/system/cart-backend.service
```

#### Frontend Angular
```bash
# Build de producción
cd frontend/angular
npm run build --prod

# Los archivos están en dist/ - servir con Nginx
sudo cp -r dist/shopping-cart-angular/* /var/www/html/
```

#### Dashboard Streamlit
```bash
# Ejecutar con configuración de producción
streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
```

### Configuración de Nginx (Proxy Reverso)

```nginx
server {
    listen 80;
    server_name tudominio.com;
    
    # Angular
    location / {
        root /var/www/html;
        try_files $uri $uri/ /index.html;
    }
    
    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # Streamlit Dashboard
    location /dashboard {
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🔒 Recomendaciones de Seguridad

### Para Entornos de Producción

1. **Cambiar secret keys:**
   ```bash
   # Generar nueva clave secreta
   openssl rand -hex 32
   ```

2. **Usar HTTPS:**
   ```bash
   # Con Let's Encrypt
   sudo certbot --nginx -d tudominio.com
   ```

3. **Configurar firewall:**
   ```bash
   # Solo permitir puertos necesarios
   sudo ufw allow 22/tcp
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

4. **Variables de entorno seguras:**
   ```bash
   # No committear .env al repositorio
   echo ".env" >> .gitignore
   
   # Usar variables de sistema en producción
   export DATABASE_URL="postgresql://..."
   ```

5. **Rate limiting en FastAPI:**
   ```python
   # Instalar slowapi
   pip install slowapi
   ```

---

## 📊 Monitoreo y Mantenimiento

### Logs importantes
```bash
# Backend logs
tail -f backend/logs/app.log

# PostgreSQL logs
tail -f /var/log/postgresql/postgresql.log

# Redis logs
redis-cli MONITOR
```

### Backups automáticos
```bash
# Configurar cron para backups diarios
crontab -e
# Añadir:
0 2 * * * /ruta/al/proyecto/scripts/backup_db.sh
```

### Limpieza de caché Redis
```bash
# Limpiar todas las claves
redis-cli FLUSHALL

# Limpiar solo claves de carritos
redis-cli --scan --pattern "cart:*" | xargs redis-cli DEL
```

---

## 🆘 Soporte y Ayuda

### Enlaces útiles
- [Documentación FastAPI](https://fastapi.tiangolo.com/)
- [Documentación Angular](https://angular.io/docs)
- [Documentación Streamlit](https://docs.streamlit.io/)
- [Documentación PostgreSQL](https://www.postgresql.org/docs/)

### Comandos de diagnóstico rápido

```bash
# Verificar todos los servicios
curl http://localhost:8000/docs           # Backend
curl http://localhost:4200                # Angular
curl http://localhost:8501                # Streamlit
redis-cli ping                            # Redis
psql -d cartdb -c "SELECT 1"             # PostgreSQL

# Verificar conexiones
netstat -tulpn | grep -E ':(8000|4200|8501|5432|6379)'

# Reinicio completo
docker-compose down && docker-compose up -d
```

---

## 📝 Checklist de Verificación

Antes de reportar un problema, verifica:

- [ ] Redis está corriendo (`redis-cli ping`)
- [ ] PostgreSQL está activo (`sudo systemctl status postgresql`)
- [ ] Backend tiene el archivo `.env` configurado
- [ ] Las dependencias están instaladas (`npm list` y `pip list`)
- [ ] Los seeders se ejecutaron correctamente
- [ ] Los puertos están libres (8000, 4200, 8501, 5432, 6379)
- [ ] El token JWT no ha expirado
- [ ] El navegador no tiene caché (Ctrl+F5)

---

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver archivo `LICENSE` para más detalles.

---

## 👨‍💻 Contacto y Contribuciones

- **Issues**: [GitHub Issues](https://github.com/tu-usuario/shopping-cart-system/issues)
- **Email**: soporte@tudominio.com

---

**¡Gracias por usar este sistema! 🎉**