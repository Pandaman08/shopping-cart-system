#!/usr/bin/env python3
"""
Script para generar imágenes placeholder para los productos
Requiere: pip install Pillow
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import os

# Crear directorio de imágenes si no existe
IMAGES_DIR = Path(__file__).parent / "static" / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# Datos de productos con colores específicos
PRODUCTS = {
    "iphone.jpg": {"name": "iPhone 15 Pro", "color": "#000000", "icon": "📱"},
    "macbook.jpg": {"name": "MacBook Pro", "color": "#A2AAAD", "icon": "💻"},
    "tshirt.jpg": {"name": "Camiseta Deportiva", "color": "#FF6B6B", "icon": "👕"},
    "jeans.jpg": {"name": "Jeans", "color": "#1F3A93", "icon": "👖"},
    "pan.jpg": {"name": "Sartén Antiadherente", "color": "#8B4513", "icon": "🍳"},
    "sheets.jpg": {"name": "Juego de Sábanas", "color": "#E8E8E8", "icon": "🛏️"},
    "ball.jpg": {"name": "Balón de Fútbol", "color": "#FFFFFF", "icon": "⚽"},
    "racket.jpg": {"name": "Raqueta de Tenis", "color": "#FFD700", "icon": "🎾"},
    "book.jpg": {"name": "Libro Python", "color": "#3776AB", "icon": "📚"},
    "lego.jpg": {"name": "Lego Star Wars", "color": "#FFBB00", "icon": "🧩"},
    "tablet.jpg": {"name": "Tablet Samsung", "color": "#1428A0", "icon": "📱"},
    "headphones.jpg": {"name": "Auriculares Sony", "color": "#000000", "icon": "🎧"},
}

def create_placeholder_image(filename: str, product_name: str, color: str, emoji: str):
    """Crear una imagen placeholder con gradiente y emoji"""
    width, height = 400, 400
    
    # Crear imagen
    img = Image.new('RGB', (width, height), color=color)
    draw = ImageDraw.Draw(img)
    
    # Dibujar fondo con gradiente simulado (rectángulos superpuestos)
    for i in range(height):
        ratio = i / height
        # Hacer el color más oscuro hacia abajo
        factor = 1 - (ratio * 0.3)
        r = int(int(color[1:3], 16) * factor)
        g = int(int(color[3:5], 16) * factor)
        b = int(int(color[5:7], 16) * factor)
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        draw.line([(0, i), (width, i)], fill=hex_color)
    
    # Dibujar emoji en el centro
    bbox = draw.textbbox((0, 0), emoji)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Ajustar tamaño del emoji usando fuentes más grandes
    try:
        # Intentar con fuente más grande
        font = ImageFont.load_default()
        draw.text(
            ((width - text_width) // 2, (height - text_height) // 2 - 50),
            emoji,
            fill="white",
            font=font
        )
    except:
        pass
    
    # Escribir el nombre del producto
    text = product_name
    bbox = draw.textbbox((0, 0), text)
    text_width = bbox[2] - bbox[0]
    
    # Determinar color de texto basado en luminancia del fondo
    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    text_color = "white" if luminance < 0.5 else "black"
    
    draw.text(
        ((width - text_width) // 2, height - 80),
        text,
        fill=text_color,
        font=font
    )
    
    # Guardar imagen
    filepath = IMAGES_DIR / filename
    img.save(filepath)
    print(f"✓ Creada: {filename}")

# Crear todas las imágenes
print("🎨 Generando imágenes placeholder...")
for filename, info in PRODUCTS.items():
    create_placeholder_image(
        filename,
        info["name"],
        info["color"],
        info["icon"]
    )

print(f"\n✅ {len(PRODUCTS)} imágenes creadas en: {IMAGES_DIR}")
