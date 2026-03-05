#!/usr/bin/env bash
# ==========================================
# Cirujano de Sintetizadores - Database Backup
# ==========================================
# Crea backup de PostgreSQL y lo comprime.
# Uso: bash scripts/backup-db.sh
#
# Los backups se guardan en ./backups/ con timestamp.
# Mantiene los últimos 30 backups automáticamente.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "${SCRIPT_DIR}")"
cd "${PROJECT_DIR}"

# Configuración
BACKUP_DIR="${PROJECT_DIR}/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
KEEP_DAYS=30

# Leer variables de entorno
if [ -f .env ]; then
    # shellcheck disable=SC1091
    source .env 2>/dev/null || true
fi

DB_USER="${POSTGRES_USER:-cirujano}"
DB_NAME="${POSTGRES_DB:-cirujano_db}"
DB_CONTAINER="${DB_CONTAINER:-cirujano_db}"

BACKUP_FILE="${BACKUP_DIR}/${DB_NAME}_${TIMESTAMP}.sql.gz"

echo "🗄️  Cirujano de Sintetizadores - Database Backup"
echo "================================================="
echo "   Base de datos: ${DB_NAME}"
echo "   Usuario:       ${DB_USER}"
echo "   Contenedor:    ${DB_CONTAINER}"
echo "   Destino:       ${BACKUP_FILE}"

# Crear directorio de backups
mkdir -p "${BACKUP_DIR}"

# =====================
# Crear backup
# =====================
echo ""
echo "📦 Creando backup..."

if docker ps --format '{{.Names}}' | grep -q "${DB_CONTAINER}"; then
    # PostgreSQL corriendo en Docker
    docker exec "${DB_CONTAINER}" pg_dump \
        -U "${DB_USER}" \
        -d "${DB_NAME}" \
        --no-owner \
        --no-privileges \
        --clean \
        --if-exists \
        | gzip > "${BACKUP_FILE}"
elif command -v pg_dump &> /dev/null; then
    # PostgreSQL local
    pg_dump \
        -U "${DB_USER}" \
        -d "${DB_NAME}" \
        --no-owner \
        --no-privileges \
        --clean \
        --if-exists \
        | gzip > "${BACKUP_FILE}"
elif [ -f "backend/cirujano.db" ]; then
    # SQLite fallback
    BACKUP_FILE="${BACKUP_DIR}/${DB_NAME}_${TIMESTAMP}_sqlite.gz"
    gzip -c "backend/cirujano.db" > "${BACKUP_FILE}"
    echo "   (Backup de SQLite)"
else
    echo "❌ No se encontró base de datos para respaldar."
    exit 1
fi

# Verificar backup
BACKUP_SIZE=$(du -h "${BACKUP_FILE}" | cut -f1)
echo "✅ Backup creado: ${BACKUP_FILE} (${BACKUP_SIZE})"

# =====================
# Limpiar backups antiguos
# =====================
echo ""
echo "🧹 Limpiando backups con más de ${KEEP_DAYS} días..."
DELETED=$(find "${BACKUP_DIR}" -name "*.sql.gz" -mtime +${KEEP_DAYS} -delete -print | wc -l)
echo "   Eliminados: ${DELETED} archivo(s) antiguo(s)"

# =====================
# Listar backups existentes
# =====================
echo ""
echo "📋 Backups disponibles:"
ls -lh "${BACKUP_DIR}"/*.gz 2>/dev/null | tail -10 || echo "   (ninguno)"

echo ""
echo "🔄 Para restaurar:"
echo "   gunzip < ${BACKUP_FILE} | docker exec -i ${DB_CONTAINER} psql -U ${DB_USER} -d ${DB_NAME}"
