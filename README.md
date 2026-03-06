# Cirujano de Sintetizadores (CDS)

## 1. Project Overview

CDS is a full-stack repair-shop platform for synth intake, repair tracking, inventory, quotes, payments, manuals, warranties, tickets, token-based signatures, and token-based customer photo uploads. The FastAPI backend is broad; the Vue 3 SPA already exposes public, client, and admin routes, but the frontend is still uneven and several modules remain in progress or only partially validated.

### 1.1 Current Verified Snapshot (2026-03-05)

This README refresh is based on direct code inspection and test execution in this workspace:

- Frontend router source: `src/router/index.ts`
- Frontend pages scanned from: `src/vue/content/pages/` and `src/vue/content/pages/admin/`
- Vue components scanned from: `src/vue/components/`
- Backend route registration scanned from: `backend/app/main.py` and `backend/app/api/v1/router.py`
- Latest focused navigation audit run:
  - `PLAYWRIGHT_FRONTEND_PORT=5175 PLAYWRIGHT_API_PORT=8001 PLAYWRIGHT_BASE_URL=http://127.0.0.1:5175 PLAYWRIGHT_API_URL=http://127.0.0.1:8001/api/v1 npm run test:e2e -- tests/e2e/navigation-intent.spec.ts --project=chromium --no-deps`
  - Result: `4 passed`

Migration context currently present in repo:

- `MIGRACION_VUE_REAL.md` states active migration principles:
  - aditivo (no destructivo/sustractivo)
  - deconstructivo (desarmar y rearmar)
  - usar lo existente antes de crear
  - no inventar variables ni comportamiento

## 2. Architecture

```text
Browser
  |
  |  Public SPA routes, /tienda, /dashboard, /admin/*, /signature/:token, /photo-upload/:token
  v
Vue 3 + Vite dev server (:5173)
  |
  |  Axios baseURL = VITE_API_URL
  |  Auth flow:
  |    POST /api/v1/auth/login
  |    -> access_token + refresh_token
  |    -> stored in localStorage by src/composables/useAuth.ts
  |    -> GET /api/v1/auth/me hydrates the session
  |    -> POST /api/v1/auth/refresh rotates both tokens
  |
  v
FastAPI (:8000)
  |
  |  /api/v1/*
  |  Upload destinations used by current code:
  |    uploads/signatures/repair-{id}/signature-{ingreso|retiro}.png
  |    uploads/repairs/repair-{id}/...
  |    uploads/images/...
  |    public/images/INVENTARIO/...
  |    public/images/instrumentos/...
  |
  v
SQLite (dev default via DATABASE_URL=sqlite:///./cirujano.db)
or PostgreSQL (same app, via DATABASE_URL=postgresql://...)
```

## 3. Tech Stack

| Scope | Packages |
| --- | --- |
| Frontend runtime | `vue@^3.2.47`, `vue-router@^4.2.4`, `pinia@^3.0.4`, `axios@^1.13.2`, `bootstrap@^5.2.3`, `@popperjs/core@^2.11.7`, `@fortawesome/fontawesome-free@^6.4.0`, `swiper@^10.0.4`, `leaflet@^1.9.4`, `dompurify@^3.3.1`, `@emailjs/browser@^4.4.1`, `emailjs@^4.0.3`, `gh-pages@^6.3.0`, `primeicons@^7.0.0` |
| Frontend dev/test/build | `vite@^6.2.5`, `@vitejs/plugin-vue@^5.2.3`, `vitest@^1.6.1`, `@vitest/coverage-v8@^1.6.1`, `@vitest/ui@^1.6.1`, `@playwright/test@^1.58.2`, `@vue/test-utils@^2.4.6`, `@testing-library/vue@^8.1.0`, `@testing-library/user-event@^14.6.1`, `typescript@^5.2.2`, `sass@^1.62.1`, `eslint@^9.39.2`, `eslint-plugin-vue@^10.6.2`, `vue-eslint-parser@^10.2.0`, `@typescript-eslint/eslint-plugin@^8.52.0`, `@typescript-eslint/parser@^8.52.0`, `jsdom@^27.4.0`, `happy-dom@^20.6.1`, `sharp@^0.34.5`, `terser@^5.46.0`, `critters@^0.0.25`, `vite-plugin-imagemin@^0.6.1` |
| Backend runtime/API | `fastapi==0.104.1`, `uvicorn[standard]==0.24.0`, `sqlalchemy==2.0.23`, `alembic==1.12.1`, `psycopg2-binary==2.9.9`, `pydantic-settings==2.1.0`, `python-jose[cryptography]==3.3.0`, `passlib[bcrypt]==1.7.4`, `python-multipart==0.0.6`, `pydantic[email]==2.5.0`, `email-validator==2.1.0`, `python-dotenv==1.0.0`, `httpx==0.25.1`, `slowapi==0.1.5`, `limits==1.6.0`, `Pillow==10.1.0`, `python-magic==0.4.27`, `python-json-logger==2.0.6`, `sendgrid==6.10.0`, `google-auth==2.25.2`, `google-auth-oauthlib==1.1.0`, `google-auth-httplib2==0.2.0`, `google-api-python-client==2.104.0` |
| Backend dev/test/optional | `pytest==7.4.3`, `pytest-asyncio==0.21.1`, `black==23.12.0`, `ruff==0.1.8`, `asyncpg==0.29.0`, `redis==3.5.3`, `celery==5.3.4` |

## 4. Module Status

Audited Vue surface in `src/`: 20 non-admin page files, 16 admin page files, 9 calculator modules, 127 Vue components, and 48 route `path` declarations in `src/router/index.ts`.

| Module | Status | Notes |
| --- | --- | --- |
| Public portal | 🔄 IN PROGRESS | Public pages exist for home/legal pages, calculators, store, quote flow, signature, and photo upload. The current unit suite now covers the public shells/legal/token pages, but most landing content sections in `src/vue/content/sections/*` remain untested. |
| Auth & session | 🔄 IN PROGRESS | `/auth/login`, `/auth/register`, `/auth/me`, `/auth/refresh`, `/auth/logout`, password reset, and optional email 2FA exist. ⚠️ Current SPA stores JWTs in `localStorage`, and `deleteAccount()` is explicitly not implemented in backend. |
| Customer panel | ✅ WORKING | Routes exist for `/dashboard`, `/repairs`, `/repairs/:id`, `/profile`, `/ot-payments`, and `/agendar`. These pages all have active unit tests in `tests/unit/client/`. |
| Admin panel | 🔄 IN PROGRESS | Admin routes exist for inventory, clients, repairs, quotes, categories, contact, newsletter, appointments, tickets, purchase requests, manuals, stats, wizards, and archive. Test coverage is partial: inventory, quotes, manuals, appointments, and some wizard flows are covered, but not the entire admin surface. |
| Entry wizards | 🔄 IN PROGRESS | `WizardClientIntake`, `WizardInventoryItem`, `WizardManualUpload`, `WizardMaterialsUsage`, `WizardPurchaseRequest`, `WizardSignatureRequest`, and `WizardTicket` exist. Only `WizardPurchaseRequest` and `WizardTicket` are covered by active unit tests. |
| Calculator modules | ✅ WORKING | The full `src/modules/*` surface is covered in unit tests (`CalculatorWrappers`, `ResistorColorView`, `SmdCapacitorView`, `SmdResistorView`, `Timer555View`). ⚠️ Coverage is strong for modules, but global frontend thresholds still fail due uncovered views/admin/articles areas. |
| Digital signatures | ✅ WORKING | Backend request, lookup, submit, cancel, and SSE endpoints exist; public route `/signature/:token` exists; unit tests cover the page submission flow. ⚠️ Effective expiry is 1-5 minutes, not the schema default of 15. |
| Token photo uploads | ✅ WORKING | Public route `/photo-upload/:token` exists; backend request lookup and upload submission endpoints exist; page unit tests cover success and failure states. |
| Store / purchase requests | 🔄 IN PROGRESS | Public store page, cart widget, purchase-request board, and customer deposit-proof/payment confirmation flow exist. Focused navigation Playwright audit for `/`, `/tienda`, `/calculadoras`, `/privacidad` now passes (`4 passed`, see Section 11), but this does not replace a full authenticated end-to-end regression of every admin/client flow. |

### 4.1 Frontend Route Inventory (from `src/router/index.ts`)

Public (Master layout children):

- `/`
- `/license`
- `/policy`
- `/terminos`
- `/privacidad`
- `/agendar` (requires auth)
- `/cotizador-ia`
- `/calculadoras`
- `/tienda`

Auth:

- `/login`
- `/register`
- `/password-reset`

Client:

- `/dashboard`
- `/ot-payments`
- `/repairs`
- `/repairs/:id`
- `/profile`

Admin (`/admin` + children):

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

Public token routes:

- `/signature/:token`
- `/photo-upload/:token`

Calculator routes:

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

- `/:pathMatch(.*)*` -> redirect to `/`

### 4.2 Home Sections vs Real Routes

`Nosotros`, `Servicios`, and `Contacto` are currently in-page sections in `HomePage` (`SectionInfo` IDs `about`, `services`, `contact`) and resolve to hashes (`#about`, `#services`, `#contact`), not standalone paths like `/nosotros` or `/servicios`.

## 5. Environment Variables

Sources audited for this section: `.env.example`, `backend/.env.example`, `.env.production.example`.

### Frontend

- `VITE_API_URL`
- `VITE_APP_VERSION`
- `VITE_ANALYTICS_MODE`
- `VITE_ANALYTICS_URL`
- `VITE_GA_ID`
- `VITE_TURNSTILE_SITE_KEY`
- `VITE_TURNSTILE_DISABLE`
- `VITE_ENVIRONMENT` (defined in `.env.production.example`)

### Backend

- `DEBUG`
- `ENVIRONMENT`
- `DATABASE_URL`
- `SECRET_KEY`
- `JWT_SECRET`
- `JWT_REFRESH_SECRET`
- `ALLOW_TOKEN_IN_RESPONSE`
- `ENABLE_API_DOCS`
- `ENABLE_PUBLIC_UPLOADS`
- `CORS_ORIGINS`
- `ALLOWED_ORIGINS`
- `SMTP_HOST`
- `SMTP_SERVER`
- `SMTP_PORT`
- `SMTP_USER`
- `SMTP_PASSWORD`
- `SMTP_USE_TLS`
- `SMTP_USE_SSL`
- `FROM_EMAIL`
- `SMTP_FROM_EMAIL`
- `PUBLIC_BASE_URL`
- `ENFORCE_CSRF`
- `RATE_LIMIT_STORAGE_URI`
- `REDIS_URL`
- `ENABLE_INSTRUMENT_AUTO_SYNC`
- `INSTRUMENT_SYNC_ON_STARTUP`
- `INSTRUMENT_SYNC_INTERVAL_MINUTES`
- `CLAUDE_API_KEY`
- `SENDGRID_API_KEY`
- `SENDGRID_FROM_EMAIL`
- `GOOGLE_CALENDAR_CREDENTIALS_FILE`
- `GOOGLE_CALENDAR_ID`
- `UPLOAD_DIR`
- `MAX_FILE_SIZE`
- `IMAGE_MAX_SIZE`
- `ENCRYPTION_KEY`
- `LOG_LEVEL`
- `LOG_FILE`
- `INVENTORY_EXCEL_PATH`
- `IMPORT_DB_PATH`
- `KICAD_SYMBOLS_PATH`
- `TURNSTILE_SECRET_KEY`
- `TURNSTILE_DISABLE`
- `WHATSAPP_TOKEN`
- `WHATSAPP_PHONE_ID`
- `WHATSAPP_API_URL`
- `WHATSAPP_TEMPLATE_NAME`
- `WHATSAPP_TEMPLATE_LANG`
- `SEED_ADMIN_PASSWORD`
- `SEED_TEST_PASSWORD`

### Production

- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`
- `DATABASE_URL` (PostgreSQL)
- `REDIS_URL`
- `SECRET_KEY`
- `JWT_SECRET`
- `JWT_REFRESH_SECRET`
- `ENFORCE_CSRF`
- `ALLOW_TOKEN_IN_RESPONSE`
- `ENABLE_API_DOCS`
- `ENABLE_PUBLIC_UPLOADS`
- `ALLOWED_ORIGINS`
- `PUBLIC_BASE_URL`
- `SMTP_*`
- `WHATSAPP_*`
- `TURNSTILE_*`
- `CLAUDE_API_KEY`
- `UPLOAD_DIR`
- `MAX_FILE_SIZE`

⚠️ `.env.example` and `backend/.env.example` include active runtime keys plus legacy placeholders (`CLAUDE_API_KEY`, `MAX_FILE_SIZE`, `UPLOAD_DIR`) that are not currently part of the critical request path.

## 6. Local Setup

1. Copy both env templates so Vite and FastAPI read values from the expected places.

```bash
cp .env.example .env
cp backend/.env.example backend/.env
```

2. Install frontend dependencies.

```bash
npm install
```

3. Create or reuse the backend virtual environment and install Python dependencies.

```bash
test -d backend/.venv || python3 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements.txt
```

4. Run Alembic from inside `backend/`.

```bash
cd backend
.venv/bin/python -m alembic upgrade head
cd ..
```

5. Seed a development database if you want local users and base roles.

```bash
cd backend
.venv/bin/python scripts/init_db_and_seed.py --allow-default-credentials
cd ..
```

6. Start the backend from inside `backend/`.

```bash
cd backend
.venv/bin/python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

7. In another terminal, start the frontend.

```bash
npm run dev
```

8. Open the local services.

- Frontend: `http://localhost:5173`
- Backend health: `http://localhost:8000/health`
- Swagger: `http://localhost:8000/docs` only if `ENABLE_API_DOCS=true`

⚠️ Run backend commands from `backend/`. The default `DATABASE_URL=sqlite:///./cirujano.db` is relative, so running `uvicorn` or `alembic` from the repo root points at a different SQLite file.

### Local-only artifacts and secret hygiene

- `backend/cirujano.db` is a local SQLite development artifact. Keep it local; do not commit it.
- `backend/cirujano.log*` are local operational logs. Keep them local; do not commit them.
- `.env`, `backend/.env`, uploads, SQLite artifacts, and rotated logs are ignored by `.gitignore`.
- The repo history was rewritten on 2026-03-04 to purge `backend/cirujano.db`, `backend/cirujano.log.1`, and the confirmed legacy seed password from Git history.
- `.github/workflows/secret-scan.yml` now blocks tracked local env files, tracked DB/log/upload artifacts, and known legacy weak literals before they are merged again.

## 7. Authentication & Authorization

### JWT flow

1. `POST /api/v1/auth/login` accepts `email`, `password`, and optional `turnstile_token`.
2. If `two_factor_enabled` is on, login returns `{ "requires_2fa": true, "challenge_id": ... }` and the code is stored in `two_factor_codes` with a 10-minute expiry.
3. Otherwise login returns `access_token`, `refresh_token`, and `token_type`.
4. The SPA stores both tokens in `localStorage` in `src/composables/useAuth.ts` and `src/stores/auth.ts`.
5. `src/services/api.ts` adds `Authorization: Bearer <access_token>` from `localStorage` on outgoing requests.
6. `GET /api/v1/auth/me` hydrates the current user after login or on route guard hydration.
7. `POST /api/v1/auth/refresh` expects `{ "refresh_token": "..." }` and returns a new access token plus a new refresh token.
8. `POST /api/v1/auth/logout` exists, but the current backend only returns a success message. Real session invalidation is frontend-side: the SPA clears `localStorage`.
9. Password reset is implemented with `POST /api/v1/auth/forgot-password` and `POST /api/v1/auth/reset-password`.

⚠️ `src/services/api.ts` is cookie/CSRF-ready (`withCredentials=true` and CSRF header support), but the active auth flow still uses bearer tokens in `localStorage`, not HttpOnly cookies.

### Roles and access

- `guest`: public routes only.
- `client`: `/dashboard`, `/repairs`, `/repairs/:id`, `/profile`, `/ot-payments`, and `/agendar`.
- `admin`: all client routes plus `/admin/*`.
- `technician`: exists in backend and in the frontend auth store (`isTechnician`), but there is no dedicated technician route branch in `src/router/index.ts`.
- Granular server-side roles and permissions also exist through `permissions`, `roles`, and `user_role_assignments`. Current predefined roles in code are `super_admin`, `admin`, `technician`, `receptionist`, and `viewer`, but actual assignments depend on seed/data in the target database.

### Frontend router guards

- Location: `src/router/index.ts`
- Guard types in current code: `requiresAuth`, `requiresAdmin`, `requiresGuest`
- Behavior:
  - unauthenticated users are redirected to `/login?redirect=...`
  - authenticated non-admin users are redirected away from `/admin/*`
  - authenticated users are redirected away from guest-only routes like `/login` and `/register`

⚠️ `useAuth().deleteAccount()` currently returns `false` and sets `deleteAccount endpoint not implemented in backend`.

## 8. Digital Signature Flow

1. An authorized user creates a request with `POST /api/v1/signatures/requests`.
2. The backend creates a `signature_requests` row with a random `token`, `status="pending"`, `request_type` (`ingreso` or `retiro`), and `expires_at`.
3. The current router clamps `expires_minutes` to `1..5`. The schema default is `15`, but any value above `5` is reduced to `5`.
4. The public SPA route is `/signature/:token`.
5. The page in `src/vue/content/pages/SignaturePage.vue` captures a canvas signature and posts base64 PNG data to `POST /api/v1/signatures/submit`.
6. The backend stores the PNG at `uploads/signatures/repair-{repair_id}/signature-{request_type}.png`.
7. The saved path is written into `repairs.signature_ingreso_path` or `repairs.signature_retiro_path`.
8. On submit, the request is marked `signed`, `signed_at` is recorded, client IP and user-agent are recorded, and the token is rotated to prevent replay.
9. Admin lookup endpoints exist at:
   - `GET /api/v1/signatures/requests/{request_id}`
   - `GET /api/v1/signatures/requests/token/{token}`
   - `GET /api/v1/signatures/stream/{token}` for SSE updates
10. Revocation/cancellation is partially implemented with `POST /api/v1/signatures/requests/{request_id}/cancel`.

⚠️ There is no restore/un-cancel endpoint, and there is no endpoint to delete an already stored signature file after submission.

## 9. Database & Migrations

### Active database behavior

- Default development DB: SQLite via `DATABASE_URL=sqlite:///./cirujano.db`
- Production-capable DB driver shipped in requirements: PostgreSQL via `psycopg2-binary`
- Active DB engine code lives in `backend/app/core/database.py`
- Active Alembic config lives in `backend/alembic.ini`
- Current Alembic head: `009_add_quote_items_and_recipients`

### Run migrations

```bash
cd backend
.venv/bin/python -m alembic upgrade head
```

### Roll back one revision

```bash
cd backend
.venv/bin/python -m alembic downgrade -1
```

### Seed script

```bash
cd backend
.venv/bin/python scripts/init_db_and_seed.py --allow-default-credentials
```

Additional seed scripts present today:

```bash
cd backend
.venv/bin/python scripts/seed_permissions.py
.venv/bin/python scripts/seed_admin.py
```

### SQLite -> PostgreSQL migration

1. Create an empty PostgreSQL database and user outside the app.
2. Set a PostgreSQL URL in `backend/.env`, for example:

```bash
DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/cirujano_db
```

3. From `backend/`, run the schema migrations against PostgreSQL.

```bash
cd backend
.venv/bin/python -m alembic upgrade head
```

4. Seed permissions/roles if you need server-side RBAC.

```bash
cd backend
.venv/bin/python scripts/seed_permissions.py
```

5. Seed users only if you want the repo's development users.

```bash
cd backend
.venv/bin/python scripts/init_db_and_seed.py --allow-default-credentials
```

6. If you need existing SQLite data inside PostgreSQL, manual ETL is still required. This repo does not contain a `sqlite -> postgres` transfer script.

### ORM models actually present in `backend/app/models/`

- Users/auth: `UserRole`, `User`, `Role`, `Permission`, `TwoFactorCode`
- Clients/repairs: `Client`, `Device`, `RepairStatus`, `Repair`, `RepairNote`, `RepairPhoto`, `RepairIntakeSheet`, `RepairComponentUsage`, `SignatureRequest`, `PhotoUploadRequest`, `Appointment`, `Ticket`, `TicketMessage`, `ContactMessage`, `AuditLog`
- Catalog/inventory: `Category`, `Brand`, `Instrument`, `InstrumentPhoto`, `Product`, `Stock`, `StockMovement`, `StorageLocation`, `Tool`, `ToolBrand`, `ToolCategory`, `DeviceBrand`, `DeviceType`, `ManualDocument`
- Commercial: `Quote`, `QuoteItem`, `QuoteRecipient`, `Payment`, `PurchaseRequest`, `PurchaseRequestItem`, `Invoice`, `InvoiceItem`, `InvoiceSequence`, `Warranty`, `WarrantyClaim`, `NewsletterSubscription`

⚠️ App startup also runs `Base.metadata.create_all()` plus multiple `_ensure_*_schema()` patch functions in `backend/app/core/database.py`. Alembic is not the only schema path in the current codebase.

## 10. API Reference

Swagger: `http://localhost:8000/docs`

⚠️ In the current code, Swagger only exists when `ENABLE_API_DOCS=true`. `.env.example` sets `ENABLE_API_DOCS=false`, so `/docs` returns `404` unless you enable it.

### Global endpoints outside `/api/v1`

- `GET /`
- `GET /health`
- `GET /api/health`
- `GET /api/csrf-token`
- `POST /api/logs`
- `POST /api/metrics`
- `GET /api/logs`
- `GET /api/metrics`
- `GET /api/logs/stats`
- `DELETE /api/logs`
- `DELETE /api/metrics`
- `/uploads/*` and `/static/*` when exposed

### Main endpoint groups mounted under `/api/v1`

| Prefix | Notes |
| --- | --- |
| `/auth` | login, register, logout, me, refresh, 2FA, password reset, email confirmation |
| `/users` | user CRUD; ⚠️ mounted from both `backend/app/api/v1/endpoints/users.py` and `backend/app/routers/user.py` |
| `/brands` | brand lookup |
| `/instruments` | instrument CRUD/list; ⚠️ mounted from both endpoint layers |
| `/categories` | category CRUD; ⚠️ mounted from both endpoint layers |
| `/items` | mixed Excel-backed and DB-backed inventory item endpoints |
| `/inventory` | admin inventory, alerts, public catalog, store-catalog sync |
| `/stock-movements` | stock movement list/create |
| `/repairs` | repair/OT CRUD, archive/reactivate, PDFs, intake sheets, notes, photos, components; ⚠️ mounted from both endpoint layers |
| `/repair-statuses` | repair status CRUD |
| `/diagnostic` | brands/models/faults lookup, diagnostic CRUD, quotes board/items/recipients/send/status |
| `/diagnostics` | additional versioned diagnostics endpoints |
| `/quotations` | quotation estimate endpoint |
| `/payments` | payment create/list/detail |
| `/appointments` | appointment create/read/list/update/delete and status filters |
| `/client` | client dashboard, repair timeline/detail/PDF, profile, purchase requests, deposit proof upload |
| `/clients` | admin-facing client CRUD plus device/repair lookups and next code |
| `/devices` | device CRUD |
| `/purchase-requests` | board, CRUD, payment request/confirmation flow |
| `/manuals` | manual CRUD and file upload |
| `/tickets` | ticket CRUD and messages |
| `/invoices` | invoice CRUD, send, void, payments, overdue/summary |
| `/warranties` | warranties, claims, auto-create, maintenance |
| `/analytics` | dashboard, alerts, repairs, revenue, clients, inventory, technicians, warranties, KPI summary |
| `/stats` | versioned stats endpoints |
| `/search` | search endpoint |
| `/uploads` | image uploads |
| `/files` | repair photo download endpoint |
| `/signatures` | signature request, token lookup, submit, cancel, SSE stream |
| `/photo-requests` | photo request create, token lookup, submit |
| `/newsletter` | subscribe/list subscriptions |
| `/contact` | contact create and admin message listing |
| `/imports` | import runtime endpoints |
| `/ai` | AI helper endpoints |
| `/instruments-sync` | instrument sync endpoints |

## 11. Testing

### Exact commands

Frontend unit/integration/store/composable tests:

```bash
npm test
```

Frontend integration-only suite:

```bash
npm run test:integration
```

Frontend coverage attempt:

```bash
npm run test:coverage
```

Frontend end-to-end suite:

```bash
npm run test:e2e
```

Backend test suite:

```bash
cd backend
.venv/bin/python -m pytest -q
```

Headless audit script (sin browser):

```bash
timeout 60 python3 scripts/audit_headless.py
```

### What is actually covered

- `tests/unit/`: 75 archivos (`*.test.*` / `*.spec.*`)
- `tests/integration/`: 2 archivos
- `tests/stores/`: 10 archivos
- `tests/composables/`: 3 archivos
- `tests/e2e/`: 20 archivos (specs + utilidades/fixtures)
- `backend/tests/`: 23 archivos `test*.py`

### Current observed results

Observed in this workspace on 2026-03-05:

- `npm run build`
  - Result: passed

- `cd backend && .venv/bin/python -m pytest -q`
  - Result: passed
  - Summary: `66 passed`, `14 skipped`, `1 warning`

- `timeout 60 python3 scripts/audit_headless.py`
  - Result: completed
  - Summary: `199 checks`, `191 OK`, `8 rotos`
  - Endpoints reportados como rotos:
    - `GET /api/v1/users/` -> `500`
    - `GET /api/v1/users` -> `500`
    - `POST /api/v1/instruments/` -> `500`
    - `POST /api/v1/categories/` -> `500`
    - `POST /api/v1/stock-movements/` -> `500`
    - `GET /api/v1/inventory/low-stock/alerts` -> `ERROR`
    - `GET /api/v1/analytics/repairs` -> `500`
    - `GET /api/v1/analytics/repairs/export` -> `500`

- `PLAYWRIGHT_FRONTEND_PORT=5175 PLAYWRIGHT_API_PORT=8001 PLAYWRIGHT_BASE_URL=http://127.0.0.1:5175 PLAYWRIGHT_API_URL=http://127.0.0.1:8001/api/v1 npm run test:e2e -- tests/e2e/navigation-intent.spec.ts --project=chromium --no-deps`
  - Result: passed
  - Summary: `4 passed`
  - Coverage of this run:
    - `/tienda` exit route (`Volver al inicio`)
    - no-op internal link checks on seed public routes
    - navbar escape links from `/tienda` (`/` and `/calculadoras`)
    - social link targets/hrefs for Instagram/Facebook/WhatsApp

- `npm run test`, `npm run test:coverage`, `npm run test:e2e`
  - ⚠️ Not re-run in this README refresh (last values in prior reports may be stale).

⚠️ The backend run still emits current warnings from:

- `passlib` importing deprecated `crypt`

## 12. Known Technical Debt

| Item | Priority | Status |
| --- | --- | --- |
| Duplicate API layers are mounted together in `backend/app/api/v1/router.py`, causing overlapping prefixes such as `/users`, `/categories`, `/instruments`, and `/repairs`. | High | Open |
| App startup mutates schema outside Alembic via `Base.metadata.create_all()` and `_ensure_*_schema()` patchers in `backend/app/core/database.py`. | High | Open |
| Frontend auth is internally mixed: `src/services/api.ts` is cookie/CSRF-ready, but the actual login flow stores JWTs in `localStorage`, and account deletion is not implemented in backend. | High | Open |
| `.env.example` and `backend/.env.example` mix active settings with legacy placeholders (`CLAUDE_API_KEY`, `MAX_FILE_SIZE`, `UPLOAD_DIR`) not wired into critical runtime paths. | Medium | Open |
| Latest authenticated headless audit (`timeout 60 python3 scripts/audit_headless.py`, 2026-03-05) reports 8 server-side broken checks (`500`/`ERROR`) in users, instruments/categories create, stock-movements, inventory low-stock alerts, and analytics repairs endpoints. | High | Open |
| `scripts/audit_headless.py` streaming skip rule (`'ws' in path`) is broad and currently marks newsletter routes as stream-skipped because `"news"` contains `"ws"`. | Medium | Open |
| Frontend coverage command was not re-run in this refresh (`npm run test:coverage`). | Medium | Pending refresh |
| Signature expiry contract is inconsistent: `SignatureRequestCreate.expires_minutes` defaults to `15`, but `backend/app/routers/signature.py` clamps the real expiry to `5` minutes maximum. | Medium | Open |
| `src/vue/components/articles/DiagnosticWizard.vue` still has `TODO: Generate PDF`; current implementation only generates CSV. | Medium | Open |
| Confirm that roles/permissions are seeded in target DB before relying on `require_permission(...)` outside test mode. | Medium | Pending manual DB verification |

## 13. README Scope Notes (This Refresh)

- This update is additive: it keeps existing architecture/context sections and appends verified inventory/results from current code and runs.
- It documents what is present now without creating new conceptual modules or fictional routes.
- Full "every click in every authenticated/admin flow" validation is not claimed here; current explicit automated confirmation is the focused navigation suite described in Section 11.
