#!/usr/bin/env bash
# scan_unsafe.sh — detecta patrones inseguros en el código JS/Vue/TS del frontend.
# Retorna 0 si no hay coincidencias, 1 si encuentra patrones peligrosos.
# Patrones cubiertos: eval(), new Function(), innerHTML (asignación directa).
#
# Uso: bash tools/scan_unsafe.sh
# Invocado por tests/test_security_scan.py como parte del CI de seguridad.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Desde backend/tools/ subimos hasta la raíz del repositorio
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
FRONTEND_DIR="${REPO_ROOT}/CDS_VUE3_ZERO/src"

# Si el directorio frontend no existe (entorno CI sin frontend), salir OK.
if [ ! -d "${FRONTEND_DIR}" ]; then
  echo "[scan_unsafe] Frontend dir not found at ${FRONTEND_DIR} — skipping."
  exit 0
fi

FOUND=0

# Función auxiliar: busca patrón y reporta coincidencias.
_scan() {
  local label="$1"
  local pattern="$2"
  local results
  results=$(grep -rn --include="*.js" --include="*.ts" --include="*.vue" \
    "$pattern" "${FRONTEND_DIR}" 2>/dev/null || true)
  if [ -n "$results" ]; then
    echo "[UNSAFE] ${label}:"
    echo "$results"
    FOUND=1
  fi
}

# eval() — XSS / code injection
_scan "eval()" '\beval\s*('

# new Function() — dynamic code execution
_scan "new Function(" '\bnew\s+Function\s*('

# innerHTML = — direct DOM injection (assignment, not read)
_scan "innerHTML =" 'innerHTML\s*='

# document.write — legacy XSS vector
_scan "document.write" '\bdocument\.write\s*('

if [ "${FOUND}" -eq 0 ]; then
  echo "[scan_unsafe] OK — no unsafe patterns detected."
fi

exit "${FOUND}"
