# Cirujano de Sintetizadores

Plataforma web para operacion de taller, seguimiento de reparaciones y relacion cliente-tecnico.

El proyecto hoy integra tres capas funcionales:
- Portal publico para servicios, contacto, contenido y diagnostico/cotizacion.
- Portal cliente para seguimiento de OT, perfil, pagos y documentos.
- Portal administrador para clientes, reparaciones, inventario, citas, tickets, compras y manuales.

## Resumen Ejecutivo

La aplicacion esta construida sobre:
- Frontend: Vue 3 + Vite + Pinia + Vue Router
- Backend: FastAPI + SQLAlchemy
- Base de datos local por defecto: SQLite en `backend/cirujano.db`
- Pruebas: Vitest para front unitario/integracion y Playwright para E2E

El frontend trabaja como SPA, pero el repo ya incorpora una capa de auditoria automatizada para validar navegacion, rutas protegidas, formularios y CRUD criticos sin revisar el sistema boton por boton.

## Alcance Funcional

### Publico
- Home y contenido institucional
- Formulario de contacto
- Agenda de citas
- Diagnostico/cotizador online
- Carga de fotos y firma por token publico

### Cliente
- Dashboard
- Estado e historial de reparaciones
- Perfil
- Pagos OT y comprobantes
- Acceso a documentos y cierre

### Administrador
- Dashboard interno
- Gestion de clientes y usuarios
- Reparaciones y OT
- Inventario y categorias
- Citas
- Tickets
- Solicitudes de compra
- Manuales
- Magos de ingreso y operacion

## Estructura Relevante

- Frontend: `src/`
- Backend: `backend/app/`
- Pruebas frontend: `tests/`
- Pruebas backend: `backend/tests/`
- Documentacion operativa: `docs/`
- Documentacion complementaria/archivo: `DOCUMJENTOS_EXTRAS/`
- Arquitectura Sass local: `src/scss/README.md`

## Ejecucion Local

### Frontend
```bash
npm install
npm run dev
```

### Backend
```bash
cd backend
uvicorn app.main:app --reload
```

Puertos habituales:
- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`

## Configuracion Base

### Frontend
Variable principal:
```bash
VITE_API_URL=http://localhost:8000/api/v1
```

### Backend
Configuracion por defecto:
- entorno: `development`
- base de datos: `sqlite:///./cirujano.db`
- archivo operativo: `backend/cirujano.db`

Nota:
- La configuracion efectiva sale de `backend/.env` y `backend/app/core/config.py`.
- No exponer secretos del `.env` en documentacion publica.

## Testing y Validacion

Comandos principales:
```bash
npm run build
npx vitest run --config vitest.config.ts --environment jsdom
npm run test:coverage
npm run test:e2e
```

Estado validado en esta revision:
- `npm run build`: OK
- `npx vitest run --config vitest.config.ts --environment jsdom`: `170/170` OK
- `npm run test:e2e -- tests/e2e/auth.spec.ts`: `5/5` OK
- `npm run test:coverage`: falla correctamente por umbrales globales no cumplidos

Coverage actual medido sobre `src`:
- lines/statements: `39.6%`
- branches: `62.44%`
- functions: `41.22%`

El flujo E2E ya corre aislado de la base operativa:
- frontend E2E: `127.0.0.1:5174`
- backend E2E: `127.0.0.1:8001`
- runtime E2E: `backend/tests/e2e_runtime/`

Mas detalle:
- `docs/TESTING.md`
- `docs/TESTING_STATUS_BRIEF.md`
- `docs/TESTING_COVERAGE_MATRIX.md`

## Estado Sass

La capa Sass del proyecto usa la estructura ya presente en `src/scss/`.

Estado actual:
- componentes Vue usando partials existentes con `_`
- sin CSS inline detectado en `src/`, `public/` y `tests/`
- sin `@extend`
- imports legacy concentrados en archivos base existentes:
  - `src/scss/_core.scss`
  - `src/scss/_theming.scss`
  - `src/scss/main.scss`
  - `src/scss/style.scss`

La guia local de esta capa vive en:
- `src/scss/README.md`

## Documentos Relacionados

- Testing operativo: `docs/TESTING.md`
- Estado corto de testing: `docs/TESTING_STATUS_BRIEF.md`
- Matriz de cobertura: `docs/TESTING_COVERAGE_MATRIX.md`
- Documento de rapidez/referencia externa: `DOCUMJENTOS_EXTRAS/RAPIDEZ.md`

## Nota Sobre RAPIDEZ.md

`DOCUMJENTOS_EXTRAS/RAPIDEZ.md` es una referencia de principios de performance, no la definicion de arquitectura del proyecto.

En este repo esos principios aplican como criterio:
- reducir trabajo innecesario
- evitar bloqueos de carga
- cargar solo lo necesario
- mantener estructura simple y mantenible

No obliga a cambiar el stack actual ni a salir de Vue/Vite/FastAPI.

## Criterio de Trabajo Vigente

Sobre este repo, la regla practica es:
- trabajar sobre la estructura existente
- preferir mejora aditiva
- deconstruir antes de duplicar
- reutilizar archivos, variables y capas ya presentes
- evitar capas paralelas e inventario innecesario de archivos

## Licencia y Uso

Proyecto de uso interno. Revisar antes de publicar o redistribuir.
