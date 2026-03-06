# Cirujano de Sintetizadores (CDS)

Estado auditado: 2026-03-06

Este README refleja el estado real del repositorio en este momento (frontend + backend), usando como fuente el código actual y no documentos históricos.

## 1. Objetivo del proyecto

CDS es una plataforma de taller para:

- ingreso y seguimiento de reparaciones
- clientes y dispositivos
- inventario y catálogo tienda
- cotizaciones, pagos y comprobantes
- tickets, manuales, garantías
- firma digital por enlace y carga de fotos por enlace

## 2. Estructura real del repositorio

Raíz principal:

- `src/` frontend Vue 3
- `backend/` API FastAPI
- `tests/` pruebas frontend/integración
- `backend/tests/` pruebas backend
- `.github/workflows/` CI/CD y seguridad
- `database/` SQL y seeds
- `scripts/` utilidades de soporte
- `public/` assets públicos frontend

Conteo auditado del frontend:

- componentes Vue: 127 (`src/vue/components`)
- páginas Vue totales: 36 (`src/vue/content/pages`)
- páginas admin: 16 (`src/vue/content/pages/admin`)
- módulos calculadora tipo `*View.vue`: 9 (`src/modules/*`)

## 3. Frontend actual

Stack principal:

- Vue 3 + Vue Router + Pinia
- Vite
- Vitest + Testing Library
- Playwright (E2E)
- Sass (migración activa hacia estilos en SFC + tokens CSS)

Entrada principal:

- `src/main.js`
- actualmente carga `src/assets/styles/tokens.css`
- la carga del SCSS global legado está comentada de forma explícita durante la migración

Ruteo fuente de verdad:

- `src/router/index.ts`
- 46 entradas `path` declaradas (incluyendo hijos y fallback)

### 3.1 Inventario de rutas frontend

Públicas:

- `/`
- `/license`
- `/policy`
- `/terminos`
- `/privacidad`
- `/agendar`
- `/cotizador-ia`
- `/calculadoras`
- `/tienda`

Autenticación:

- `/login`
- `/register`
- `/password-reset`

Cliente autenticado:

- `/dashboard`
- `/ot-payments`
- `/repairs`
- `/repairs/:id`
- `/profile`

Admin:

- `/admin`
- `/admin/inventory`
- `/admin/inventory/unified`
- `/admin/clients`
- `/admin/repairs`
- `/admin/repairs/:id`
- `/admin/quotes`
- `/admin/categories`
- `/admin/contact`
- `/admin/newsletter`
- `/admin/appointments`
- `/admin/tickets`
- `/admin/purchase-requests`
- `/admin/manuals`
- `/admin/stats`
- `/admin/wizards`
- `/admin/archive`

Rutas por token:

- `/signature/:token`
- `/photo-upload/:token`

Calculadoras:

- `/calc/555`
- `/calc/resistor-color`
- `/calc/smd-capacitor`
- `/calc/smd-resistor`
- `/calc/ohms-law`
- `/calc/temperature`
- `/calc/number-system`
- `/calc/length`
- `/calc/awg`

Fallback:

- `/:pathMatch(.*)*`

## 4. Backend actual

Stack principal:

- FastAPI
- SQLAlchemy + Alembic
- JWT/Auth + rate limit
- endpoints amplios en `backend/app/routers` y `backend/app/api/v1/endpoints`

Aplicación principal:

- `backend/app/main.py`
- prefijo API principal: `/api/v1`
- endpoint de salud: `/health` y `/api/health`

Observaciones de runtime:

- en entorno de pruebas usa lifespan liviano para acelerar test suite
- documentación OpenAPI/UI depende de configuración de entorno
- CORS se configura por entorno y defaults de desarrollo

Inventario auditado del backend:

- 249 rutas HTTP registradas en app
- 181 paths OpenAPI
- 35 grupos de rutas bajo `/api/v1/*`

Grupos `/api/v1` detectados:

- `ai`
- `analytics`
- `appointments`
- `auth`
- `brands`
- `categories`
- `client`
- `clients`
- `contact`
- `devices`
- `diagnostic`
- `files`
- `imports`
- `instruments`
- `instruments-sync`
- `inventory`
- `invoices`
- `items`
- `manuals`
- `newsletter`
- `payments`
- `photo-requests`
- `purchase-requests`
- `quotations`
- `repair-statuses`
- `repairs`
- `search`
- `signatures`
- `stats`
- `stock-movements`
- `tickets`
- `tools`
- `uploads`
- `users`
- `warranties`

Dependencias backend destacadas por uso real:

- lectura de inventario en Excel: `pandas` + `openpyxl`

## 5. Comparativa README anterior vs estado real

Ajustes aplicados en esta versión:

- removido inventario explícito de variables sensibles en texto
- removidos ejemplos de cadenas sensibles o placeholders de credenciales
- actualizado inventario de rutas frontend a 46 entradas reales
- alineado backend a conteo real de rutas y grupos actuales
- alineado stack con `package.json` y `backend/requirements.txt` vigentes
- eliminado contenido histórico que no aporta a operación actual

## 6. Ejecución local

Frontend:

```bash
npm ci
npm run dev
```

Backend:

```bash
cd backend
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

Build frontend:

```bash
npm run build
```

## 7. Pruebas y validación

Frontend:

```bash
npm run lint
npm run test -- --run
npm run test:integration
```

Backend:

```bash
cd backend
ENVIRONMENT=testing DATABASE_URL=sqlite:///./test_ci.db pytest tests/ --verbose
```

E2E:

```bash
npm run test:e2e
```

## 8. CI/CD actual

Workflows activos:

- `.github/workflows/tests.yml`
- `.github/workflows/ci.yml`
- `.github/workflows/deploy.yml`
- `.github/workflows/secret-scan.yml`
- `.github/workflows/security.yml`

Validaciones relevantes:

- pruebas frontend/backend/integración
- build frontend y build docker condicionado
- escaneo de secretos con baseline
- control de artefactos locales/sensibles trackeados

## 9. Higiene de secretos y artefactos

Regla del repositorio:

- no subir credenciales reales
- no subir bases locales, logs, uploads ni artefactos de test
- usar archivos de plantilla para configuración local/producción

Archivos de plantilla existentes:

- `.env.example`
- `backend/.env.example`
- `.env.production.example`
- `.env.docker`

Política de documentación:

- este README no incluye claves, tokens ni contraseñas
- este README no incluye ejemplos con credenciales embebidas

## 10. Criterio de cambios (migración activa)

Se mantiene el enfoque del proyecto:

- aditivo
- deconstructivo
- no destructivo
- reutilizar lo existente antes de crear
- evitar variables inventadas y comportamiento implícito

