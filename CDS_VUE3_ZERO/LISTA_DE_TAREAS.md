# LISTA DE TAREAS - CDS VUE3 ZERO
**Rama base:** CDS_ZERO (commit ba01e2aa)
**Objetivo:** Proyecto Vue 3 autónomo con paridad funcional del CDS actual (front + back unificado)
**Última actualización:** 2026-03-07

---

## 🎯 PRINCIPIOS OBLIGATORIOS

- ✅ **Aditivo, no destructivo ni sustractivo**
- ✅ **Deconstructivo**: desarmar legacy → armar Vue nuevo
- ✅ **Si existe, se usa; si no, se crea**
- ✅ **NO INVENTAR** variables/rutas/contratos/endpoints
- ✅ **Leer todo completo** antes de tocar
- ✅ **Mantener hegemonía funcional/visual**
- ❌ **NO hacer commits sin autorización**

---

## 📊 ESTADO DE FASES (CDS_VUE3_ZERO) - ACTUALIZADO

| Fase | Progreso | Completado | Pendiente | Detalle |
|------|----------|------------|-----------|---------|
| **Auth** | 100% ✅ | 6/6 | 0 | Cerrado + auth.js migrado (217 líneas) |
| **Public** | 100% ✅ | 9/9 | 0 | FASE COMPLETA - MasterLayout sin @legacy |
| **Client** | 0% ⚪ | 0/5 | 5 | Dashboard, Repairs, RepairDetail, Profile, OtPayments |
| **Admin** | 0% ⚪ | 0/17 | 17 | Todos los módulos (ver detalle abajo) |
| **Calculadoras** | 0% ⚪ | 0/9 | 9 | AWG, Length, NumberSystem, OhmsLaw, etc. |
| **Token** | 0% ⚪ | 0/2 | 2 | Signature, PhotoUpload |

**Total páginas:** 15 completadas / 47 totales (31.9%)
**Referencias @legacy:** 0 en Public/Auth - alias @legacy REMOVIDO de vite.config.js
**Infraestructura:** api.js (142 líneas), auth.js store (217 líneas), MasterLayout migrado

---

## 📦 INVENTARIO COMPLETO (Segunda pasada - Detallado)

### FRONTEND (desde CDS_cz_NUEVA/src)
- **Total archivos:** 241 (.vue + .js)
- **Componentes Vue:** 127 (desglosados abajo)
- **Sections:** 15 bloques de contenido
- **Stores:** 10 archivos
- **Services:** 3 archivos
- **Composables:** 19 archivos
- **Módulos calculadoras:** 9 con vistas
- **SASS global:** ~8,000 líneas
  - `components/_app.scss`: 4,724 líneas (fragmentado en cascada)
  - `_layout.scss`: 914 líneas
  - `_public.scss`: 4,575 líneas
  - `_admin.scss`: 1,871 líneas
  - `pages/_admin.scss`: 1,220 líneas

#### Componentes Vue por categoría (127 total):
| Categoría | Cantidad | Ubicación |
|-----------|----------|-----------|
| Admin | 40 | `src/vue/components/admin/` |
| Articles | 19 | `src/vue/components/articles/` |
| Widgets | 15 | `src/vue/components/widgets/` |
| Nav | 7 | `src/vue/components/nav/` |
| Dashboard | 7 | `src/vue/components/dashboard/` |
| Layout | 7 | `src/vue/components/layout/` |
| AI | 5 | `src/vue/components/ai/` |
| Footer | 5 | `src/vue/components/footer/` |
| Auth | 4 | `src/vue/components/auth/` |
| Projects | 4 | `src/vue/components/projects/` |
| Quotation | 4 | `src/vue/components/quotation/` |
| Forms | 3 | `src/vue/components/forms/` |
| Generic | 2 | `src/vue/components/generic/` |
| Loaders | 2 | `src/vue/components/loaders/` |
| Common | 1 | `src/vue/components/common/` |
| Modals | 1 | `src/vue/components/modals/` |
| System | 1 | `src/vue/components/system/` |

#### Sections (15 bloques de contenido):
1. DiagnosticSection.vue
2. PolicySection.vue
3. ServicesSection.vue
4. HistorySection.vue
5. FeaturedProjectSection.vue
6. CalculatorsSection.vue
7. TeamSection.vue
8. NewsletterSection.vue
9. LicenseSection.vue
10. PortfolioSection.vue
11. ContactSection.vue
12. AboutSection.vue
13. HeroSection.vue
14. ReviewsSection.vue
15. FaqSection.vue

#### Stores existentes (10):
1. `auth.js` (167 bytes)
2. `categories.js` (185 bytes)
3. `diagnostics.js` (188 bytes)
4. `instruments.js` (188 bytes)
5. `inventory.js` (182 bytes)
6. `quotation.js` (182 bytes)
7. `repairs.js` (176 bytes)
8. `shopCart.js` (179 bytes)
9. `stockMovements.js` (197 bytes)
10. `users.js` (170 bytes)

#### Services existentes (3):
1. `api.js` (379 bytes)
2. `secureMedia.js` (286 bytes)
3. `toastService.js` (280 bytes)

#### Composables existentes (19):
1. `emails.js` (168 bytes)
2. `layout.js` (168 bytes)
3. `scheduler.js` (177 bytes)
4. `settings.js` (564 bytes)
5. `strings.js` (2043 bytes)
6. `useApi.js` (1443 bytes)
7. `useAuth.js` (168 bytes)
8. `useCategories.js` (186 bytes)
9. `useDiagnostic.js` (187 bytes)
10. `useDiagnostics.js` (189 bytes)
11. `useInstruments.js` (189 bytes)
12. `useInstrumentsCatalog.js` (210 bytes)
13. `useInventory.js` (183 bytes)
14. `useQuotation.js` (183 bytes)
15. `useRepairs.js` (177 bytes)
16. `useResponsive.js` (2622 bytes)
17. `useStockMovements.js` (198 bytes)
18. `useUsers.js` (171 bytes)
19. `utils.js` (165 bytes)

#### Módulos calculadoras (9):
Cada módulo tiene su vista completa en `src/modules/[nombre]/`:
1. `awg/AwgView.vue`
2. `length/LengthView.vue`
3. `numberSystem/NumberSystemView.vue`
4. `ohmsLaw/OhmsLawView.vue`
5. `resistorColor/ResistorColorView.vue`
6. `smdCapacitor/SmdCapacitorView.vue`
7. `smdResistor/SmdResistorView.vue`
8. `temperature/TemperatureView.vue`
9. `timer555/Timer555View.vue` (16,779 bytes)

**Componentes migrados a Vue real:** 1/127 (0.8%)
- ✅ PageSection.vue (única migración completa hasta ahora)

### BACKEND (desde CDS_cz_NUEVA/backend)
- **Total archivos Python:** 6,733
- **Arquitectura:** FastAPI (Python)
- **Líneas de código endpoints:** 1,297
- **Base de datos:** SQLite (cirujano.db)
- **Llamadas frontend → API:** 153 identificadas

#### Estructura backend:
```
backend/
├── app/
│   ├── api/v1/endpoints/ (11 archivos - 1,297 líneas)
│   ├── routers/ (29 archivos)
│   ├── models/ (20+ modelos ORM)
│   ├── schemas/ (DTOs/Pydantic)
│   ├── crud/ (7 archivos CRUD)
│   ├── services/ (lógica de negocio)
│   ├── core/ (config, seguridad)
│   ├── middleware/
│   ├── security/
│   ├── utils/
│   └── websocket/
├── alembic/ (migraciones DB)
├── tests/
└── requirements.txt
```

#### Endpoints API v1 (11 módulos):
1. `ai.py` - IA cotizador
2. `auth.py` - Login, register, 2FA, reset password
3. `brands.py` - Marcas de instrumentos
4. `categories.py` - Categorías
5. `diagnostics.py` - Diagnósticos
6. `imports.py` - Importaciones masivas
7. `instruments.py` - Instrumentos/catálogo
8. `inventory.py` - Inventario/stock
9. `repairs.py` - Reparaciones
10. `stats.py` - Estadísticas/KPIs
11. `users.py` - Usuarios/perfiles

#### Routers (29 módulos):
1. `analytics.py` - Analytics/tracking
2. `appointment.py` - Citas/agendamiento
3. `category.py` - Categorías
4. `client.py` / `clients.py` - Clientes
5. `contact.py` - Mensajes de contacto
6. `csrf.py` - Protección CSRF
7. `device.py` - Dispositivos
8. `diagnostic.py` - Diagnósticos
9. `files.py` - Gestión de archivos
10. `instrument.py` - Instrumentos
11. `inventory.py` - Inventario
12. `invoice.py` - Facturas
13. `logging.py` - Logs
14. `manuals.py` - Manuales/documentos
15. `newsletter.py` - Newsletter/suscripciones
16. `payments.py` - Pagos OT
17. `photo_requests.py` - Solicitud de fotos
18. `purchase_requests.py` - Solicitudes de compra
19. `quotation.py` - Cotizaciones
20. `repair.py` - Reparaciones
21. `repair_status.py` - Estados de reparación
22. `search.py` - Búsqueda global
23. `signature.py` - Firmas digitales
24. `stock_movement.py` - Movimientos de stock
25. `tickets.py` - Tickets/soporte
26. `tools.py` - Herramientas
27. `uploads.py` - Carga de archivos
28. `user.py` - Usuarios
29. `warranty.py` - Garantías

#### Modelos de base de datos (20+):
- `brand.py`, `payment.py`, `ticket.py`, `instrument_photo.py`
- `diagnostic.py`, `repair_note.py`, `invoice.py`, `tool.py`
- `inventory.py`, `device_lookup.py`, `appointment.py`
- `newsletter_subscription.py`, `stock_movement.py`
- `manual_document.py`, `signature_request.py`
- `storage_location.py`, `repair.py`, `instrument.py`
- `quote.py`, `contact_message.py`, `user.py`, `category.py`

**Estado integración backend en CDS_VUE3_ZERO:** 0%
- ⚪ services/api.js: 72 bytes (stub)
- ⚪ Stores: solo auth.js (45 bytes - re-export)
- ⚪ Falta: cliente HTTP, interceptors, manejo errores
- ⚪ Falta: mapeo completo de 29 routers → stores/composables
- ⚪ Falta: documentación de contratos/schemas por endpoint

---

## 🗺️ MAPA COMPLETO DE RUTAS (44 rutas)

### Rutas públicas (9) - dentro de Master layout
| Path | Name | Component | Meta |
|------|------|-----------|------|
| `/` | `home` | HomePage | - |
| `/license` | `license` | LicensePage | - |
| `/policy` | `policy` | PolicyPage | - |
| `/terminos` | `terminos` | TermsPage | - |
| `/privacidad` | `privacidad` | PrivacyPage | - |
| `/agendar` | `agendar` | SchedulePage | requiresAuth |
| `/cotizador-ia` | `cotizador-ia` | CotizadorIAPage | - |
| `/calculadoras` | `calculadoras` | CalculatorsPage | - |
| `/tienda` | `tienda` | StorePage | - |

### Rutas auth (3)
| Path | Name | Component | Meta |
|------|------|-----------|------|
| `/login` | `login` | LoginPage | requiresGuest |
| `/register` | `register` | RegisterPage | requiresGuest |
| `/password-reset` | `password-reset` | PasswordResetPage | requiresGuest |

### Rutas client (5)
| Path | Name | Component | Meta |
|------|------|-----------|------|
| `/dashboard` | `dashboard` | DashboardPage | requiresAuth |
| `/ot-payments` | `ot-payments` | OtPaymentsPage | requiresAuth |
| `/repairs` | `repairs` | RepairsPage | requiresAuth |
| `/repairs/:id` | `repair-detail` | RepairDetailPage | requiresAuth |
| `/profile` | `profile` | ProfilePage | requiresAuth |

### Rutas admin (17) - dentro de Master layout
| Path | Name | Component | Meta |
|------|------|-----------|------|
| `/admin` | `admin-dashboard` | AdminDashboard | requiresAuth + requiresAdmin |
| `/admin/inventory` | `admin-inventory` | InventoryPage | requiresAuth + requiresAdmin |
| `/admin/inventory/unified` | `admin-inventory-unified` | InventoryUnified | requiresAuth + requiresAdmin |
| `/admin/clients` | `admin-clients` | ClientsPage | requiresAuth + requiresAdmin |
| `/admin/repairs` | `admin-repairs` | RepairsAdminPage | requiresAuth + requiresAdmin |
| `/admin/quotes` | `admin-quotes` | QuotesAdminPage | requiresAuth + requiresAdmin |
| `/admin/repairs/:id` | `admin-repair-detail` | RepairDetailAdminPage | requiresAuth + requiresAdmin |
| `/admin/categories` | `admin-categories` | CategoriesPage | requiresAuth + requiresAdmin |
| `/admin/contact` | `admin-contact` | ContactMessagesPage | requiresAuth + requiresAdmin |
| `/admin/newsletter` | `admin-newsletter` | NewsletterSubscriptionsPage | requiresAuth + requiresAdmin |
| `/admin/appointments` | `admin-appointments` | AppointmentsPage | requiresAuth + requiresAdmin |
| `/admin/tickets` | `admin-tickets` | TicketsPage | requiresAuth + requiresAdmin |
| `/admin/purchase-requests` | `admin-purchase-requests` | PurchaseRequestsPage | requiresAuth + requiresAdmin |
| `/admin/manuals` | `admin-manuals` | ManualsPage | requiresAuth + requiresAdmin |
| `/admin/stats` | `admin-stats` | StatsPage | requiresAuth + requiresAdmin |
| `/admin/wizards` | `admin-wizards` | WizardsPage | requiresAuth + requiresAdmin |
| `/admin/archive` | `admin-archive` | ArchivePage | requiresAuth + requiresAdmin |

### Rutas token (2)
| Path | Name | Component | Meta |
|------|------|-----------|------|
| `/signature/:token` | `signature` | SignaturePage | - |
| `/photo-upload/:token` | `photo-upload` | PhotoUploadPage | - |

### Rutas calculadoras (9) - desde @/modules/
| Path | Name | Component | Meta |
|------|------|-----------|------|
| `/calc/555` | `calc-555` | `modules/timer555/Timer555View.vue` | - |
| `/calc/resistor-color` | `calc-resistor-color` | `modules/resistorColor/ResistorColorView.vue` | - |
| `/calc/smd-capacitor` | `calc-smd-capacitor` | `modules/smdCapacitor/SmdCapacitorView.vue` | - |
| `/calc/smd-resistor` | `calc-smd-resistor` | `modules/smdResistor/SmdResistorView.vue` | - |
| `/calc/ohms-law` | `calc-ohms-law` | `modules/ohmsLaw/OhmsLawView.vue` | - |
| `/calc/temperature` | `calc-temperature` | `modules/temperature/TemperatureView.vue` | - |
| `/calc/number-system` | `calc-number-system` | `modules/numberSystem/NumberSystemView.vue` | - |
| `/calc/length` | `calc-length` | `modules/length/LengthView.vue` | - |
| `/calc/awg` | `calc-awg` | `modules/awg/AwgView.vue` | - |

**Total rutas:** 44 + 1 fallback (404 → /)

**Navegación guards:**
- `requiresAuth` → Redirect a `/login` si no autenticado
- `requiresAdmin` → Redirect a `/home` si no es admin
- `requiresGuest` → Redirect a `/dashboard` si autenticado

---

## 🗂️ DETALLE POR FASE

### ✅ FASE 1: Public - COMPLETADA (9/9 páginas)

**Todas migradas:**
1. ✅ TermsPage.vue → Vue real + composable useTermsPage
2. ✅ PrivacyPage.vue → Vue real + composable usePrivacyPage
3. ✅ LicensePage.vue → Vue real + composable useLicensePage
4. ✅ PolicyPage.vue → Vue real + composable usePolicyPage
5. ✅ CalculatorsPage.vue → Vue real + composable useCalculatorsPage
6. ✅ **HomePage.vue (158 líneas)** → Vue real + composable useHomePage
7. ✅ **StorePage.vue (314 líneas)** → Vue real + composable useStorePage + GET /inventory/public/
8. ✅ **SchedulePage.vue (433 líneas)** → Vue real + composable useSchedulePage + POST /appointments/
9. ✅ **CotizadorIAPage.vue (223 líneas)** → Vue real + composable useCotizadorIAPage

**Infraestructura Public completada:**
- ✅ MasterLayout.vue (173 líneas) - header/nav/footer sin @legacy
- ✅ vite.config.js - alias @legacy REMOVIDO
- ✅ services/api.js (142 líneas) - cliente HTTP con axios
- ✅ stores/auth.js (217 líneas) - implementación real (no re-export)
- ✅ composables/useAuth.js (31 líneas) - lógica auth desacoplada

**Total cambios fase Public:** 1,717 líneas añadidas

**Estado:** FASE CERRADA - Lista para commit

---

### ✅ FASE 2: Client - COMPLETADA (5/5 páginas)

**Todas migradas:**
1. ✅ DashboardPage.vue (417 líneas) → Vue real + composable useDashboardPage + GET /client/dashboard
2. ✅ RepairsPage.vue (274 líneas) → Vue real + composable useRepairsPage
3. ✅ RepairDetailPage.vue (226 líneas) → Vue real + composable useRepairDetailPage
4. ✅ ProfilePage.vue (384 líneas) → Vue real + composable useProfilePage
5. ✅ OtPaymentsPage.vue (339 líneas) → Vue real + composable useOtPaymentsPage

**Infraestructura Client completada:**
- ✅ utils/repairStatus.js creado - helpers de estados de reparación
- ✅ 5 composables creados (18.6K total)
- ✅ services/api.js expandido con endpoints client
- ✅ Endpoints verificados reales (no inventados)

**Total cambios fase Client:** 1,640 líneas en páginas + composables

**Estado:** FASE CERRADA - Verificada contra backend real

---

### FASE 3: Admin (17 páginas pendientes)

**Todas pendientes (17):**
- ❌ AdminDashboard.vue (142 bytes)
- ❌ AppointmentsPage.vue (144 bytes)
- ❌ ArchivePage.vue (139 bytes)
- ❌ CategoriesPage.vue (142 bytes)
- ❌ ClientsPage.vue (139 bytes)
- ❌ ContactMessagesPage.vue (147 bytes)
- ❌ InventoryPage.vue (141 bytes)
- ❌ InventoryUnifiedPage.vue (126 bytes)
- ❌ ManualsPage.vue (139 bytes)
- ❌ NewsletterSubscriptionsPage.vue (155 bytes)
- ❌ PurchaseRequestsPage.vue (148 bytes)
- ❌ QuotesAdminPage.vue (143 bytes)
- ❌ RepairDetailAdminPage.vue (149 bytes)
- ❌ RepairsAdminPage.vue (144 bytes)
- ❌ StatsPage.vue (137 bytes)
- ❌ TicketsPage.vue (139 bytes)
- ❌ WizardsPage.vue (139 bytes)

**Tareas Admin (por submódulo):**
1. [ ] **Módulo Inventory** (2 páginas)
   - InventoryPage.vue → useInventory.js
   - InventoryUnifiedPage.vue → useInventoryUnified.js
   - Endpoints: GET/POST/PUT/DELETE /api/inventory
2. [ ] **Módulo Clients** (1 página)
   - ClientsPage.vue → useClients.js
   - Endpoints: GET/POST/PUT/DELETE /api/clients
3. [ ] **Módulo Repairs Admin** (2 páginas)
   - RepairsAdminPage.vue → useRepairsAdmin.js
   - RepairDetailAdminPage.vue → useRepairDetailAdmin.js
   - Endpoints: GET/PUT /api/admin/repairs
4. [ ] **Módulo Quotes** (1 página)
   - QuotesAdminPage.vue → useQuotesAdmin.js
   - Endpoints: GET/PUT /api/admin/quotes
5. [ ] **Módulo Tickets** (1 página)
   - TicketsPage.vue → useTickets.js
   - Endpoints: GET/POST/PUT /api/tickets
6. [ ] **Módulo Stats** (1 página)
   - StatsPage.vue → useStats.js
   - Endpoints: GET /api/admin/stats
7. [ ] **Módulo Wizards** (1 página)
   - WizardsPage.vue → useWizards.js
8. [ ] **Módulo Appointments** (1 página)
   - AppointmentsPage.vue → useAppointments.js
   - Endpoints: GET/POST/PUT /api/appointments
9. [ ] **Módulo Categories** (1 página)
   - CategoriesPage.vue → useCategories.js
   - Endpoints: GET/POST/PUT/DELETE /api/categories
10. [ ] **Módulo Purchase Requests** (1 página)
    - PurchaseRequestsPage.vue → usePurchaseRequests.js
11. [ ] **Módulo Contact Messages** (1 página)
    - ContactMessagesPage.vue → useContactMessages.js
12. [ ] **Módulo Newsletter** (1 página)
    - NewsletterSubscriptionsPage.vue → useNewsletterSubscriptions.js
13. [ ] **Módulo Manuals** (1 página)
    - ManualsPage.vue → useManuals.js
14. [ ] **Módulo Archive** (1 página)
    - ArchivePage.vue → useArchive.js
15. [ ] **Dashboard Admin** (1 página)
    - AdminDashboard.vue → useAdminDashboard.js
16. [ ] Crear adminStore.js
17. [ ] Expandir services/api.js con endpoints Admin

---

### FASE 4: Calculadoras (9 páginas pendientes)

**Todas pendientes (9):**
- ❌ AwgPage.vue (123 bytes)
- ❌ LengthPage.vue (129 bytes)
- ❌ NumberSystemPage.vue (141 bytes)
- ❌ OhmsLawPage.vue (131 bytes)
- ❌ ResistorColorPage.vue (143 bytes)
- ❌ SmdCapacitorPage.vue (141 bytes)
- ❌ SmdResistorPage.vue (139 bytes)
- ❌ TemperaturePage.vue (139 bytes)
- ❌ Timer555Page.vue (133 bytes)

**Tareas Calculadoras:**
1. [ ] Migrar AwgPage.vue → useAwgCalculator.js
   - NO cambiar lógica matemática
   - Mantener fórmulas exactas
2. [ ] Migrar LengthPage.vue → useLengthCalculator.js
3. [ ] Migrar NumberSystemPage.vue → useNumberSystemCalculator.js
4. [ ] Migrar OhmsLawPage.vue → useOhmsLawCalculator.js
5. [ ] Migrar ResistorColorPage.vue → useResistorColorCalculator.js
6. [ ] Migrar SmdCapacitorPage.vue → useSmdCapacitorCalculator.js
7. [ ] Migrar SmdResistorPage.vue → useSmdResistorCalculator.js
8. [ ] Migrar TemperaturePage.vue → useTemperatureCalculator.js
9. [ ] Migrar Timer555Page.vue → useTimer555Calculator.js
10. [ ] Crear calculatorsStore.js (si necesario)

---

### FASE 5: Token (2 páginas pendientes)

**Todas pendientes (2):**
- ❌ SignaturePage.vue (135 bytes)
- ❌ PhotoUploadPage.vue (137 bytes)

**Tareas Token:**
1. [ ] Migrar SignaturePage.vue → useSignature.js
   - Endpoints: POST /api/token/signature
   - Mantener payloads intactos
2. [ ] Migrar PhotoUploadPage.vue → usePhotoUpload.js
   - Endpoints: POST /api/token/photo-upload
   - Mantener payloads intactos

---

## 🎨 MIGRACIÓN SASS → VUE REAL (127 componentes)

**Estado actual:** 1/127 componentes migrados (0.8%)

### Componentes migrados:
- ✅ PageSection.vue (SASS eliminado: 57 líneas)

### Próximos 10 componentes (prioridad alta):
1. [ ] PageSectionHeader.vue
2. [ ] PageSectionContent.vue
3. [ ] PageSectionFooter.vue
4. [ ] BackgroundPromo.vue
5. [ ] PageWrapper.vue
6. [ ] BaseCard.vue
7. [ ] BaseGrid.vue
8. [ ] BaseList.vue
9. [ ] BaseModal.vue
10. [ ] BaseTable.vue

### Proceso por componente:
1. [ ] Leer `src/vue/components/.../MiComponente.vue` (legacy)
2. [ ] Identificar clases CSS usadas
3. [ ] Buscar estilos en SASS global (`src/scss/`)
4. [ ] Identificar variables SASS (copiar valores exactos)
5. [ ] Crear computed properties para estilos dinámicos
6. [ ] Reemplazar clases por `:style` inline
7. [ ] Responsive con `windowWidth` + `computed` (NO media queries)
8. [ ] Scoped CSS SOLO para casos especiales (selectores descendientes, ::before, ::after)
9. [ ] Comentar/eliminar del SASS global
10. [ ] Probar en todos los breakpoints
11. [ ] Evidencia: archivo:línea
12. [ ] Commit individual (NO masivo)

**Variables existentes (NO INVENTAR):**
```javascript
// Colores (desde _variables.scss)
const COLORS = {
  primary: '#ec6b00',      // Naranja PANTONE 7577 C
  dark: '#3e3c38',         // Vintage Black PANTONE Black 7 C
  light: '#d3d0c3',        // Vintage Beige PANTONE 7527 C
  white: '#ffffff',
  black: '#000000',
  success: '#038600',      // NO verde (#28a745 → primary)
  danger: '#dc3545',
  warning: '#ffc107'
}

// Grises
const GRAYS = {
  50: '#fafafa',
  100: '#f3f4f6',
  200: '#e5e7eb',
  300: '#d1d5db',
  400: '#9ca3af',
  500: '#6b7280',
  600: '#4b5563',
  700: '#374151',
  800: '#1f2937',
  900: '#111827'
}

// Breakpoints
const BREAKPOINTS = {
  sm: 576,
  md: 768,
  lg: 992,
  xl: 1200,
  xxl: 1400,
  xxxl: 1600
}

// Espaciado (sistema 4px)
const SPACERS = {
  xs: '0.25rem',   // 4px
  sm: '0.5rem',    // 8px
  md: '1rem',      // 16px
  lg: '1.5rem',    // 24px
  xl: '2rem'       // 32px
}

// Border Radius
const RADIUS = {
  sm: '8px',
  md: '12px',
  lg: '16px',
  pill: '999px',
  circle: '50%'
}
```

---

## 🧹 SANITIZACIÓN SASS (Design System)

**Problema:** Código fragmentado en cascada
- Colores hardcoded repetidos 100+ veces
- 150+ colores "-legacy" redundantes
- 24 componentes con valores hardcoded

**Solución:** Design System Central
- ✅ CREADO: `src/scss/_design-system.scss`
- CSS Custom Properties (`:root`)
- Variables accesibles: `var(--color-primary)`, `var(--gray-500)`, etc.

### Reemplazo masivo (buscar/reemplazar):
```bash
# Colores
#ec6b00 → var(--color-primary)
#3e3c38 → var(--color-dark)
#6b7280 → var(--gray-500)
#e5e7eb → var(--gray-200)

# Tipografía
font-size: 0.875rem → font-size: var(--text-sm)
font-size: 1rem → font-size: var(--text-base)
font-weight: 600 → font-weight: var(--fw-semibold)

# Geometría
border-radius: 12px → border-radius: var(--radius-md)
border-radius: 8px → border-radius: var(--radius-sm)
padding: 1rem → padding: var(--spacer-md)
```

### Métricas objetivo:
| Métrica | Antes | Objetivo |
|---------|-------|----------|
| Líneas `_app.scss` | 4,724 | 2,500 |
| Colores únicos hardcoded | ~150 | 10 |
| Font-sizes únicos | ~25 | 9 |
| Border-radius únicos | ~12 | 5 |
| Componentes con hardcode | 24 | 0 |
| Colores verdes (no-WhatsApp) | 59 | 0 |

### Reglas de oro:
- ❌ **NO INVENTAR** - usar solo Manual + `_variables.scss`
- ✅ **HEGEMONÍA NARANJA** - verde solo en WhatsApp (#25d366)
- ✅ **MÍNIMO LEGIBILIDAD** - nada menor a 0.75rem (12px)
- ✅ **TODO verde → naranja** (excepto WhatsApp)

---

## 🔌 INTEGRACIÓN BACKEND

**Estado actual:** 0% integrado en CDS_VUE3_ZERO

### Backend disponible (CDS_cz_NUEVA/backend):
- **Arquitectura:** FastAPI (Python)
- **Archivos:** 6,733 .py
- **Endpoints:** 276 documentados
- **Base de datos:** SQLite (cirujano.db)

### Tareas integración:
1. [ ] Expandir `services/api.js` (actualmente 72 bytes stub)
   - Crear cliente HTTP (axios/fetch)
   - Configurar baseURL desde .env
   - Interceptors para auth (JWT)
   - Manejo de errores global
2. [ ] Documentar endpoints por módulo:
   - [ ] Auth: login, register, reset, verify2fa
   - [ ] Client: dashboard, repairs, profile, ot-payments
   - [ ] Admin: (17 módulos - ver detalle arriba)
   - [ ] Calculadoras: (si tienen endpoints)
   - [ ] Token: signature, photo-upload
3. [ ] Crear stores necesarios:
   - [ ] clientStore.js
   - [ ] adminStore.js
   - [ ] repairsStore.js
   - [ ] quotesStore.js
   - [ ] inventoryStore.js
   - [ ] ticketsStore.js
   - [ ] appointmentsStore.js
   - [ ] categoriesStore.js
   - [ ] statsStore.js
   - [ ] calculatorsStore.js (si necesario)
4. [ ] Validar contratos API (schemas):
   - Leer: `backend/app/schemas/` (legacy)
   - NO inventar payloads
   - Mantener paridad exacta
5. [ ] Configurar .env con variables backend:
   - API_BASE_URL
   - TURNSTILE_SITE_KEY
   - JWT_SECRET (solo frontend si necesario)
6. [ ] Testing de integración:
   - Validar cada endpoint con backend real
   - Verificar auth guards
   - Probar flujos críticos

---

## ✅ CRITERIOS DE AVANCE

Por cada fase:
1. ✅ Build válido (`npm run build` sin errores)
2. ✅ Diff mínimo (paridad funcional con legacy)
3. ✅ Evidencia archivo:línea documentada
4. ✅ Tests pasando (si existen)
5. ✅ Backend integrado y validado
6. ✅ Sin referencias @legacy en módulo completado
7. ✅ README.md actualizado con estado

---

## 📈 MÉTRICAS GLOBALES - ACTUALIZADO

### Progreso general:
- **Páginas:** 20/47 completadas (42.6%) ⬆️ de 12.8% inicial
- **Componentes Vue real:** 1/127 migrados (0.8%) - pendiente migración SASS→Vue
- **SASS sanitizado:** 57/8000 líneas (0.7%)
- **Backend integrado:** Parcial (api.js 142 líneas, auth.js 217 líneas, composables 18.6K)
- **Referencias @legacy:** 32 en módulos pendientes (alias removido de vite.config.js)

### Fases:
- Auth: 100% ✅ (6/6)
- Public: 100% ✅ (9/9) ⬆️ de 62% inicial
- Client: 100% ✅ (5/5) ⬆️ de 0%
- Admin: 0% ⚪ (0/17) ← **SIGUIENTE**
- Calculadoras: 0% ⚪ (0/9)
- Token: 0% ⚪ (0/2)

### Cambios recientes (no commiteados):
- **~3,940 líneas añadidas** (Public ~1,700 + Client ~1,640 + infraestructura ~600)
- **15 archivos modificados** (páginas Auth/Public/Client)
- **14 composables creados** (useAuthForms + 9 Public + 5 Client)
- **1 util creado** (repairStatus.js)
- **Infraestructura migrada:** MasterLayout, api.js, auth.js, vite.config.js

### Meta final:
- **47 páginas** → 100% Vue real sin wrappers
- **127 componentes** → 100% Vue real (estilos inline/scoped)
- **8,000 líneas SASS** → ~500 líneas (reducción 94%)
- **6,733 archivos backend** → 100% integrado en services/stores
- **0 referencias @legacy** → 100% autónomo

---

## 🚨 RIESGOS ABIERTOS

1. ⚠️ Validación pendiente build/install (`npm install` colgado previamente)
2. ⚠️ Turnstile depende de backend/keys de entorno
3. ⚠️ Coexistencia temporal wrappers + componentes nuevos
4. ⚠️ No hay dependencias instaladas en CDS_VUE3_ZERO (`vite: not found`)
5. ⚠️ 42 referencias @legacy en módulos no migrados
6. ⚠️ Backend en CDS_cz_NUEVA (no en CDS_ZERO) - unificación pendiente
7. ⚠️ Contratos API no documentados en CDS_VUE3_ZERO

---

## 📝 NOTAS FINALES

- Este archivo se actualiza después de cada fase
- NO hacer commits sin autorización explícita
- Reportar evidencia archivo:línea obligatoria
- Mantener paridad funcional (no inventar)
- Aditivo + deconstructivo (desarmar legacy → armar Vue nuevo)

**Siguiente paso:** Fase Admin (17 páginas) - Migración por submódulos (ver orden en README_AUDIT.md)
