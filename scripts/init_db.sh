#!/bin/bash
echo "Inicializando base de datos..."
docker-compose exec -T postgres psql -U cartuser -d cartdb < backend/init_db.sql
echo "Base de datos inicializada correctamente"