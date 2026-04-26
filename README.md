# Shopping Cart System

Guia rapida para ejecutar la aplicacion completa en local (backend + frontend + datos de prueba).

## Stack
- Backend: FastAPI (Python)
- Frontend: Angular 17
- Base de datos: PostgreSQL
- Redis: opcional (si no esta instalado, el backend usa cache en memoria)

## Requisitos
- Node.js 20 LTS (recomendado para Angular 17)
- Python 3.11+ (se recomienda una version estable, no beta)
- PostgreSQL 15+

Comprobar versiones:

```powershell
node --version
npm --version
python --version
psql --version
```

## 1) Preparar base de datos
Crear la base `cartdb` en PostgreSQL y asegurar credenciales:

- Usuario: `postgres`
- Password: `tucontraseña`
- Host: `localhost`
- Puerto: `5432`

Si usas otras credenciales, ajusta:
- `backend/.env`
- variable de entorno `DATABASE_URL` antes de ejecutar el seed

## 2) Backend
Desde la raiz del proyecto:

```powershell
Set-Location "backend"
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Crear/editar `backend/.env` con:

```env
DATABASE_URL=postgresql://postgres:tucontraseña@localhost:5432/cartdb
REDIS_URL=redis://localhost:6379
SECRET_KEY=tucontraseña
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
CORS_ORIGINS=["http://localhost:4200","http://localhost:8501"]
```

Levantar backend:

```powershell
Set-Location "backend"
.\venv\Scripts\python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Chequeo rapido:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

## 3) Cargar datos de prueba (seed)
En otra terminal, desde la raiz:

```powershell
$env:DATABASE_URL="postgresql://postgres:tucontraseña@localhost:5432/cartdb"
python scripts\seed_data.py
```

Esto crea categorias, productos, usuarios y pedidos.

## 4) Frontend Angular
En otra terminal:

```powershell
Set-Location "frontend/angular"
npm install
npx ng serve --port 4200
```

Abrir en navegador:
- http://localhost:4200

## Credenciales de prueba
- Admin: `admin@example.com` / `admin123`
- Cliente: `cliente1@example.com` / `cliente123`
- Cliente: `cliente2@example.com` / `cliente123`

## URLs utiles
- Frontend: http://localhost:4200
- Backend API: http://127.0.0.1:8000
- Swagger: http://127.0.0.1:8000/docs

## Problemas comunes
### No puedo loguear
- Verifica que el backend este corriendo.
- Reejecuta el seed: `python scripts\\seed_data.py`.
- Confirma credenciales de prueba.

### Frontend compila pero tarda en mostrar productos
- La API responde rapido; la demora suele ser por imagenes remotas.
- El listado ya usa carga diferida (`lazy`) y fallback de imagen.

### Error de CORS
- Revisa `CORS_ORIGINS` en `backend/.env`.
- Reinicia backend despues de cambiar `.env`.

## Notas importantes
- `docker-compose.yml` actualmente no esta configurado para levantar todo el sistema automaticamente.
- Redis no es obligatorio en local para probar la app.

## Estructura base

```text
backend/            FastAPI
frontend/angular/   Angular
frontend/streamlit/ Dashboard opcional
scripts/            Seed y utilidades
```
