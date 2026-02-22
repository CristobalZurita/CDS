#!/usr/bin/env bash
# ==========================================
# Cirujano de Sintetizadores - Deploy Script
# ==========================================
# Despliega la aplicación completa en producción con Docker Compose.
# Uso: bash scripts/deploy.sh [--build] [--migrate]
#
# Flags:
#   --build    Reconstruir imágenes Docker
#   --migrate  Ejecutar migraciones Alembic antes de levantar

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "${SCRIPT_DIR}")"
cd "${PROJECT_DIR}"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

DO_BUILD=false
DO_MIGRATE=false

for arg in "$@"; do
    case "${arg}" in
        --build) DO_BUILD=true ;;
        --migrate) DO_MIGRATE=true ;;
        *) echo -e "${RED}Flag desconocido: ${arg}${NC}"; exit 1 ;;
    esac
done

echo -e "${GREEN}🚀 Cirujano de Sintetizadores - Deploy${NC}"
echo "========================================="

# =====================
# 1. Verificar prerequisitos
# =====================
echo -e "\n${YELLOW}[1/6] Verificando prerequisitos...${NC}"

if [ ! -f .env ]; then
    echo -e "${RED}❌ Archivo .env no encontrado.${NC}"
    echo "   Copia .env.production.example a .env y completa los valores."
    echo "   cp .env.production.example .env"
    exit 1
fi

if [ ! -f certs/fullchain.pem ] || [ ! -f certs/privkey.pem ]; then
    echo -e "${YELLOW}⚠️  Certificados SSL no encontrados en certs/.${NC}"
    echo "   Ejecuta: bash scripts/setup-ssl.sh"
    echo "   Continuando sin SSL (solo HTTP)..."
fi

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker no instalado.${NC}"
    exit 1
fi

if ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose no disponible.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisitos OK${NC}"

# =====================
# 2. Pull latest code (si es git)
# =====================
echo -e "\n${YELLOW}[2/6] Verificando código...${NC}"

if [ -d .git ]; then
    CURRENT_BRANCH=$(git branch --show-current)
    echo "   Rama actual: ${CURRENT_BRANCH}"
    echo "   Último commit: $(git log --oneline -1)"
fi

# =====================
# 3. Build (si se solicitó)
# =====================
if [ "${DO_BUILD}" = true ]; then
    echo -e "\n${YELLOW}[3/6] Construyendo imágenes Docker...${NC}"
    docker compose build --no-cache
    echo -e "${GREEN}✅ Imágenes construidas${NC}"
else
    echo -e "\n${YELLOW}[3/6] Build omitido (usar --build para reconstruir)${NC}"
fi

# =====================
# 4. Detener servicios existentes
# =====================
echo -e "\n${YELLOW}[4/6] Deteniendo servicios existentes...${NC}"
docker compose down --remove-orphans 2>/dev/null || true
echo -e "${GREEN}✅ Servicios detenidos${NC}"

# =====================
# 5. Migraciones (si se solicitó)
# =====================
if [ "${DO_MIGRATE}" = true ]; then
    echo -e "\n${YELLOW}[5/6] Ejecutando migraciones...${NC}"
    # Levantar solo PostgreSQL primero
    docker compose up -d postgres
    echo "   Esperando a que PostgreSQL esté listo..."
    sleep 10

    # Ejecutar migraciones
    docker compose run --rm backend alembic upgrade head
    echo -e "${GREEN}✅ Migraciones ejecutadas${NC}"
else
    echo -e "\n${YELLOW}[5/6] Migraciones omitidas (usar --migrate para ejecutar)${NC}"
fi

# =====================
# 6. Levantar todos los servicios
# =====================
echo -e "\n${YELLOW}[6/6] Levantando servicios...${NC}"
docker compose up -d
echo ""

# Esperar a que los servicios estén listos
echo "   Esperando a que los servicios inicien..."
sleep 15

# =====================
# Verificación
# =====================
echo -e "\n${GREEN}=========================================${NC}"
echo -e "${GREEN}🎉 Deploy completado${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""

# Verificar health checks
echo "📊 Estado de servicios:"
docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || docker compose ps

echo ""
echo "🔍 Health checks:"

# Backend
BACKEND_HEALTH=$(curl -sf http://localhost:8000/api/health 2>/dev/null || echo '{"status":"unreachable"}')
echo "   Backend:  ${BACKEND_HEALTH}"

# Frontend
FRONTEND_STATUS=$(curl -sf -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null || echo "unreachable")
echo "   Frontend: HTTP ${FRONTEND_STATUS}"

echo ""
echo "📋 Comandos útiles:"
echo "   Logs:     docker compose logs -f"
echo "   Estado:   docker compose ps"
echo "   Detener:  docker compose down"
echo "   Backup:   bash scripts/backup-db.sh"
