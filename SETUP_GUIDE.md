# 🚀 Instrucciones para Ejecutar el Sistema Completo

## 1️⃣ Iniciar Backend (Puerto 8000)

### En PowerShell - Terminal 1:
```powershell
cd backend
.\venv\Scripts\Activate.ps1
```

### Crear variables de entorno:
```powershell
$env:DATABASE_URL="postgresql://postgres:tucontraseña@localhost:5432/cartdb"
```

### Ejecutar el servidor:
```powershell
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

✅ Debería mostrar:
```
Uvicorn running on http://127.0.0.1:8000
Press CTRL+C to quit
```

---

## 2️⃣ Cargar Datos de Prueba

### En PowerShell - Terminal 2:
```powershell
cd backend
$env:DATABASE_URL="postgresql://postgres:tucontraseña@localhost:5432/cartdb"
python ..\scripts\seed_data.py
```

✅ Debería crear:
- 6 categorías
- 12 productos
- 5 usuarios
- Múltiples pedidos de ejemplo

---

## 3️⃣ Iniciar Frontend (Puerto 4200)

### En PowerShell - Terminal 3:
```powershell
cd frontend/angular
npm install  # Si no instalaste las dependencias
npm start
```

✅ Debería abrir automáticamente en:
```
http://localhost:4200
```

---

## 📋 URLs Útiles

| URL | Descripción |
|-----|------------|
| `http://localhost:4200` | Frontend - Dashboard de productos |
| `http://127.0.0.1:8000` | Backend - API |
| `http://127.0.0.1:8000/docs` | Swagger - Documentación API |
| `http://127.0.0.1:8000/api/images/` | Imágenes locales |

---

## 🔐 Credenciales de Prueba

```
Admin:
  Email: admin@example.com
  Password: admin123

Cliente 1:
  Email: cliente1@example.com
  Password: cliente123

Cliente 2:
  Email: cliente2@example.com
  Password: cliente123
```

---

## 🎨 Dashboard - Características

✨ **Diseño Moderno**: Interfaz responsiva con Tailwind CSS
🔍 **Búsqueda**: Busca productos por nombre o descripción en tiempo real
📁 **Categorías**: Filtra por categoría (Electrónicos, Ropa, Hogar, etc.)
📊 **Ordenamiento**: Ordena por Nombre, Precio o Stock
🎴 **Tarjetas**: Muestra productos en tarjetas atractivas
📦 **Stock**: Indicadores visuales de disponibilidad
🛒 **Carrito**: Botones para añadir al carrito directamente
⚡ **Animaciones**: Transiciones suaves en hover

---

## 🖼️ Imágenes de Productos

Las imágenes se encuentran en:
```
backend/static/images/
├── iphone.jpg
├── macbook.jpg
├── tshirt.jpg
├── jeans.jpg
├── pan.jpg
├── sheets.jpg
├── ball.jpg
├── racket.jpg
├── book.jpg
├── lego.jpg
├── tablet.jpg
└── headphones.jpg
```

Se sirven automáticamente a través de:
```
http://127.0.0.1:8000/api/images/nombre.jpg
```

---

## ❌ Solución de Problemas

### "No se puede conectar al backend"
- Verifica que el backend esté corriendo en el puerto 8000
- Revisa la variable `DATABASE_URL`
- Confirma que PostgreSQL está activo

### "No aparecen las imágenes"
- Verifica que existan en `backend/static/images/`
- Revisa que el backend esté corriendo
- Abre en navegador: `http://127.0.0.1:8000/api/images/iphone.jpg`

### "Error al ejecutar el seed"
- Confirma que `DATABASE_URL` está correcta
- Verifica que la base de datos `cartdb` existe
- Ejecuta: `python scripts\seed_data.py` (desde la raíz del proyecto)

### "Angular no compila"
- Ejecuta: `npm install` en `frontend/angular`
- Limpia: `npm cache clean --force`
- Intenta: `npm start` nuevamente

---

## 📝 Cambios Principales Realizados

### Backend
- ✅ Configurado servidor de archivos estáticos para imágenes
- ✅ Creada carpeta `backend/static/images/` con 12 imágenes placeholder
- ✅ Actualizado `seed_data.py` para usar rutas locales (`/api/images/...`)
- ✅ Añadido `StaticFiles` en `main.py`

### Frontend
- ✅ Instalado Tailwind CSS
- ✅ Configurado `tailwind.config.js` y `postcss.config.js`
- ✅ Creado componente `DashboardComponent` 
- ✅ Diseñado con Tailwind CSS (responsivo, moderno, animado)
- ✅ Añadida ruta `/dashboard` como página de inicio
- ✅ Integración con servicios existentes (ProductsService, CartService)

---

## 🎯 Validación

Después de ejecutar todo, verifica:

1. ✅ Backend responde: `http://127.0.0.1:8000/health`
2. ✅ API Swagger: `http://127.0.0.1:8000/docs`
3. ✅ Dashboard carga: `http://localhost:4200`
4. ✅ Imágenes se muestran en tarjetas
5. ✅ Búsqueda filtra productos
6. ✅ Botones de categoría funcionan
7. ✅ "Añadir al Carrito" trabaja (requiere login)

---

¡Listo! 🎉 Tu sistema de carrito de compras con imágenes locales y dashboard moderno está funcionando.
