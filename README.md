# Cirujano de Sintetizadores (CDS)

Estado auditado: 2026-03-17 · Rama activa: `CDS_ZERO`

---

## 1. Objetivo del proyecto

Plataforma de taller para reparación de sintetizadores e instrumentos electrónicos:

- Ingreso y seguimiento de órdenes de trabajo (OT)
- Gestión de clientes y dispositivos
- Inventario y catálogo de tienda
- Cotizaciones, pagos y comprobantes
- Tickets, manuales, garantías
- Firma digital y carga de fotos por enlace único
- 18 calculadoras electrónicas
- Dashboard de estadísticas y KPIs

---

## 2. Estado actual del sistema

Hoy CDS se entrega y despliega como un monolito modular con estas fuentes de verdad:

- Frontend activo único: `CDS_VUE3_ZERO`
- Backend activo único: `backend/` con FastAPI
- Cotizador público canónico: `/api/v1/quotations/*`
- `diagnostic` queda para compatibilidad diagnóstica/interna y rutas legacy deprecadas
- Media canónica: `/api/v1/media/*` con Cloudinary como fuente real
- `images` queda como compatibilidad legacy deprecada
- Inventario canónico: `/api/v1/inventory/*`
- `/items/*` queda como compatibilidad legacy deprecada
- La ruta futura a microservicios está documentada en `MICROS.md`, pero no es la fase actual de entrega

---

## 3. Estructura del repositorio

```
raiz/
├── CDS_VUE3_ZERO/          ← Frontend Vue 3 (único activo)
├── backend/                ← API FastAPI + SQLAlchemy
└── .github/workflows/      ← CI/CD
```

> El layer legacy (L) fue extraído a `/RESTO/` (carpeta hermana fuera del repo)
> y eliminado de git en `CDS_ZERO` el 2026-03-15.

---

## 4. Frontend — CDS_VUE3_ZERO

### 4.1 Stack

- Vue 3 Composition API + `<script setup>`
- Vue Router 4 · Pinia · Vite 6
- Axios · ApexCharts cargado sólo donde se usa
- CSS puro con tokens `--cds-*` (sin Bootstrap, sin SCSS global)
- Font Awesome 6 Free

### 4.2 Estructura interna

```
CDS_VUE3_ZERO/src/
├── app/AppRoot.vue
├── components/
│   ├── admin/          ← Componentes admin
│   ├── base/           ← BaseInput, BaseButton, BaseSelect…
│   ├── business/       ← PhotoUpload, RepairCard…
│   ├── composite/      ← FormField, DataTable…
│   ├── home/           ← Secciones de la homepage
│   ├── ui/             ← Compatibilidad residual
│   └── widgets/
├── composables/        ← Flujo por dominio/página
├── layouts/
│   ├── MasterLayout.vue       ← Público + cliente
│   └── AdminShellLayout.vue   ← Admin (sidebar + topbar)
├── pages/
│   ├── admin/          ← 20 páginas admin
│   ├── auth/           ← Login, Register, PasswordReset
│   ├── calculators/    ← 18 calculadoras
│   ├── client/         ← Dashboard, Repairs, Profile, OtPayments
│   ├── public/         ← Home, Store, Cotizador, Calculadoras…
│   └── token/          ← Signature, PhotoUpload
├── router/routes/      ← Rutas por dominio
├── services/api.js     ← Cliente Axios (Bearer + CSRF automático)
├── stores/             ← auth.js · shopCart.js
└── styles/
    ├── tokens.css      ← Variables --cds-* (única fuente de verdad)
    ├── fonts.css
    ├── typography.css
    ├── main.css
    ├── utilities.css
    └── layout.css      ← Compatibilidad / residuo controlado
```

### 4.3 Rutas frontend

#### Públicas

| Ruta | Página |
|------|--------|
| `/` | HomePage |
| `/cotizador` | CotizadorPage (wizard + modo instrumento no encontrado) |
| `/calculadoras` | CalculatorsPage |
| `/tienda` | StorePage |
| `/agendar` | SchedulePage |
| `/simulador` | SimulatorPage |
| `/license` · `/policy` · `/terminos` · `/privacidad` | Páginas legales |

#### Autenticación

| Ruta | Página |
|------|--------|
| `/login` | LoginPage |
| `/register` | RegisterPage |
| `/password-reset` | PasswordResetPage |

#### Cliente autenticado

| Ruta | Página |
|------|--------|
| `/dashboard` | DashboardPage |
| `/repairs` | RepairsPage |
| `/repairs/:id` | RepairDetailPage |
| `/ot-payments` | OtPaymentsPage |
| `/profile` | ProfilePage |

#### Admin (20 páginas)

| Ruta | Página |
|------|--------|
| `/admin` | AdminDashboard |
| `/admin/clients` | ClientsPage |
| `/admin/repairs` | RepairsAdminPage |
| `/admin/repairs/:id` | RepairDetailAdminPage |
| `/admin/intake` | IntakeWizardPage |
| `/admin/inventory` | InventoryPage |
| `/admin/inventory/unified` | InventoryUnifiedPage |
| `/admin/quotes` | QuotesAdminPage |
| `/admin/stats` | StatsPage (KPIs + 3 gráficos ApexCharts) |
| `/admin/categories` | CategoriesPage |
| `/admin/contact` | ContactMessagesPage |
| `/admin/newsletter` | NewsletterSubscriptionsPage |
| `/admin/appointments` | AppointmentsPage |
| `/admin/tickets` | TicketsPage |
| `/admin/purchase-requests` | PurchaseRequestsPage |
| `/admin/manuals` | ManualsPage |
| `/admin/wizards` | WizardsPage |
| `/admin/archive` | ArchivePage |
| `/admin/media` | MediaPage |
| `/admin/leads` | LeadsAdminPage |

#### Por token (sin auth)

| Ruta | Página |
|------|--------|
| `/signature/:token` | SignaturePage |
| `/photo-upload/:token` | PhotoUploadPage |

#### Calculadoras (18)

`/calc/555` · `/calc/resistor-color` · `/calc/smd-capacitor` · `/calc/smd-resistor` · `/calc/ohms-law` · `/calc/temperature` · `/calc/number-system` · `/calc/length` · `/calc/awg` · `/calc/cd40106` · `/calc/current-divider` · `/calc/led-series-resistor` · `/calc/low-high-pass-filter` · `/calc/rc-time-constant` · `/calc/reactance` · `/calc/series-parallel-capacitor` · `/calc/series-parallel-resistor` · `/calc/voltage-divider`

---

## 5. Backend — FastAPI

### 5.1 Stack

- FastAPI 0.104.1 · Uvicorn 0.24.0
- SQLAlchemy 2.0.23 · Alembic 1.12.1
- Pydantic 2.5.0
- JWT (python-jose) · bcrypt (passlib)
- Cloudinary 1.38.0
- SlowAPI 0.1.5 (rate limiting)
- SDK opcional: `transbank-sdk` o `mercadopago` (según `PAYMENT_GATEWAY`)

### 5.2 Estructura

```
backend/
├── app/
│   ├── main.py              ← FastAPI app + CSRF middleware
│   ├── core/
│   │   ├── config.py        ← Settings desde .env
│   │   ├── database.py
│   │   ├── dependencies.py  ← require_permission, get_current_user
│   │   └── security.py
│   ├── models/              ← SQLAlchemy models
│   ├── routers/             ← Routers por dominio
│   ├── services/            ← Lógica de negocio
│   ├── schemas/             ← Pydantic schemas
│   └── data/                ← brands.json · instruments.json · faults.json
├── tests/                   ← 30 archivos de test (pytest)
├── alembic/                 ← Migraciones
├── requirements.txt
└── .env.example
```

### 5.3 Grupos de API (`/api/v1/`)

```
analytics          KPIs, dashboard, timelines, reportes
appointments       Citas
ai                 Análisis experimental / compatibilidad deprecada
auth               Login, register, JWT refresh, 2FA
brands             Marcas de instrumentos
categories         Categorías de inventario
client             Portal cliente autenticado (servido por client_portal)
clients            CRUD admin de clientes (/clients/*)
contact            Formulario de contacto público
devices            Dispositivos de clientes
diagnostic         Compatibilidad diagnóstica e interna (deprecated)
files              Archivos protegidos
images             Compatibilidad Cloudinary legacy (deprecated)
imports            Importación de datos
instruments        Catálogo de instrumentos
inventory          Inventario y productos (canónico; /items deprecated)
invoices           Facturación
leads              Leads del cotizador público
manuals            Manuales técnicos
media              Gestión canónica de assets y bindings Cloudinary
newsletter         Suscripciones
payment-gateway    Transbank Webpay Plus / MercadoPago
payments           CRUD de pagos
photo-requests     Solicitudes de foto por enlace
purchase-requests  Solicitudes de compra
quotation          Cotizador público canónico + quotes admin
repair-statuses    Estados de OT
repairs            Órdenes de trabajo (core)
search             Búsqueda global
signatures         Firma digital por enlace
stats              Estadísticas básicas
stock-movements    Movimientos de stock
tickets            Tickets de soporte
tools              Herramientas internas
uploads            Subida de archivos
users              Gestión de usuarios
warranties         Garantías
webhooks           WhatsApp Cloud API (verify + receive)
```

### 5.4 Contratos canónicos hoy

- Cotizador público: `POST /api/v1/quotations/estimate`
- Gestión de quotes admin: `/api/v1/quotations/quotes/*`
- Media dinámica: `/api/v1/media/assets` y `/api/v1/media/bindings`
- Upload firmado y helpers de media: `/api/v1/uploads/*`
- Portal cliente: `/api/v1/client/*`
- Inventario activo: `/api/v1/inventory/*`

Compatibilidades que siguen vivas, pero ya no son la capa primaria:

- `/api/v1/diagnostic/*`
- `/api/v1/images/*`
- `/api/v1/items/*`
- `/api/v1/ai/analyze`

### 5.5 KPIs disponibles en `/api/v1/analytics/`

| Endpoint | Qué retorna |
|----------|-------------|
| `/kpis/summary` | Resumen consolidado |
| `/kpis/turnaround` | Promedio/min/max días por OT |
| `/kpis/overdue` | OTs activas vencidas |
| `/kpis/lead-conversion` | Tasa leads → reparaciones |
| `/kpis/top-models` | Modelos más reparados |
| `/kpis/client-return` | Tasa de retorno de clientes |
| `/repairs/timeline` | OTs últimos N días |
| `/revenue/timeline` | Ingresos últimos N meses |

---

## 6. Ejecución local

### Frontend

```bash
cd CDS_VUE3_ZERO
npm install
npm run dev
# http://localhost:5174
npm run build
```

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
# http://localhost:8000
# Docs: http://localhost:8000/docs (solo si ENABLE_API_DOCS=true)
```

### Variables de entorno

```bash
cp backend/.env.example backend/.env
# Editar con credenciales reales
```

Variables clave:

| Variable | Descripción |
|----------|-------------|
| `JWT_SECRET` / `JWT_REFRESH_SECRET` | Secretos JWT |
| `CLOUDINARY_URL` | CDN de imágenes |
| `WHATSAPP_TOKEN` / `WHATSAPP_PHONE_ID` | Meta Cloud API |
| `WHATSAPP_WEBHOOK_VERIFY_TOKEN` | Verificación webhook Meta |
| `PAYMENT_GATEWAY` | `transbank` o `mercadopago` |
| `TRANSBANK_COMMERCE_CODE` / `TRANSBANK_API_KEY` | Transbank |
| `MERCADOPAGO_ACCESS_TOKEN` | MercadoPago |
| `VITE_GOOGLE_MAPS_API_KEY` | Places Autocomplete |
| `ENFORCE_CSRF` | `true` en producción |

---

## 7. Tests

### Backend (pytest)

```bash
cd backend
pytest tests/ --verbose
```

30 archivos de test incluyen:
- Auth flows, guards de permisos
- OT workflow, pagos, inventario
- WhatsApp webhook, payment gateway
- Router deduplicación, client_portal module
- Seguridad (JWT secrets, CSRF, rate limiting)

### Frontend E2E (Playwright)

```bash
cd CDS_VUE3_ZERO
npm run test:e2e
```

---

## 8. CI/CD

| Workflow | Propósito |
|----------|-----------|
| `ci.yml` | Build frontend ZERO + validaciones |
| `tests.yml` | Tests frontend + backend en paralelo |
| `secret-scan.yml` | Escaneo de secretos (detect-secrets) |
| `security.yml` | Validaciones de seguridad |
| `sync-instruments.yml` | Sincronización manual de instrumentos |

---

## 9. Entrega y crecimiento

- La entrega inmediata es el sistema real desplegado como monolito modular
- El dominio/host real tiene prioridad frente a demos en localhost
- La evolución a microservicios existe, pero está diferida y documentada en `MICROS.md`
- No se deben abrir microservicios antes de cerrar y estabilizar el monolito actual

---

## 10. Filosofía del proyecto

- **Aditivo** — agregar, no eliminar funcionalidad existente
- **Deconstructivo** — desarmar para entender, reconstruir limpio
- **Sin inventar** — usar lo que existe antes de crear
- **Leer todo** — entender el contrato antes de cambiar
- **No commit sin autorización explícita**

---

*README actualizado: 2026-03-17 · CDS_ZERO*
