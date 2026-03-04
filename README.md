# Cirujano de Sintetizadores (CDS)

## 1. Project Overview

CDS is a full-stack repair-shop platform for synth intake, repair tracking, inventory, quotes, payments, manuals, warranties, tickets, token-based signatures, and token-based customer photo uploads. The FastAPI backend is broad; the Vue 3 SPA already exposes public, client, and admin routes, but the frontend is still uneven and several modules remain in progress or only partially validated.

## 2. Architecture

```text
Browser
  |
  |  Public SPA routes, /dashboard, /admin/*, /signature/:token, /photo-upload/:token
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

Audited Vue surface in `src/`: 19 non-admin pages, 16 admin pages, 9 calculator modules, 196 Vue components.

| Module | Status | Notes |
| --- | --- | --- |
| Public portal | 🔄 IN PROGRESS | Public pages exist for home/legal pages, calculators, store, quote flow, signature, and photo upload. The current unit suite now covers the public shells/legal/token pages, but most landing content sections in `src/vue/content/sections/*` remain untested. |
| Auth & session | 🔄 IN PROGRESS | `/auth/login`, `/auth/register`, `/auth/me`, `/auth/refresh`, `/auth/logout`, password reset, and optional email 2FA exist. ⚠️ Current SPA stores JWTs in `localStorage`, and `deleteAccount()` is explicitly not implemented in backend. |
| Customer panel | ✅ WORKING | Routes exist for `/dashboard`, `/repairs`, `/repairs/:id`, `/profile`, `/ot-payments`, and `/agendar`. These pages all have active unit tests in `tests/unit/client/`. |
| Admin panel | 🔄 IN PROGRESS | Admin routes exist for inventory, clients, repairs, quotes, categories, contact, newsletter, appointments, tickets, purchase requests, manuals, stats, wizards, and archive. Test coverage is partial: inventory, quotes, manuals, appointments, and some wizard flows are covered, but not the entire admin surface. |
| Entry wizards | 🔄 IN PROGRESS | `WizardClientIntake`, `WizardInventoryItem`, `WizardManualUpload`, `WizardMaterialsUsage`, `WizardPurchaseRequest`, `WizardSignatureRequest`, and `WizardTicket` exist. Only `WizardPurchaseRequest` and `WizardTicket` are covered by active unit tests. |
| Digital signatures | ✅ WORKING | Backend request, lookup, submit, cancel, and SSE endpoints exist; public route `/signature/:token` exists; unit tests cover the page submission flow. ⚠️ Effective expiry is 1-5 minutes, not the schema default of 15. |
| Token photo uploads | ✅ WORKING | Public route `/photo-upload/:token` exists; backend request lookup and upload submission endpoints exist; page unit tests cover success and failure states. |
| Store / purchase requests | 🔄 IN PROGRESS | Public store page, cart widget, purchase-request board, and customer deposit-proof/payment confirmation flow exist. `StorePage` unit coverage, the full frontend coverage run, the full backend pytest run, and the current Playwright integration runner all pass in this workspace on 2026-03-04. |

## 5. Environment Variables

Source audited for this section: root `.env.example`.

### Frontend

- `VITE_API_URL=http://localhost:8000/api/v1`
- `VITE_TURNSTILE_SITE_KEY=REPLACE_WITH_TURNSTILE_SITE_KEY`

### Backend

- `DEBUG=true`
- `ENVIRONMENT=development`
- `DATABASE_URL=sqlite:///./cirujano.db`
- `SECRET_KEY=REPLACE_WITH_RANDOM_64_HEX`
- `JWT_SECRET=REPLACE_WITH_RANDOM_64_HEX`
- `JWT_REFRESH_SECRET=REPLACE_WITH_RANDOM_64_HEX`
- `ALLOW_TOKEN_IN_RESPONSE=false`
- `ENABLE_API_DOCS=false`
- `ENABLE_PUBLIC_UPLOADS=false`
- `CORS_ORIGINS=http://localhost:5173,http://localhost:5174,http://127.0.0.1:5173,http://127.0.0.1:5174,http://0.0.0.0:5173`
- `SMTP_HOST=mail.cirujanodesintetizadores.cl`
- `SMTP_PORT=465`
- `SMTP_USER=not-reply@cirujanodesintetizadores.cl`
- `SMTP_PASSWORD=REPLACE_WITH_SMTP_PASSWORD`
- `SMTP_USE_TLS=false`
- `SMTP_USE_SSL=true`
- `FROM_EMAIL=not-reply@cirujanodesintetizadores.cl`
- `CLAUDE_API_KEY=REPLACE_WITH_CLAUDE_API_KEY`
- `UPLOAD_DIR=./uploads`
- `MAX_FILE_SIZE=10485760`
- `TURNSTILE_SECRET_KEY=REPLACE_WITH_TURNSTILE_SECRET_KEY`
- `TURNSTILE_DISABLE=true`
- `WHATSAPP_TOKEN=REPLACE_WITH_WHATSAPP_TOKEN`
- `WHATSAPP_PHONE_ID=REPLACE_WITH_WHATSAPP_PHONE_ID`
- `WHATSAPP_API_URL=https://graph.facebook.com/v22.0`
- `WHATSAPP_TEMPLATE_NAME=hello_world`
- `WHATSAPP_TEMPLATE_LANG=en_US`

### Production

- `.env.example` does not define production-only keys; it only ships development-oriented sample values.
- A separate `.env.production.example` file exists in the repo, but it is outside the audited input requested for this README section.
- For real production use, the current code requires secure values at minimum for `ENVIRONMENT`, `DATABASE_URL`, `SECRET_KEY`, `JWT_SECRET`, `JWT_REFRESH_SECRET`, `SMTP_PASSWORD`, `TURNSTILE_SECRET_KEY`, `WHATSAPP_TOKEN`, and `WHATSAPP_PHONE_ID`.

⚠️ `.env.example` is not complete relative to active code paths. The app also reads variables such as `PUBLIC_BASE_URL`, `ENABLE_INSTRUMENT_AUTO_SYNC`, `INSTRUMENT_SYNC_ON_STARTUP`, `INSTRUMENT_SYNC_INTERVAL_MINUTES`, `IMAGE_MAX_SIZE`, `REDIS_URL`, `RATE_LIMIT_STORAGE_URI`, and Google Calendar credentials, but they are not present in `.env.example`.

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

Frontend/backend integration runner used by this repo:

```bash
bash scripts/run_tests.sh
```

Backend test suite:

```bash
cd backend
.venv/bin/python -m pytest -q
```

### What is actually covered

- `tests/unit/` currently contains 26 files:
  - admin pages/components: 8
  - client pages: 6
  - auth UI: 2
  - public pages: 4
  - store/cart: 2
  - router guard: 1
  - layout/model helpers: 2
  - generic component spec: 1
- Frontend extra active suites also exist in:
  - `tests/integration/` with 2 files
  - `tests/stores/` with 10 files
  - `tests/composables/` with 3 files
  - `tests/e2e/` with 14 spec/setup files plus auth state and helper files
- Backend active test files currently exist in `backend/tests/` with 23 `test*.py` files for auth, appointments, categories, health, imports, inventory/store sync, OT workflow, payments, uploads, rate limiting, audit logging, purchase requests, security hardening, and integration/auth-guard flows.

### Current observed results

Observed in this workspace on 2026-03-04:

- `npm run build`
  - Result: passed

- `bash scripts/run_tests.sh`
  - Result: passed
  - Backend stage: `13 passed`
  - Playwright stage: `9 passed`
  - ⚠️ The script skips coverage automatically when `pytest-cov` is not installed in `backend/.venv`

- `npm run test:coverage`
  - Result: passed
  - Test files: `41`
  - Tests: `205 passed`
  - Coverage summary from `coverage/coverage-summary.json`:
    - lines/statements: `44.15%`
    - functions: `45.93%`
    - branches: `61.48%`

- `cd backend && .venv/bin/python -m pytest -q`
  - Result: passed
  - Summary: `63 passed`, `14 skipped`, `1 warning`

⚠️ The backend run still emits current warnings from:

- `passlib` importing deprecated `crypt`

## 12. Known Technical Debt

| Item | Priority | Status |
| --- | --- | --- |
| Duplicate API layers are mounted together in `backend/app/api/v1/router.py`, causing overlapping prefixes such as `/users`, `/categories`, `/instruments`, and `/repairs`. | High | Open |
| App startup mutates schema outside Alembic via `Base.metadata.create_all()` and `_ensure_*_schema()` patchers in `backend/app/core/database.py`. | High | Open |
| `.env.example` drifts from active code: it misses variables currently read by the app (`PUBLIC_BASE_URL`, auto-sync flags, `IMAGE_MAX_SIZE`, `REDIS_URL`, etc.) and also includes variables not wired into the active backend path (`CLAUDE_API_KEY`, `MAX_FILE_SIZE`, `UPLOAD_DIR`). | High | Open |
| Frontend auth is internally mixed: `src/services/api.ts` is cookie/CSRF-ready, but the actual login flow stores JWTs in `localStorage`, and account deletion is not implemented in backend. | High | Open |
| Frontend coverage is green but still low at `44.15%` line coverage; many parallel `.ts` wrappers and entire public/calculator/admin surfaces remain unexercised. | High | Open |
| `bash scripts/run_tests.sh` cannot produce backend coverage today because `pytest-cov` is not installed in `backend/.venv`; it falls back to plain `pytest`. | Medium | Open |
| Signature expiry contract is inconsistent: `SignatureRequestCreate.expires_minutes` defaults to `15`, but `backend/app/routers/signature.py` clamps the real expiry to `5` minutes maximum. | Medium | Open |
| `src/vue/components/articles/DiagnosticWizard.vue` still has `TODO: Generate PDF`; current implementation only generates CSV. | Medium | Open |
| Confirm that roles/permissions have actually been seeded in the target database before relying on `require_permission(...)` outside test mode. | Medium | [PLACEHOLDER] |
