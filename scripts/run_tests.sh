#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
BACKEND_PYTHON="$BACKEND_DIR/.venv/bin/python"
BACKEND_HOST="${BACKEND_TEST_HOST:-127.0.0.1}"
BACKEND_PORT="${BACKEND_TEST_PORT:-8002}"
BACKEND_LOG_DIR="$ROOT_DIR/.tmp"
BACKEND_LOG_FILE="$BACKEND_LOG_DIR/backend-integration.log"
BACKEND_PID=""

BACKEND_STATUS=0
E2E_STATUS=0

export TURNSTILE_DISABLE="${TURNSTILE_DISABLE:-true}"
export ENVIRONMENT="${ENVIRONMENT:-development}"
export TEST_DB_PATH="${TEST_DB_PATH:-$BACKEND_DIR/tests/test_cirujano.db}"
export DATABASE_URL="${DATABASE_URL:-sqlite:///$TEST_DB_PATH}"
export JWT_SECRET="${JWT_SECRET:-test-secret}"
export JWT_REFRESH_SECRET="${JWT_REFRESH_SECRET:-test-refresh-secret}"
export SKIP_MIGRATIONS="${SKIP_MIGRATIONS:-1}"
export ENABLE_INSTRUMENT_AUTO_SYNC="${ENABLE_INSTRUMENT_AUTO_SYNC:-false}"
export INSTRUMENT_SYNC_ON_STARTUP="${INSTRUMENT_SYNC_ON_STARTUP:-false}"
export BACKEND_TEST_BASE_URL="${BACKEND_TEST_BASE_URL:-http://$BACKEND_HOST:$BACKEND_PORT}"

cleanup() {
  if [ -n "$BACKEND_PID" ] && kill -0 "$BACKEND_PID" 2>/dev/null; then
    kill "$BACKEND_PID" 2>/dev/null || true
    wait "$BACKEND_PID" 2>/dev/null || true
  fi
}

trap cleanup EXIT

BACKEND_ARGS=(
  -m pytest
  tests/test_api_integration.py
  tests/test_auth_guards.py
)

if (cd "$BACKEND_DIR" && "$BACKEND_PYTHON" -m pytest --help | grep -q -- "--cov"); then
  BACKEND_ARGS+=(
    --cov=app
    --cov-report=term-missing
  )
else
  echo "WARNING: pytest-cov no esta disponible en backend/.venv; se ejecuta pytest sin coverage."
fi

mkdir -p "$BACKEND_LOG_DIR"

echo "==> Starting backend test server"
(
  cd "$BACKEND_DIR"
  exec "$BACKEND_PYTHON" -m uvicorn app.main:app --host "$BACKEND_HOST" --port "$BACKEND_PORT" --app-dir "$BACKEND_DIR"
) >"$BACKEND_LOG_FILE" 2>&1 &
BACKEND_PID=$!

BACKEND_READY=0
for _ in $(seq 1 60); do
  if curl -fsS "$BACKEND_TEST_BASE_URL/health" >/dev/null 2>&1; then
    BACKEND_READY=1
    break
  fi
  sleep 1
done

echo "==> Backend integration tests"
if [ "$BACKEND_READY" -ne 1 ]; then
  echo "Backend test server did not become ready."
  tail -n 40 "$BACKEND_LOG_FILE" || true
  BACKEND_STATUS=1
elif (cd "$BACKEND_DIR" && "$BACKEND_PYTHON" "${BACKEND_ARGS[@]}"); then
  BACKEND_STATUS=0
else
  BACKEND_STATUS=$?
fi

echo
echo "==> Playwright integration flow"
if (cd "$ROOT_DIR" && npm run test:e2e -- tests/e2e/integration-flows.spec.ts); then
  E2E_STATUS=0
else
  E2E_STATUS=$?
fi

echo
echo "==> Summary"
if [ "$BACKEND_STATUS" -eq 0 ]; then
  echo "backend: PASS"
else
  echo "backend: FAIL ($BACKEND_STATUS)"
fi

if [ "$E2E_STATUS" -eq 0 ]; then
  echo "playwright: PASS"
else
  echo "playwright: FAIL ($E2E_STATUS)"
fi

if [ "$BACKEND_STATUS" -ne 0 ] || [ "$E2E_STATUS" -ne 0 ]; then
  exit 1
fi
