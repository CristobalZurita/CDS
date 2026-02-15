# 📋 MATRIZ DE CLASIFICACIÓN ADITIVA
**Objetivo:** Mapear CADA CAJA sin tocar nada. Solo inventario. Cuando sepamos EXACTAMENTE qué va dónde, ENTONCES decidimos si deconstruir o no.

---

## 🏠 ESTADO ACTUAL - INVENTARIO DE CAJAS

### CAJA 1: SCSS/ESTILOS
**Ubicación actual:** `/src/scss/`

```
src/scss/
├── _admin.scss              → Estilos admin (¿ir a pages/admin?)
├── _brand.scss              → Branding (¿ir a abstracts/variables?)
├── _core.scss               → Core styles (¿ir a base/?)
├── _global.scss             → Global (¿dónde ir?)
├── _layout.scss             → Layout (✅ CORRECTO - layout/)
├── _mixins.scss             → Mixins (✅ CORRECTO - abstracts/)
├── _public.scss             → Estilos público (¿ir a pages/public?)
├── _reset.scss              → Reset (✅ CORRECTO - base/)
├── _theming.scss            → Temas (✅ CORRECTO - themes/)
├── _typography.scss         → Tipografía (✅ CORRECTO - base/)
├── _variables.scss          → Variables (✅ CORRECTO - abstracts/)
├── abstracts/
│   ├── _index.scss          → Index (✅ CORRECTO)
│   ├── _mixins.scss         → Mixins (✅ CORRECTO)
│   └── _variables.scss      → Variables (✅ CORRECTO)
├── base/
│   ├── _index.scss          → Index (✅ CORRECTO)
│   └── _typography.scss     → Typography (✅ CORRECTO)
├── components/
│   └── _index.scss          → VACÍO ❌ NECESITA POBLACIÓN
├── layout/
│   ├── _index.scss          → Index (✅ CORRECTO)
│   └── _sections.scss       → Sections (✅ CORRECTO)
├── pages/
│   ├── _admin.scss          → Admin styles (✅ CORRECTO)
│   └── _index.scss          → Index (✅ CORRECTO)
├── themes/
│   └── _index.scss          → Themes (✅ CORRECTO)
├── vendors/
│   └── _index.scss          → Vendors (✅ CORRECTO)
├── main.scss                → Entry point (⚠️ REVISAR imports)
└── style.scss               → ¿Duplicado con main.scss?
```

**Análisis:**
- ✅ 7-1 estructura existe
- ❌ components/ vacío
- ❌ utilities/ NO EXISTE
- ⚠️ Archivos root duplicados (_admin, _brand, _core, _global, etc. que no están en carpetas)
- ⚠️ ¿style.scss vs main.scss? Revisar si es duplicado

**Plan de movimiento ADITIVO:**
1. NO TOCAR: Lo que está correcto (abstracts, base, layout, pages, themes, vendors)
2. AÑADIR: `/src/scss/utilities/` (5 archivos nuevos)
3. POBLAT: `/src/scss/components/` (7 archivos nuevos)
4. REVISAR: Archivos root - ¿consolidar en abstracts o eliminar? (DECONSTRUCCIÓN deliberada)

---

### CAJA 2: COMPOSABLES/LÓGICA REUTILIZABLE
**Ubicación actual:** `/src/composables/`

```
src/composables/
├── emails.js                ✅ OK (reutilizable)
├── layout.js                ✅ OK (reutilizable)
├── scheduler.js             ✅ OK (reutilizable)
├── settings.js              ✅ OK (reutilizable)
├── strings.js               ✅ OK (reutilizable)
├── useApi.js                ✅ OK (pero: CONVERTIR A TypeScript)
├── useAuth.js               ✅ OK (pero: CONVERTIR A TypeScript)
├── useCalculator.ts         ⚠️ MEZCLADO (1 de .ts, rest .js)
├── useCategories.js         ✅ OK (pero: CONVERTIR A TypeScript)
├── useDiagnostic.js         ✅ OK (pero: CONVERTIR A TypeScript)
├── useDiagnostics.js        ✅ OK (pero: CONVERTIR A TypeScript)
├── useInstruments.js        ✅ OK (pero: CONVERTIR A TypeScript)
├── useInstrumentsCatalog.js ✅ OK (pero: CONVERTIR A TypeScript)
├── useInventory.js          ✅ OK (pero: CONVERTIR A TypeScript)
├── useQuotation.js          ✅ OK (pero: CONVERTIR A TypeScript)
├── useRepairs.js            ✅ OK (pero: CONVERTIR A TypeScript)
├── useStockMovements.js     ✅ OK (pero: CONVERTIR A TypeScript)
├── useUsers.js              ✅ OK (pero: CONVERTIR A TypeScript)
├── useValidation.ts         ⚠️ MEZCLADO (1 de .ts, rest .js)
└── utils.js                 ⚠️ GENÉRICO (¿debería ir a /utils/?)
```

**Análisis:**
- ✅ Composables bien nombrados (use* pattern)
- ⚠️ MEZCLADO: Algunos .ts, mayoría .js
- ❌ SIN TIPOS: Necesitan TypeScript
- ⚠️ utils.js: ¿Genérico? Debería ir a /src/utils/

**Plan de movimiento ADITIVO:**
1. NO TOCAR: Lógica (funcionan, se mantienen como están)
2. CREAR: Interfaces TypeScript en `/src/types/composables.ts`
3. MIGRAR: Gradualmente .js → .ts (sin cambiar lógica, solo tipos)
4. REORGANIZAR: utils.js → /src/utils/composables.ts (DESPUÉS de clarificar)

---

### CAJA 3: STORES/ESTADO PINIA
**Ubicación actual:** `/src/stores/`

```
src/stores/
├── auth.js                  ✅ OK (auth state)
├── categories.js            ✅ OK (categories state)
├── diagnostics.js           ✅ OK (diagnostics state)
├── instruments.js           ✅ OK (instruments state)
├── inventory.js             ✅ OK (inventory state)
├── quotation.js             ✅ OK (quotation state)
├── repairs.js               ✅ OK (repairs state)
├── stockMovements.js        ✅ OK (stock movements state)
├── users.js                 ✅ OK (users state)
├── __tests__/
│   └── inventory.spec.js    ✅ OK (test)
```

**Análisis:**
- ✅ Stores bien organizados por dominio
- ❌ SIN TIPOS: Necesitan TypeScript
- ❌ SIN INTERFACES: Pinia con types mejoraría DX

**Plan de movimiento ADITIVO:**
1. NO TOCAR: Stores funcionan
2. CREAR: `/src/types/stores.ts` (interfaces para cada store)
3. MIGRAR: Gradualmente .js → .ts (con tipos)

---

### CAJA 4: COMPONENTES VUE
**Ubicación actual:** `/src/vue/components/` (~130 archivos)

```
src/vue/components/
├── admin/                   ✅ Admin-específicos
│   ├── layout/              ✅ Admin layout
│   ├── repair/              ✅ Repair sub-components
│   ├── wizard/              ✅ Wizard components
│   └── ... (15+ componentes)
├── ai/                      ✅ AI-related
├── articles/                ✅ Article rendering
├── auth/                    ✅ Auth forms
├── dashboard/               ✅ Dashboard widgets
├── footer/                  ✅ Footer sections
├── forms/                   ✅ Form components
├── generic/                 ✅ Generic (Link, Image, etc)
├── layout/                  ✅ Layout (Header, Section, etc)
├── loaders/                 ✅ Loading spinners
├── modals/                  ✅ Modal dialogs
├── nav/                     ✅ Navigation
├── projects/                ✅ Project showcase
├── quotation/               ✅ Quotation flow
├── system/                  ✅ System alerts
├── widgets/                 ✅ UI widgets
└── prototypes/              ✅ Prototypes
```

**Análisis:**
- ✅ Componentes bien organizados por dominio
- ⚠️ ESTILOS INLINE: Probablemente muchos tienen `style=` o `:style`
- ❌ SIN TIPOS: Props sin TypeScript

**Plan de movimiento ADITIVO:**
1. AUDITAR: Buscar inline styles y :style dinámicos en cada componente
2. CREAR: Archivos SCSS para cada categoria (admin, forms, widgets, etc.)
3. MIRAR: Props → TypeScript interfaces

---

### CAJA 5: VALIDATION/TIPOS DE DOMINIO
**Ubicación actual:** `/src/validation/` + `/src/domain/`

```
src/validation/
├── index.ts                 ✅ Main validators
├── numeric.ts               ✅ Numeric validation
├── physical.ts              ✅ Physical validation
├── rules.ts                 ✅ Validation rules

src/domain/
├── awg/                     ✅ AWG calculator domain
├── common/                  ✅ Common types
├── length/                  ✅ Length calculator domain
├── numberSystem/            ✅ Number system domain
├── ohmsLaw/                 ✅ Ohms Law domain
├── resistorColor/           ✅ Resistor color calculator
├── smdCapacitor/            ✅ SMD capacitor domain
├── smdResistor/             ✅ SMD resistor domain
├── temperature/             ✅ Temperature calculator
└── timer555/                ✅ Timer 555 calculator
```

**Análisis:**
- ✅ TypeScript types YA EXISTEN
- ✅ Domain-driven design aplicado
- ✅ Bien organizado

**Plan de movimiento ADITIVO:**
1. NO TOCAR: Funcionan perfectamente
2. EXPANDIR: Crear tipos API para todas las respuestas
3. UNIFICAR: `/src/types/` como hub central

---

### CAJA 6: SERVICIOS/API
**Ubicación actual:** `/src/services/`

```
src/services/
├── api.js                   ⚠️ API client (¿métodos hardcodeados?)
├── toastService.js          ✅ Toast notifications
└── (¿FALTA: auth, validación, seguridad?)
```

**Análisis:**
- ⚠️ MUY GENÉRICO: api.js probablemente tiene TODO
- ❌ FALTA: Servicios de seguridad (sanitization, XSS prevention, CSRF)
- ❌ FALTA: Servicio de validación centralizado

**Plan de movimiento ADITIVO:**
1. AUDITAR: `/src/services/api.js` - ¿qué contiene?
2. CREAR: `/src/services/security.ts` (XSS, sanitization, CSRF)
3. CREAR: `/src/services/validation.ts` (validación centralizada)
4. CREAR: `/src/services/auth.ts` (JWT management seguro)
5. REFACTOR: api.js → type-safe gradualmente

---

### CAJA 7: RUTAS/ROUTER
**Ubicación actual:** `/src/router/`

```
src/router/
├── index.js                 ⚠️ Rutas en JS
└── index.ts                 ⚠️ ¿Duplicado con .js?
```

**Análisis:**
- ⚠️ ¿Dos archivos router? ¿Cuál se usa?
- ❌ NO ESTÁ EN TS (si existe .ts pero se usa .js)
- ❌ PROBABLEMENTE: Sin meta de seguridad/permisos

**Plan de movimiento ADITIVO:**
1. AUDITAR: ¿Cuál router es activo? (.js o .ts)
2. CONSOLIDAR: Elegir UNO (probablemente .ts)
3. AÑADIR: Meta information (seguridad, permisos, roles)

---

### CAJA 8: VIEWS/PÁGINAS
**Ubicación actual:** `/src/vue/content/pages/` + `/src/views/`

```
src/views/
├── HomeView.vue             ✅ Home
├── InventoryUnified.vue     ✅ Inventory

src/vue/content/pages/
├── CalculatorsPage.vue      ✅ Public pages
├── CotizadorIAPage.vue      ✅ AI quoter
├── DashboardPage.vue        ✅ Dashboard
├── ... (~20 pages)
├── admin/
│   ├── AdminDashboard.vue   ✅ Admin pages
│   ├── ... (~15 admin pages)
```

**Análisis:**
- ⚠️ FRAGMENTADO: `/src/views/` AND `/src/vue/content/pages/`
- ✅ Páginas bien organizadas
- ❌ ¿Convención de nombres inconsistente? (View vs Page)

**Plan de movimiento ADITIVO:**
1. NO TOCAR: Funcionan
2. DOCUMENTAR: Convención (View para simples, Page para complejas)
3. OPCIONALMENTE: Unificar estructura después (DECONSTRUCCIÓN deliberada)

---

### CAJA 9: MAIN.JS + CONFIGURACIÓN
**Ubicación actual:** `/src/main.js`

```javascript
// Probablemente:
// - Crea app Vue
// - Monta pinia
// - Carga router
// - Importa SCSS
// - ¿Configura plugins?
```

**Análisis:**
- ⚠️ REQUIERE AUDITORÍA: ¿Qué configuración tiene?
- ❌ PROBABLEMENTE: Sin setup para seguridad (CSP, headers, etc.)

**Plan de movimiento ADITIVO:**
1. AUDITAR: `/src/main.js` - ¿qué hace?
2. CREAR: `/src/config/security.ts` (configuración de seguridad)
3. CREAR: `/src/config/app.ts` (configuración de app)
4. IMPORTAR: Desde main.js

---

### CAJA 10: TIPOS/INTERFACES
**Ubicación actual:** `/src/types/` (si existe) o fragmentado

```
Actual: FRAGMENTADO
- domain/common/types.ts
- validation/index.ts
- composables/*.js (sin tipos)
- stores/*.js (sin tipos)
```

**Análisis:**
- ❌ NO HAY `/src/types/` centralizado
- ❌ Tipos esparcidos en varios lugares
- ❌ Duplicación de tipos probablemente

**Plan de movimiento ADITIVO:**
1. CREAR: `/src/types/` hub central
2. CREAR: `api.ts`, `components.ts`, `stores.ts`, `composables.ts`, `domain.ts`
3. IMPORTAR desde main/services cuando sea necesario

---

### CAJA 11: ANÁLYTICS/TRACKING
**Ubicación actual:** `/src/analytics/`

```
src/analytics/
├── events.js                ✅ Event definitions
├── index.js                 ✅ Main
├── providers/
│   ├── consoleProvider.js   ✅ Console logging
│   └── gtmProvider.js       ✅ GTM integration
├── tracker.js               ✅ Tracker
```

**Análisis:**
- ✅ Bien organizado
- ❌ PROBABLEMENTE: Sin tipos TypeScript

**Plan de movimiento ADITIVO:**
1. NO TOCAR: Funcionan
2. OPCIONALMENTE: Migrar a TypeScript

---

### CAJA 12: BACKEND
**Ubicación actual:** `/backend/`

```
backend/
├── app/                     ✅ FastAPI app
│   ├── models/              → DB models (SQLAlchemy)
│   ├── routes/              → API endpoints
│   ├── schemas/             → Pydantic schemas
│   ├── services/            → Business logic
│   └── middleware/          → Middleware
├── requirements.txt         ⚠️ AUDITAR: ¿Qué paquetes?
├── alembic/                 ✅ DB migrations
└── tests/                   ❌ PROBABLEMENTE: Pocos/nulos
```

**Análisis:**
- ⚠️ REQUIERE AUDITORÍA PROFUNDA: Backend es "CAJA NEGRA"
- ❌ PROBABLEMENTE: Sin validación de inputs
- ❌ PROBABLEMENTE: Sin encriptación PII
- ❌ PROBABLEMENTE: Sin rate limiting
- ❌ PROBABLEMENTE: Sin audit logs
- ❌ PROBABLEMENTE: Sin tests de seguridad

**Plan de movimiento ADITIVO (Backend):**
1. AUDITAR `/backend/app/` - estructura
2. CREAR: `/backend/app/security/` (validadores, encriptación)
3. CREAR: `/backend/app/audit/` (audit logging)
4. AÑADIR: Rate limiting middleware
5. MIGRAR: Pydantic schemas con validación stricta
6. CREAR: Tests de seguridad

---

## 🗺️ MAPA DE DESTINOS - DÓNDE VA CADA CAJA

### Fase 1: SCSS COMPLETO (ADITIVO)
```
✅ Mantener: abstracts/, base/, layout/, pages/, themes/, vendors/
➕ AÑADIR: utilities/ (5 archivos)
➕ POBLAR: components/ (7 archivos)
🔍 REVISAR: Archivos root (_admin.scss, _brand.scss, etc.)
   └─ Decisión: CONSOLIDAR en abstracts o main.scss
```

### Fase 2: FRONT SECURITY (ADITIVO + CREAR)
```
✅ Mantener: composables/, stores/, services/
➕ CREAR: /src/services/security.ts
➕ CREAR: /src/services/auth.ts (JWT seguro)
➕ CREAR: /src/config/security.ts
➕ AUDITAR: Inline styles en componentes
➕ MIGRAR: Inline styles → SCSS + CSS Custom Properties
```

### Fase 3: BACKEND SECURITY (AUDITOR PROFUNDA)
```
❓ PRIMERO: Leer backend/app/* - estructura
➕ CREAR: /backend/app/security/ (validators, encryption)
➕ CREAR: /backend/app/audit/
➕ CREAR: /backend/app/middleware/rate_limit.py
➕ MIGRAR: Schemas con validación Pydantic
```

### Fase 4: TYPESCRIPT (GRADUAL, SIN ROMPER)
```
✅ Mantener: domain/ (ya tiene tipos)
✅ Mantener: validation/ (ya tiene tipos)
➕ CREAR: /src/types/ (hub central)
🔄 MIGRAR: composables/ .js → .ts (con tipos)
🔄 MIGRAR: stores/ .js → .ts (con tipos)
🔄 MIGRAR: services/ .js → .ts (con tipos)
🔄 AUDITAR: router/ - ¿cuál es activo?
```

### Fase 5: TESTING (ADITIVO)
```
✅ Mantener: /src/stores/__tests__/ (ya existen tests)
➕ CREAR: /tests/unit/ (más coverage)
➕ CREAR: /tests/e2e/ (Cypress)
➕ CREAR: /tests/integration/ (API testing)
➕ CREAR: /backend/tests/ (backend testing)
```

### Fase 6: OBSERVABILIDAD (CREAR)
```
➕ CREAR: /src/services/logging.ts (logging centralizado)
➕ CREAR: /backend/app/logging/ (Sentry, ELK)
➕ CREAR: /backend/app/metrics/ (Prometheus)
```

### Fase 7: CI/CD (CREAR EN ROOT)
```
➕ CREAR: .github/workflows/ (GitHub Actions)
➕ CREAR: .husky/ (pre-commit hooks)
➕ CREAR: docker-compose.yml (si no existe)
```

---

## ✅ SUMARIO: QUÉ ES ADITIVO vs QUÉ REQUIERE DECONSTRUCCIÓN

### ADITIVO (NO TOCAR, SOLO AÑADIR):
- ✅ Composables lógica (funcionan, mantener como están)
- ✅ Stores Pinia (funcionan, mantener como están)
- ✅ Componentes Vue (funcionan, mantener como están)
- ✅ Domain types (YA TypeScript, perfectos)
- ✅ Analytics (funcionan, mantener como están)
- ✅ Layout SCSS (✅ correcto, solo añadir utilities + components)

### REQUIERE DECONSTRUCCIÓN DELIBERADA:
- 🔄 Archivos SCSS root (_admin.scss, _brand.scss, etc.) - CONSOLIDAR en abstracts
- 🔄 router/index.js vs router/index.ts - ELEGIR UNO
- 🔄 /src/views/ vs /src/vue/content/pages/ - UNIFICAR estructura
- 🔄 /src/services/api.js - REFACTOR a type-safe
- 🔄 Componentes con inline styles - MIGRAR A SCSS
- 🔄 Composables/Stores/Services .js → .ts - MIGRAR GRADUALMENTE

### CREAR NUEVO (ADITIVO PURO):
- ➕ /src/scss/utilities/ (5 archivos SCSS)
- ➕ /src/scss/components/ (7 archivos SCSS)
- ➕ /src/types/ (hub central para TypeScript)
- ➕ /src/services/security.ts
- ➕ /src/services/auth.ts
- ➕ /src/config/security.ts
- ➕ /backend/app/security/
- ➕ /backend/app/audit/
- ➕ .github/workflows/
- ➕ .husky/
- ➕ /tests/ (nuevos tests)

---

## 🎯 PRÓXIMO PASO

**ANTES de hacer NADA:**

1. ¿Leer archivos clave para ENTENDER el estado actual?
   - /src/main.js - ¿Qué se inicializa?
   - /src/services/api.js - ¿Cómo funciona API?
   - /backend/app/main.py - ¿Qué configura?
   - /src/router/index.js vs index.ts - ¿Cuál activo?

2. ¿O saltamos directo a CREAR la estructura paralela?
   - Crear carpetas vacías
   - Crear files skeletons
   - Definir checkpoints de sincronización

**¿Qué prefieres?**
