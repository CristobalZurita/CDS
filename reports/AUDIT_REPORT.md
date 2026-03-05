# CDS FULL AUDIT — 2026-03-05

## SUMMARY
| Category | Total | Pass | Fail |
|---|---:|---:|---:|
| Public routes | 20 | 0 | 20 |
| Auth flow | 3 | 0 | 3 |
| All 43 routes | 43 | 0 | 43 |
| Buttons | 14 | 0 | 14 |
| Links | 1 | 0 | 1 |
| Forms | 4 | 0 | 4 |
| API endpoints | 2 | 0 | 2 |
| Assets | 1 | 0 | 1 |
| TOTAL | 88 | 0 | 88 |

## CRITICAL — blocks user from completing a task
ROUTE: GLOBAL (afecta las 88 pruebas: rutas públicas, protegidas, botones, links, formularios, API y assets)  
ACTION: Playwright intenta iniciar navegador para ejecutar cualquier caso  
EXPECTED: Chromium debe iniciar y permitir navegar/validar vistas y endpoints  
ACTUAL: El proceso del navegador termina antes de abrir contexto/página  
ERROR: `Error: browserType.launch: Target page, context or browser has been closed` + `[FATAL:content/browser/sandbox_host_linux.cc:41] Check failed: . shutdown: Operation not permitted (1)`

## NON-CRITICAL — visible but does not block
ROUTE: N/A (ejecución inicial del comando)  
ACTION: lanzamiento de Playwright con flag no soportado  
EXPECTED: comando válido para esta versión de Playwright  
ACTUAL: `--headed=false` no es opción válida en Playwright 1.58.2  
ERROR: comando ajustado y re-ejecutado sin ese flag; el bloqueo real siguió siendo el crash de Chromium

## ROUTES NOT TESTED — requires manual verification
- `/` (entrada raíz; aparece dos veces en router por padre e hijo)
- `/license`
- `/policy`
- `/terminos`
- `/privacidad`
- `/agendar`
- `/cotizador-ia`
- `/calculadoras`
- `/login`
- `/register`
- `/password-reset`
- `/dashboard`
- `/repairs`
- `/repairs/:id`
- `/profile`
- `/admin` (padre + dashboard hijo)
- `/admin/inventory`
- `/admin/inventory/unified`
- `/admin/clients`
- `/admin/repairs`
- `/admin/repairs/:id`
- `/admin/categories`
- `/admin/contact`
- `/admin/newsletter`
- `/admin/appointments`
- `/admin/tickets`
- `/admin/purchase-requests`
- `/admin/archive`
- `/admin/manuals`
- `/signature/:token`
- `/photo-upload/:token`
- `/calc/555`
- `/calc/resistor-color`
- `/calc/smd-capacitor`
- `/calc/smd-resistor`
- `/calc/ohms-law`
- `/calc/temperature`
- `/calc/number-system`
- `/calc/length`
- `/calc/awg`
- `/:pathMatch(.*)*`

Razón común: ninguna ruta alcanzó ejecución funcional porque Chromium no pudo iniciar en este entorno (`sandbox_host_linux.cc:41`).

## API ENDPOINTS STATUS
| Method | Path | Unauth | Auth | Status |
|---|---|---|---|---|
| GET | `/api/v1/brands/` | N/A or 200/404 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/auth/me` | Expected 401 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/items` | N/A or 200/404 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/stats/` | Expected 401 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/stats` | Expected 401 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/stats/quick` | N/A or 200/404 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/stats/repairs` | Expected 401 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/stats/dashboard` | Expected 401 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/users/` | Expected 401 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/users` | Expected 401 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/repairs/` | Expected 401 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/repairs` | Expected 401 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/repairs/archived` | Expected 401 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/instruments/` | N/A or 200/404 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/categories/` | N/A or 200/404 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/stock-movements/` | Expected 401 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/contact/messages` | Expected 401 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/diagnostic/instruments/brands` | N/A or 200/404 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/diagnostic/faults` | N/A or 200/404 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/diagnostic/` | N/A or 200/404 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/payments/` | Expected 401 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/appointments/` | Expected 401 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/appointments/status/pending` | Expected 401 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/appointments/status/confirmed` | Expected 401 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/client/dashboard` | Expected 401 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/client/repairs` | Expected 401 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/client/profile` | Expected 401 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/clients/` | Expected 401 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/clients` | Expected 401 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/clients/next-code` | Expected 401 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/devices/` | Expected 401 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/repair-statuses/` | N/A or 200/404 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/newsletter/subscriptions` | Expected 401 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/tools/` | Expected 401 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/inventory/` | Expected 401 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/inventory/low-stock/alerts` | Expected 401 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/invoices/` | Expected 401 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/invoices/summary` | Expected 401 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/invoices/overdue` | Expected 401 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/warranties/` | Expected 401 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/warranties/expiring-soon` | Expected 401 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/warranties/claims` | Expected 401 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/analytics/dashboard` | Expected 401 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/analytics/alerts` | Expected 401 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/analytics/repairs` | Expected 401 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/analytics/repairs/timeline` | Expected 401 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/analytics/repairs/export` | Expected 401 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/analytics/revenue` | Expected 401 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/analytics/revenue/timeline` | Expected 401 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/analytics/clients` | Expected 401 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/analytics/inventory` | Expected 401 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/analytics/technicians` | Expected 401 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/analytics/warranties` | Expected 401 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/analytics/kpis/summary` | Expected 401 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/search/` | Expected 401 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/tickets/` | Expected 401 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/purchase-requests/` | Expected 401 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/api/v1/manuals/` | Expected 401 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/health` | N/A or 200/404 | Expected <500 | BLOCKED: browser launch failed |
| GET | `/` | N/A or 200/404 | Expected <500 | BLOCKED: browser launch failed |

## BROKEN ASSETS
| Page | Asset | Type | HTTP |
|---|---|---|---|
| N/A (no page navigation executed) | N/A | N/A | BLOCKED (Chromium launch crash) |
