#!/bin/bash
# ============================================
# CDS - Security Pre-Flight Check
# ============================================
# Script de verificación de seguridad antes de deploy
# Correr: bash scripts/security-check.sh

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0
WARNINGS=0

echo "🔒 CDS Security Pre-Flight Check"
echo "================================="
echo ""

# ============================================
# 1. Verificar que no hay secrets hardcodeados
# ============================================
echo "1️⃣  Buscando posibles secrets hardcodeados..."

# Patrones de secrets
PATTERNS=(
  "sk_live_"           # Stripe live key
  "pk_live_"           # Stripe public key
  "BEGIN RSA PRIVATE"  # Clave privada
  "BEGIN OPENSSH"      # SSH key
  "AKIA"               # AWS Access Key
  "ghp_"               # GitHub Personal Token
  "glpat-"             # GitLab Personal Token
  "eyJ"                # JWT token (base64)
  "cloudinary://"      # Cloudinary URL completa
  "postgresql://"      # DB URL con password
  "mysql://"           # MySQL URL con password
)

FOUND_SECRETS=0
for pattern in "${PATTERNS[@]}"; do
  if grep -r "$pattern" CDS_VUE3_ZERO/src backend/app --include="*.py" --include="*.js" --include="*.vue" --include="*.ts" 2>/dev/null | grep -v "__pycache__" | grep -v ".pyc" | head -3; then
    FOUND_SECRETS=1
  fi
done

if [ $FOUND_SECRETS -eq 1 ]; then
  echo -e "${RED}   ❌ Posibles secrets encontrados en código${NC}"
  ERRORS=$((ERRORS + 1))
else
  echo -e "${GREEN}   ✅ No hay secrets hardcodeados obvious${NC}"
fi

# ============================================
# 2. Verificar archivos .env no trackeados
# ============================================
echo ""
echo "2️⃣  Verificando que .env no está en git..."

if git ls-files | grep -E "^\.env$|\.env\.local$|backend/\.env$" > /dev/null 2>&1; then
  echo -e "${RED}   ❌ Archivos .env trackeados en git:${NC}"
  git ls-files | grep -E "^\.env$|\.env\.local$|backend/\.env$"
  ERRORS=$((ERRORS + 1))
else
  echo -e "${GREEN}   ✅ .env files correctamente ignorados${NC}"
fi

# ============================================
# 3. Verificar longitud de secrets (si existen)
# ============================================
echo ""
echo "3️⃣  Verificando secrets del backend..."

if [ -f "backend/.env" ]; then
  # Verificar SECRET_KEY
  if [ -n "${SECRET_KEY:-}" ]; then
    if [ ${#SECRET_KEY} -lt 32 ]; then
      echo -e "${RED}   ❌ SECRET_KEY muy corto (${#SECRET_KEY} chars, mínimo 32)${NC}"
      ERRORS=$((ERRORS + 1))
    else
      echo -e "${GREEN}   ✅ SECRET_KEY longitud OK${NC}"
    fi
  else
    echo -e "${YELLOW}   ⚠️  SECRET_KEY no definido (usando default)${NC}"
    WARNINGS=$((WARNINGS + 1))
  fi
  
  # Verificar que JWT secrets son diferentes
  if [ -n "${JWT_SECRET:-}" ] && [ -n "${JWT_REFRESH_SECRET:-}" ]; then
    if [ "$JWT_SECRET" = "$JWT_REFRESH_SECRET" ]; then
      echo -e "${RED}   ❌ JWT_SECRET y JWT_REFRESH_SECRET son iguales${NC}"
      ERRORS=$((ERRORS + 1))
    else
      echo -e "${GREEN}   ✅ JWT secrets son diferentes${NC}"
    fi
  fi
else
  echo -e "${YELLOW}   ⚠️  No hay backend/.env (usando defaults)${NC}"
fi

# ============================================
# 4. Verificar configuración de producción
# ============================================
echo ""
echo "4️⃣  Verificando configuración de entorno..."

ENVIRONMENT=${ENVIRONMENT:-development}

if [ "$ENVIRONMENT" = "production" ]; then
  echo -e "   ℹ️  Modo producción detectado"
  
  if [ "${DEBUG:-true}" = "true" ]; then
    echo -e "${RED}   ❌ DEBUG=true en producción${NC}"
    ERRORS=$((ERRORS + 1))
  else
    echo -e "${GREEN}   ✅ DEBUG=false${NC}"
  fi
  
  if [ "${ENFORCE_CSRF:-false}" = "false" ]; then
    echo -e "${RED}   ❌ ENFORCE_CSRF=false en producción${NC}"
    ERRORS=$((ERRORS + 1))
  else
    echo -e "${GREEN}   ✅ ENFORCE_CSRF=true${NC}"
  fi
  
  if [ "${ENABLE_API_DOCS:-true}" = "true" ]; then
    echo -e "${YELLOW}   ⚠️  ENABLE_API_DOCS=true en producción (exposición de docs)${NC}"
    WARNINGS=$((WARNINGS + 1))
  fi
else
  echo -e "   ℹ️  Modo desarrollo (OK para local): $ENVIRONMENT"
fi

# ============================================
# 5. Verificar dependencias
# ============================================
echo ""
echo "5️⃣  Verificando dependencias..."

# Verificar si hay npm audit
if command -v npm &> /dev/null; then
  echo "   🔍 Corriendo npm audit..."
  cd CDS_VUE3_ZERO
  if npm audit --audit-level=high 2>/dev/null | grep -q "found 0 vulnerabilities"; then
    echo -e "${GREEN}   ✅ No hay vulnerabilidades HIGH/CRITICAL en frontend${NC}"
  else
    echo -e "${YELLOW}   ⚠️  npm audit reportó vulnerabilidades (revisar arriba)${NC}"
    WARNINGS=$((WARNINGS + 1))
  fi
  cd ..
fi

# ============================================
# 6. Verificar CSP headers (build)
# ============================================
echo ""
echo "6️⃣  Verificando CSP en build..."

if [ -f "CDS_VUE3_ZERO/dist/index.html" ]; then
  echo -e "${GREEN}   ✅ Build existe${NC}"
  # Podríamos verificar meta tags CSP aquí
else
  echo -e "${YELLOW}   ⚠️  No hay build (correr npm run build para verificar)${NC}"
fi

# ============================================
# 7. Verificar que el backend tiene CORS configurado
# ============================================
echo ""
echo "7️⃣  Verificando CORS backend..."

if grep -q "allowed_origins" backend/app/core/config.py; then
  echo -e "${GREEN}   ✅ CORS configurado en backend${NC}"
else
  echo -e "${RED}   ❌ CORS no encontrado en backend${NC}"
  ERRORS=$((ERRORS + 1))
fi

# ============================================
# Resumen
# ============================================
echo ""
echo "================================="
echo "📊 RESUMEN"
echo "================================="

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
  echo -e "${GREEN}✅ Todos los checks pasaron${NC}"
  exit 0
elif [ $ERRORS -eq 0 ]; then
  echo -e "${YELLOW}⚠️  $WARNINGS advertencias (no bloqueantes)${NC}"
  exit 0
else
  echo -e "${RED}❌ $ERRORS errores encontrados${NC}"
  if [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}⚠️  $WARNINGS advertencias${NC}"
  fi
  echo ""
  echo "Corrige los errores antes de deployar."
  exit 1
fi
