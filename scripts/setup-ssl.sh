#!/usr/bin/env bash
# ==========================================
# Cirujano de Sintetizadores - SSL Setup
# ==========================================
# Genera certificados SSL con Let's Encrypt (certbot)
# Uso: bash scripts/setup-ssl.sh
#
# PRE-REQUISITOS:
#   - Dominio apuntando al servidor (DNS A record)
#   - Puerto 80 abierto (para challenge HTTP-01)
#   - Docker y docker-compose instalados

set -euo pipefail

DOMAIN="${1:-cirujanodesintetizadores.cl}"
EMAIL="${2:-admin@cirujanodesintetizadores.cl}"
CERTS_DIR="./certs"
CERTBOT_DIR="./certbot"

echo "🔐 Configurando SSL para: ${DOMAIN}"
echo "📧 Email de contacto: ${EMAIL}"

# Crear directorios
mkdir -p "${CERTS_DIR}"
mkdir -p "${CERTBOT_DIR}"

# =====================
# Opción 1: Certificados auto-firmados (para desarrollo/testing)
# =====================
generate_self_signed() {
    echo "⚠️  Generando certificados auto-firmados (solo para testing)..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout "${CERTS_DIR}/privkey.pem" \
        -out "${CERTS_DIR}/fullchain.pem" \
        -subj "/CN=${DOMAIN}/O=CDS/C=CL"
    echo "✅ Certificados auto-firmados creados en ${CERTS_DIR}/"
    echo "⚠️  IMPORTANTE: Estos NO son válidos para producción real."
}

# =====================
# Opción 2: Let's Encrypt (producción real)
# =====================
generate_letsencrypt() {
    echo "🌐 Obteniendo certificados Let's Encrypt..."

    # Verificar que certbot está disponible
    if ! command -v certbot &> /dev/null; then
        echo "📦 Instalando certbot..."
        sudo apt-get update && sudo apt-get install -y certbot
    fi

    # Detener nginx temporalmente si está corriendo
    docker compose stop nginx 2>/dev/null || true

    # Obtener certificado
    sudo certbot certonly \
        --standalone \
        --preferred-challenges http \
        --agree-tos \
        --no-eff-email \
        --email "${EMAIL}" \
        -d "${DOMAIN}" \
        -d "www.${DOMAIN}"

    # Copiar certificados al directorio del proyecto
    sudo cp "/etc/letsencrypt/live/${DOMAIN}/fullchain.pem" "${CERTS_DIR}/fullchain.pem"
    sudo cp "/etc/letsencrypt/live/${DOMAIN}/privkey.pem" "${CERTS_DIR}/privkey.pem"
    sudo chown "$(whoami):$(whoami)" "${CERTS_DIR}"/*.pem
    chmod 600 "${CERTS_DIR}/privkey.pem"
    chmod 644 "${CERTS_DIR}/fullchain.pem"

    echo "✅ Certificados Let's Encrypt instalados en ${CERTS_DIR}/"

    # Reiniciar nginx
    docker compose up -d nginx 2>/dev/null || true
}

# =====================
# Renovación automática (cron)
# =====================
setup_auto_renewal() {
    echo "⏰ Configurando renovación automática..."

    RENEWAL_SCRIPT="/etc/cron.d/certbot-renew-cirujano"
    sudo bash -c "cat > ${RENEWAL_SCRIPT}" << 'CRON'
# Renovar certificados Let's Encrypt cada día a las 3:00 AM
0 3 * * * root certbot renew --quiet --deploy-hook "docker compose -f /opt/cirujano/docker-compose.yml exec nginx nginx -s reload" >> /var/log/certbot-renew.log 2>&1
CRON

    echo "✅ Renovación automática configurada"
}

# =====================
# Menú principal
# =====================
echo ""
echo "Seleccione una opción:"
echo "  1) Certificados auto-firmados (testing/desarrollo)"
echo "  2) Let's Encrypt (producción real)"
echo "  3) Solo renovación automática (ya tiene certificados)"
echo ""

read -rp "Opción [1/2/3]: " option

case "${option}" in
    1) generate_self_signed ;;
    2) generate_letsencrypt && setup_auto_renewal ;;
    3) setup_auto_renewal ;;
    *) echo "❌ Opción no válida"; exit 1 ;;
esac

echo ""
echo "🎉 Configuración SSL completada."
echo ""
echo "Próximos pasos:"
echo "  1. Verificar certificados: openssl x509 -in ${CERTS_DIR}/fullchain.pem -text -noout"
echo "  2. Levantar servicios: docker compose up -d"
echo "  3. Probar: curl -I https://${DOMAIN}"
