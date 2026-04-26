#!/bin/bash

# Script para backup de base de datos
DB_NAME="cartdb"
BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_backup_$TIMESTAMP.sql"

# Crear directorio si no existe
mkdir -p $BACKUP_DIR

echo "📦 Creando backup de $DB_NAME..."
pg_dump -U postgres $DB_NAME > $BACKUP_FILE

if [ $? -eq 0 ]; then
    echo "✅ Backup creado: $BACKUP_FILE"
    # Comprimir
    gzip $BACKUP_FILE
    echo "✅ Backup comprimido: ${BACKUP_FILE}.gz"
else
    echo "❌ Error al crear backup"
fi