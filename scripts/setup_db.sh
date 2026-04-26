#!/bin/bash

# Script para crear y poblar la base de datos
echo "Configurando base de datos..."

# Colores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Configuración
DB_NAME="cartdb"
DB_USER="postgres"  # Cambiar según tu configuración

# Crear base de datos
echo "Creando base de datos $DB_NAME..."
createdb -U $DB_USER $DB_NAME 2>/dev/null

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Base de datos creada${NC}"
else
    echo -e "${RED}La base de datos ya existe o hubo un error${NC}"
fi

# Ejecutar seeders con Python
echo "Ejecutando seeders..."
python3 scripts/seed_data.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Datos de prueba insertados correctamente${NC}"
else
    echo -e "${RED}Error al insertar datos${NC}"
fi

echo "✅ Configuración completada"