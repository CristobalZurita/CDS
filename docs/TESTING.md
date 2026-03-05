# Testing (Aditivo)

## Frontend
- Runner: Vitest (`npm run test`).
- Ubicación: `tests/`.
- Coverage real: `npm run test:coverage`.
- Reportes para IDE/herramientas:
  - `coverage/lcov.info`
  - `coverage/coverage-summary.json`

## Backend
- Runner: pytest + pytest-asyncio.
- Ubicación: `backend/tests/`.

## Objetivo mínimo
- Cobertura sobre flujos críticos: auth, inventory, repairs, payments.

## Flujo E2E aislado
- `npm run test:e2e` ya no toca la base operativa.
- Frontend E2E: `http://127.0.0.1:5174`
- Backend E2E: `http://127.0.0.1:8001`
- Runtime aislado:
  - DB: `backend/tests/e2e_runtime/e2e_cirujano.db`
  - uploads: `backend/tests/e2e_runtime/uploads`
- Base operativa real:
  - `backend/cirujano.db`

## Limpieza operativa
- Si se quiere limpiar basura E2E de la base real: `python scripts/e2e/cleanup_operational_db.py`
- Si se quiere reconstruir el runtime E2E manualmente: `python scripts/e2e/reset_environment.py`

## Comandos base
```bash
npm run test:coverage
npm run test:e2e
npm run build
```

## Matriz actual
- Ver `docs/TESTING_COVERAGE_MATRIX.md` para el estado cuantificado de rutas, auditoría admin, CRUD E2E y coverage instrumentado.
- Ver `docs/TESTING_STATUS_BRIEF.md` para un resumen corto listo para explicar a otra persona.

## Foto actual
- `npm run test:coverage`:
  - `170/170` passing
  - lines/statements: `39.07%`
  - branches: `61.9%`
  - functions: `41%`
- `npm run test:e2e`:
  - `91/91` passing
- `npm run build`:
  - passing
