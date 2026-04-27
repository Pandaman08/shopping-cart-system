#!/usr/bin/env python3
import asyncio
import asyncpg
import random
from datetime import datetime, timedelta
import os
import bcrypt as _bcrypt

def get_password_hash(password: str) -> str:
    return _bcrypt.hashpw(password.encode("utf-8"), _bcrypt.gensalt()).decode("utf-8")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:CHANGE_ME@localhost:5432/cartdb")

async def seed_database():
    """Insertar datos de prueba en la base de datos"""
    
    conn = await asyncpg.connect(DATABASE_URL)
    
    try:
        # Limpiar datos existentes (opcional)
        await conn.execute("TRUNCATE TABLE order_items, orders, cart_items, carts, products, categories, users CASCADE")
        
        print("🌱 Sembrando datos de prueba...")
        
        # 1. Crear categorías
        categories = [
            ("Electrónicos", "Productos electrónicos y tecnología"),
            ("Ropa", "Prendas de vestir y accesorios"),
            ("Hogar", "Artículos para el hogar"),
            ("Deportes", "Equipo deportivo"),
            ("Libros", "Libros y publicaciones"),
            ("Juguetes", "Juguetes y juegos")
        ]
        
        category_ids = []
        for name, desc in categories:
            cat_id = await conn.fetchval(
                "INSERT INTO categories (name, description) VALUES ($1, $2) RETURNING id",
                name, desc
            )
            category_ids.append(cat_id)
        
        print(f"  ✓ {len(categories)} categorías creadas")
        
        # 2. Crear productos
        products_data = [
            ("iPhone 15 Pro", "Teléfono de última generación", 999.99, 50, 0, "/api/images/iphone.jpg"),
            ("MacBook Pro", "Laptop profesional", 1999.99, 30, 0, "/api/images/macbook.jpg"),
            ("Camiseta Deportiva", "Camiseta de algodón", 29.99, 200, 1, "/api/images/tshirt.jpg"),
            ("Jeans", "Pantalón vaquero", 59.99, 150, 1, "/api/images/jeans.jpg"),
            ("Sartén Antiadherente", "Sartén de 28cm", 39.99, 100, 2, "/api/images/pan.jpg"),
            ("Juego de Sábanas", "Sábanas 100% algodón", 49.99, 80, 2, "/api/images/sheets.jpg"),
            ("Balón de Fútbol", "Balón oficial", 29.99, 120, 3, "/api/images/ball.jpg"),
            ("Raqueta de Tenis", "Raqueta profesional", 89.99, 60, 3, "/api/images/racket.jpg"),
            ("Libro Python", "Aprende Python desde cero", 49.99, 90, 4, "/api/images/book.jpg"),
            ("Lego Star Wars", "Set de construcción", 79.99, 70, 5, "/api/images/lego.jpg"),
            ("Tablet Samsung", "Tablet 10 pulgadas", 299.99, 45, 0, "/api/images/tablet.jpg"),
            ("Auriculares Sony", "Auriculares Bluetooth", 149.99, 110, 0, "/api/images/headphones.jpg"),
        ]
        
        product_ids = []
        for name, desc, price, stock, cat_idx, img in products_data:
            product_id = await conn.fetchval(
                """
                INSERT INTO products (name, description, price, stock, category_id, image_url)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING id
                """,
                name, desc, price, stock, category_ids[cat_idx], img
            )
            product_ids.append(product_id)
        
        print(f"  ✓ {len(products_data)} productos creados")
        
        # 3. Crear usuarios
        users_data = [
            ("admin@example.com", get_password_hash("admin123"), "Admin User", "admin"),
            ("cliente1@example.com", get_password_hash("cliente123"), "Juan Pérez", "cliente"),
            ("cliente2@example.com", get_password_hash("cliente123"), "María García", "cliente"),
            ("cliente3@example.com", get_password_hash("cliente123"), "Carlos López", "cliente"),
            ("cliente4@example.com", get_password_hash("cliente123"), "Ana Martínez", "cliente"),
        ]
        
        user_ids = []
        for email, pwd_hash, name, role in users_data:
            user_id = await conn.fetchval(
                """
                INSERT INTO users (email, password_hash, full_name, role)
                VALUES ($1, $2, $3, $4)
                RETURNING id
                """,
                email, pwd_hash, name, role
            )
            user_ids.append(user_id)
        
        print(f"  ✓ {len(users_data)} usuarios creados")
        
        # 4. Crear pedidos de ejemplo (últimos 30 días)
        order_statuses = ['paid', 'paid', 'paid', 'delivered', 'shipped']  # Más probabilidad de paid
        payment_methods = ['credit_card', 'debit_card', 'paypal', 'transfer']
        
        orders_count = 0
        for user_id in user_ids[1:]:  # Excepto admin
            # Crear entre 2 y 8 pedidos por usuario
            num_orders = random.randint(2, 8)
            
            for i in range(num_orders):
                # Fecha aleatoria en los últimos 30 días
                days_ago = random.randint(0, 30)
                order_date = datetime.now() - timedelta(days=days_ago)
                
                # Crear carrito temporal
                cart_id = await conn.fetchval(
                    """
                    INSERT INTO carts (user_id, status, created_at)
                    VALUES ($1, 'completed', $2)
                    RETURNING id
                    """,
                    user_id, order_date
                )
                
                # Seleccionar 1-5 productos aleatorios
                num_items = random.randint(1, 5)
                selected_products = random.sample(product_ids, num_items)
                total_amount = 0
                
                for product_id in selected_products:
                    quantity = random.randint(1, 3)
                    
                    # Obtener precio del producto
                    product = await conn.fetchrow(
                        "SELECT name, price FROM products WHERE id = $1",
                        product_id
                    )
                    
                    subtotal = product['price'] * quantity
                    total_amount += subtotal
                    
                    # Agregar al carrito
                    await conn.execute(
                        """
                        INSERT INTO cart_items (cart_id, product_id, quantity, unit_price)
                        VALUES ($1, $2, $3, $4)
                        """,
                        cart_id, product_id, quantity, product['price']
                    )
                
                # Crear pedido
                status = random.choice(order_statuses)
                payment_method = random.choice(payment_methods)
                
                order_id = await conn.fetchval(
                    """
                    INSERT INTO orders (user_id, cart_id, total_amount, status, 
                                      payment_method, shipping_address, created_at, paid_at)
                    VALUES ($1, $2, $3, $4::varchar, $5, $6, $7::timestamp, 
                            CASE WHEN $4::varchar IN ('paid', 'delivered', 'shipped') THEN $7::timestamp ELSE NULL END)
                    RETURNING id
                    """,
                    user_id, cart_id, total_amount, status, payment_method,
                    f"Calle {random.randint(1, 999)}, Ciudad", order_date
                )
                
                # Crear items del pedido
                cart_items = await conn.fetch(
                    "SELECT * FROM cart_items WHERE cart_id = $1",
                    cart_id
                )
                
                for item in cart_items:
                    product = await conn.fetchrow(
                        "SELECT name FROM products WHERE id = $1",
                        item['product_id']
                    )
                    
                    await conn.execute(
                        """
                        INSERT INTO order_items (order_id, product_id, product_name, 
                                               quantity, unit_price)
                        VALUES ($1, $2, $3, $4, $5)
                        """,
                        order_id, item['product_id'], product['name'],
                        item['quantity'], item['unit_price']
                    )
                    
                    # Actualizar stock (solo si está pagado)
                    if status in ['paid', 'delivered', 'shipped']:
                        await conn.execute(
                            "UPDATE products SET stock = stock - $1 WHERE id = $2",
                            item['quantity'], item['product_id']
                        )
                
                orders_count += 1
        
        print(f"  ✓ {orders_count} pedidos creados")
        
        # 5. Actualizar estadísticas de usuarios
        for user_id in user_ids:
            await conn.execute(
                """
                UPDATE users 
                SET last_login = NOW() - (random() * INTERVAL '30 days')::INTERVAL
                WHERE id = $1
                """,
                user_id
            )
        
        print("\n✅ Seed completado exitosamente!")
        print(f"\nResumen:")
        print(f"  - Categorías: {len(categories)}")
        print(f"  - Productos: {len(products_data)}")
        print(f"  - Usuarios: {len(users_data)}")
        print(f"  - Pedidos: {orders_count}")
        
        # Mostrar credenciales de prueba
        print("\n🔐 Credenciales de prueba:")
        print("  Admin: admin@example.com / admin123")
        print("  Cliente: cliente1@example.com / cliente123")
        print("  Cliente: cliente2@example.com / cliente123")
        
    except Exception as e:
        print(f"❌ Error durante el seeding: {e}")
        raise
    finally:
        await conn.close()

if __name__ == "__main__":
    print("🚀 Iniciando seeding de base de datos...")
    asyncio.run(seed_database())