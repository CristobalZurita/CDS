#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STAMP="$(date +%Y%m%d_%H%M%S)"
OUT_DIR="$ROOT_DIR/docs"
OUT_FILE="$OUT_DIR/auditoria_fase0_${STAMP}.md"

mkdir -p "$OUT_DIR"

{
  echo "# Auditoria Fase 0 - CDS"
  echo
  echo "- Fecha: $(date -Iseconds)"
  echo "- Root: $ROOT_DIR"
  echo
  echo "## 1) Modelos SQLAlchemy detectados"
  echo '```text'
  rg "class .*(Base|\\(Base\\))" "$ROOT_DIR/backend" --type py || true
  echo '```'
  echo

  echo "## 2) Routers/endpoints detectados"
  echo '```text'
  rg "@router\\." "$ROOT_DIR/backend" --type py -l || true
  echo '```'
  echo

  echo "## 3) Accesos DB directos (candidate hotspots)"
  echo '```text'
  rg "db\\.query|db\\.execute|session\\.query" "$ROOT_DIR/backend" --type py || true
  echo '```'
  echo

  echo "## 4) Llamadas HTTP directas en frontend (candidate hotspots)"
  echo '```text'
  rg "axios\\.|\\.get\\(|\\.post\\(" "$ROOT_DIR/src" --type vue --type js --type ts || true
  echo '```'
  echo

  echo "## 5) Alembic status"
  echo '```text'
  if [[ -f "$ROOT_DIR/backend/alembic.ini" ]]; then
    (
      cd "$ROOT_DIR/backend"
      alembic current 2>&1 || true
      alembic history --verbose 2>&1 || true
    )
  else
    echo "No se encontro backend/alembic.ini"
  fi
  echo '```'
  echo

  echo "## 6) Git status (snapshot)"
  echo '```text'
  (
    cd "$ROOT_DIR"
    git status --short
  ) || true
  echo '```'
} > "$OUT_FILE"

echo "Auditoria Fase 0 generada en:"
echo "$OUT_FILE"
