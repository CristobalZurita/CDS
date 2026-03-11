# Cirujano de Sintetizadores (CDS)

Estado auditado: 2026-03-11

Este README refleja el estado real del repositorio en este momento (frontend Vue 3 ZERO + backend FastAPI), usando como fuente el código actual y no documentos históricos.

---

## 1. Objetivo del proyecto

CDS es una plataforma de taller para:

- Ingreso y seguimiento de reparaciones
- Gestión de clientes y dispositivos
- Inventario y catálogo tienda
- Cotizaciones, pagos y comprobantes
- Tickets, manuales, garantías
- Firma digital por enlace y carga de fotos por enlace
- Calculadoras electrónicas (18 herramientas)

---

## 2. Estructura real del repositorio

```
raiz/
├── CDS_VUE3_ZERO/          ← Frontend Vue 3 principal (ZERO)
├── backend/                ← API FastAPI
├── src/                    ← Frontend LEGACY (Vue 3 original)
├── tests/                  ← Pruebas frontend/integración
├── backend/tests/          ← Pruebas backend
├── .github/workflows/      ← CI/CD y seguridad
├── database/               ← SQL y seeds
├── scripts/                ← Utilidades de soporte
├── public/                 ← Assets públicos LEGACY
├── docs/                   ← Documentación adicional
└── uploads/                ← Archivos subidos localmente
```

### 2.1 Frontend CDS_VUE3_ZERO (Principal)

Condo auditado:

- **Componentes Vue**: 90 (`CDS_VUE3_ZERO/src/components`)
- **Páginas Vue totales**: 56 (`CDS_VUE3_ZERO/src/pages`)
- **Páginas admin**: 18 (`CDS_VUE3_ZERO/src/pages/admin`)
- **Layouts**: 2 (`MasterLayout`, `AdminShellLayout`)
- **Composables**: 57 (`CDS_VUE3_ZERO/src/composables`)
- **Stores**: 2 (`auth.js`, `shopCart.js`)

### 2.2 Frontend LEGACY (Referencia)

- **Componentes Vue**: 127 (`src/vue/components`)
- **Páginas Vue**: 36 (`src/vue/content/pages`)
- **Módulos calculadora**: 9 (`src/modules/*`)

El LEGACY se mantiene como referencia pero **no está en uso activo**. El desarrollo actual ocurre en ZERO.

---

## 3. Frontend CDS_VUE3_ZERO (Actual)

### 3.1 Stack principal

- Vue 3.2.47 + Vue Router 4.2.4 + Pinia 3.0.4
- Vite 6.2.5
- Axios 1.13.2
- CSS puro con tokens (sin Bootstrap en ZERO)
- Sass 1.62.1 (solo para componentes específicos)

### 3.2 Entrada principal

- `CDS_VUE3_ZERO/src/main.js`
- Carga `AppRoot.vue` con `<router-view />` puro
- Importa estilos desde `src/styles/main.css`

### 3.3 Estructura de carpetas ZERO

```
CDS_VUE3_ZERO/src/
├── app/
│   └── AppRoot.vue              ← Root component
├── components/
│   ├── admin/                   ← Componentes admin (8)
│   ├── auth/                    ← Formularios de auth
│   ├── base/                    ← Componentes base
│   ├── business/                ← Componentes de negocio
│   ├── composite/               ← Componentes compuestos
│   ├── ui/                      ← UI Kit (BaseButton, BaseInput)
│   └── widgets/                 ← Widgets reutilizables
├── composables/                 ← 57 composables
├── layouts/
│   ├── MasterLayout.vue         ← Layout público/cliente
│   └── AdminShellLayout.vue     ← Layout admin (sidebar + topbar)
├── pages/
│   ├── admin/                   ← 18 páginas admin
│   ├── auth/                    ← Login, Register, PasswordReset
│   ├── calculators/             ← 18 calculadoras
│   ├── client/                  ← Dashboard, Repairs, Profile
│   ├── public/                  ← Home, Store, CotizadorIA
│   └── token/                   ← Signature, PhotoUpload
├── router/
│   ├── index.js                 ← Configuración principal
│   └── routes/                  ← Módulos por dominio
├── services/
│   └── api.js                   ← Cliente Axios
├── stores/
│   ├── auth.js                  ← Store de autenticación
│   └── shopCart.js              ← Store del carrito
└── styles/
    ├── main.css                 ← Orquestador de estilos
    ├── tokens.css               ← Variables CSS globales
    ├── typography.css           ← Escalas tipográficas
    ├── layout.css               ← Layout utilities
    └── utilities.css            ← Utilidades CSS
```

### 3.4 Ruteo fuente de verdad

- `CDS_VUE3_ZERO/src/router/index.js`
- Guards: auth, admin, guest
- 55+ rutas declaradas

### 3.5 Inventario de rutas frontend

#### Públicas (11)

| Ruta | Página | Descripción |
|------|--------|-------------|
| `/` | HomePage | Landing principal |
| `/license` | LicensePage | Licencias de uso |
| `/policy` | PolicyPage | Políticas |
| `/terminos` | TermsPage | Términos de servicio |
| `/privacidad` | PrivacyPage | Privacidad |
| `/agendar` | SchedulePage | Agendar cita (requiere auth) |
| `/cotizador-ia` | CotizadorIAPage | Cotizador con IA |
| `/calculadoras` | CalculatorsPage | Índice de calculadoras |
| `/tienda` | StorePage | Tienda de instrumentos |
| `/simulador` | SimulatorPage | Simulador de circuitos |
| `/registro` | RegisterPage | Registro de usuarios |

#### Autenticación (3)

| Ruta | Página |
|------|--------|
| `/login` | LoginPage |
| `/register` | RegisterPage |
| `/password-reset` | PasswordResetPage |

#### Cliente autenticado (5)

| Ruta | Página |
|------|--------|
| `/dashboard` | DashboardPage |
| `/ot-payments` | OtPaymentsPage |
| `/repairs` | RepairsPage |
| `/repairs/:id` | RepairDetailPage |
| `/profile` | ProfilePage |

#### Admin (18 páginas)

| Ruta | Página | Descripción |
|------|--------|-------------|
| `/admin` | AdminDashboard | Dashboard principal |
| `/admin/inventory` | InventoryPage | Gestión de inventario |
| `/admin/inventory/unified` | InventoryUnifiedPage | Vista unificada |
| `/admin/clients` | ClientsPage | Gestión de clientes |
| `/admin/repairs` | RepairsAdminPage | Gestión de reparaciones |
| `/admin/repairs/:id` | RepairDetailAdminPage | Detalle de reparación |
| `/admin/quotes` | QuotesAdminPage | Cotizaciones |
| `/admin/categories` | CategoriesPage | Categorías |
| `/admin/contact` | ContactMessagesPage | Mensajes de contacto |
| `/admin/newsletter` | NewsletterSubscriptionsPage | Suscripciones |
| `/admin/appointments` | AppointmentsPage | Citas |
| `/admin/tickets` | TicketsPage | Tickets de soporte |
| `/admin/purchase-requests` | PurchaseRequestsPage | Solicitudes de compra |
| `/admin/manuals` | ManualsPage | Manuales técnicos |
| `/admin/stats` | StatsPage | Estadísticas avanzadas |
| `/admin/wizards` | WizardsPage | Wizards de gestión |
| `/admin/intake` | IntakeWizardPage | Wizard de ingreso |
| `/admin/archive` | ArchivePage | Archivo de reparaciones |

#### Rutas por token (2)

| Ruta | Página |
|------|--------|
| `/signature/:token` | SignaturePage |
| `/photo-upload/:token` | PhotoUploadPage |

#### Calculadoras (18)

| Ruta | Calculadora |
|------|-------------|
| `/calc/555` | Timer 555 |
| `/calc/resistor-color` | Código de colores resistencias |
| `/calc/smd-capacitor` | Códigos SMD capacitores |
| `/calc/smd-resistor` | Códigos SMD resistencias |
| `/calc/ohms-law` | Ley de Ohm |
| `/calc/temperature` | Conversión de temperatura |
| `/calc/number-system` | Sistemas numéricos |
| `/calc/length` | Conversión de longitud |
| `/calc/awg` | Calibres AWG |
| `/calc/cd40106` | CD40106 Schmitt Trigger |
| `/calc/current-divider` | Divisor de corriente |
| `/calc/led-series-resistor` | Resistencia LED serie |
| `/calc/low-high-pass-filter` | Filtros paso bajo/alto |
| `/calc/rc-time-constant` | Constante de tiempo RC |
| `/calc/reactance` | Reactancia |
| `/calc/series-parallel-capacitor` | Capacitores serie/paralelo |
| `/calc/series-parallel-resistor` | Resistencias serie/paralelo |
| `/calc/voltage-divider` | Divisor de voltaje |

#### Fallback

- `/:pathMatch(.*)*` → 404

---

## 4. Backend actual

### 4.1 Stack principal

- FastAPI 0.104.1
- Uvicorn 0.24.0
- SQLAlchemy 2.0.23 + Alembic 1.12.1
- Pydantic 2.5.0
- JWT con python-jose 3.5.0
- Passlib con bcrypt 1.7.4
- Cloudinary 1.38.0 (para imágenes)
- Pandas 2.3.3 + OpenPyXL 3.1.5 (lectura Excel)
- SlowAPI 0.1.5 (rate limiting)

### 4.2 Aplicación principal

- `backend/app/main.py`
- Prefijo API: `/api/v1`
- Endpoint de salud: `/health`

### 4.3 Inventario auditado del backend

- **249 rutas HTTP** registradas
- **181 paths** OpenAPI
- **35 grupos** de rutas bajo `/api/v1/*`

### 4.4 Grupos de API

```
/api/v1/
├── ai                    ← Endpoints de IA/ML
├── analytics             ← Dashboard y métricas
├── appointments          ← Citas
├── auth                  ← Autenticación JWT
├── brands                ← Marcas de instrumentos
├── categories            ← Categorías de inventario
├── client                ← Endpoints de cliente
├── clients               ← Gestión de clientes
├── contact               ← Formulario de contacto
├── devices               ← Dispositivos de clientes
├── diagnostic            ← Diagnósticos y cotizaciones
├── files                 ← Gestión de archivos
├── imports               ← Importación de datos
├── instruments           ← Instrumentos/catalogación
├── instruments-sync      ← Sincronización
├── inventory             ← Inventario
├── invoices              ← Facturación
├── items                 ← Items genéricos
├── manuals               ← Manuales técnicos
├── newsletter            ← Suscripciones newsletter
├── payments              ← Pagos
├── photo-requests        ← Solicitudes de fotos
├── purchase-requests     ← Solicitudes de compra
├── quotations            ← Cotizaciones
├── repair-statuses       ← Estados de reparación
├── repairs               ← Reparaciones (core)
├── search                ← Búsqueda global
├── signatures            │─ Firmas digitales
├── stats                 ← Estadísticas
├── stock-movements       ← Movimientos de stock
├── tickets               ← Tickets de soporte
├── tools                 ← Herramientas
├── uploads               │─ Subida de archivos
├── users                 ← Gestión de usuarios
└── warranties            ← Garantías
```

### 4.5 Servicios de imágenes (Cloudinary)

El backend integra Cloudinary para gestión de imágenes:

- **518 imágenes** catalogadas en Cloudinary
- Endpoint de resolución: `/api/v1/images/resolve`
- Endpoint batch: `/api/v1/images/resolve-batch`
- Mapeo automático de rutas locales a URLs CDN
- Configuración via variable de entorno `CLOUDINARY_URL`

---

## 5. Ejecución local

### 5.1 Frontend ZERO

```bash
cd CDS_VUE3_ZERO
npm install
npm run dev
# Servidor en http://localhost:5174
```

### 5.2 Backend

```bash
cd backend
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
# API en http://localhost:8000
# Documentación: http://localhost:8000/docs
```

### 5.3 Variables de entorno

Archivos de plantilla disponibles (copiar y configurar):

- `.env.example` → `.env` (frontend LEGACY)
- `backend/.env.example` → `backend/.env` (backend)
- `.env.production.example` → configuración producción
- `.env.docker` → configuración Docker

**Nota**: No subir archivos `.env` con valores reales al repositorio.

---

## 6. Pruebas y validación

### 6.1 Frontend

```bash
# Linting
npm run lint

# Tests unitarios
npm run test -- --run

# Tests de integración
npm run test:integration

# Tests E2E con Playwright
npm run test:e2e
npm run test:e2e:headed
```

### 6.2 Backend

```bash
cd backend
ENVIRONMENT=testing DATABASE_URL=sqlite:///./test_ci.db pytest tests/ --verbose
```

### 6.3 Build producción

```bash
# Frontend ZERO
cd CDS_VUE3_ZERO
npm run build

# Frontend LEGACY (si aplica)
npm run build
```

---

## 7. CI/CD actual

### 7.1 Workflows activos

| Workflow | Archivo | Propósito |
|----------|---------|-----------|
| Tests | `.github/workflows/tests.yml` | Tests frontend/backend |
| CI | `.github/workflows/ci.yml` | Build y validaciones |
| Deploy | `.github/workflows/deploy.yml` | Despliegue |
| Secret Scan | `.github/workflows/secret-scan.yml` | Escaneo de secretos |
| Security | `.github/workflows/security.yml` | Validaciones de seguridad |

### 7.2 Validaciones relevantes

- Tests frontend/backend/integración
- Build frontend y build Docker condicionado
- Escaneo de secretos con baseline (`.secrets.baseline`)
- Control de artefactos locales/sensibles trackeados

---

## 8. Higiene de secretos y artefactos

### 8.1 Reglas del repositorio

- No subir credenciales reales
- No subir bases locales SQLite, logs, uploads ni artefactos de test
- Usar archivos de plantilla para configuración local/producción

### 8.2 Archivos protegidos por `.gitignore`

```
.env
.env.local
*.db
*.log
uploads/
node_modules/
dist/
__pycache__/
```

### 8.3 Política de documentación

- Este README no incluye claves, tokens ni contraseñas
- Este README no incluye ejemplos con credenciales embebidas

---

## 9. Criterio de cambios (Filosofía del proyecto)

Se mantiene el enfoque del proyecto:

- **Aditivo**: Agregar, no quitar
- **Deconstructivo**: Desarmar para armar algo nuevo
- **No destructivo**: No eliminar funcionalidad existente
- **Reutilizar**: Usar lo existente antes de crear
- **Sin inventar**: Evitar variables y comportamiento implícito
- **Leer todo**: Entender antes de cambiar

---

## 10. Estado de migración (LEGACY → ZERO)

### 10.1 Completado ✅

| Componente | Estado |
|------------|--------|
| Infraestructura base | 100% Vue 3 + Vite + Pinia |
| Router y guards | 100% Funcional |
| Layouts | MasterLayout + AdminShellLayout |
| Páginas públicas | 11/11 Completas |
| Páginas auth | 3/3 Completas |
| Páginas cliente | 5/5 Completas |
| Páginas admin | 18/18 Completas |
| Calculadoras | 18/18 Completas |
| Páginas token | 2/2 Completas |
| Cloudinary | 518 imágenes mapeadas |
| UI Admin escalada | 45% más grande para legibilidad |

### 10.2 Diferencias arquitectónicas

| Aspecto | LEGACY | ZERO |
|---------|--------|------|
| Componentes Vue | 198 | 90 |
| Composables | Mezclados | 57 separados |
| Stores | Monolíticos | 2 especializados |
| Estilos | SCSS global (8k líneas) | CSS puro con tokens |
| Bootstrap | Sí | No |
| Imágenes | Assets locales (~25MB) | Cloudinary CDN |
| Layout admin | 4 componentes | 1 AdminShellLayout |

### 10.3 Funcionalidades nuevas en ZERO

- **+8 calculadoras electrónicas** (cd40106, current-divider, led-series-resistor, etc.)
- **Sistema Cloudinary** para imágenes optimizadas
- **IntakeWizardPage** consolidada
- **SimulatorPage** (simulador de circuitos)
- **InventoryUnifiedPage**
- **Sistema de usuarios admin** completo
- **Más endpoints de cliente** (`/client/*`)

---

## 11. Documentación adicional

- `MIGRACION_A_VUE.md` → Plan de migración (estado histórico)
- `MIGRACION_VUE_REAL.md` → Proceso de migración detallado
- `ESTRATEGIA_SANITIZACION.md` → Estrategia de sanitización
- `AUDITORIA_PROBLEMAS.md` → Auditoría de problemas conocidos

---

*README actualizado: 2026-03-11*
*Versión: 3.0.0 (ZERO)*
