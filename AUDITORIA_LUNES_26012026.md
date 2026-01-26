# AUDITORIA COMPLETA DEL PROYECTO - LUNES 26/01/2026

**Proyecto:** Cirujano de Sintetizadores (CDS)
**Fecha:** 26 de Enero de 2026
**Rama:** CZ_NUEVA
**Auditor:** Claude Opus 4.5

---

## RESUMEN EJECUTIVO

| Categoría | Críticos | Importantes | Menores |
|-----------|----------|-------------|---------|
| Endpoints y API | 2 | 3 | 2 |
| Componentes Vue | 0 | 3 | 5 |
| Rutas y Navegación | 0 | 3 | 2 |
| Estilos y Assets | 0 | 1 | 3 |
| Backend | 1 | 2 | 1 |
| **TOTAL** | **3** | **12** | **13** |

---

## 1. PROBLEMAS CRITICOS

### 1.1 URL Hardcodeada en QuoteGenerator.vue
**Archivo:** `src/vue/components/ai/QuoteGenerator.vue`
**Línea:** 53
**Problema:** URL de API hardcodeada que NO usa la variable de entorno
```javascript
axios.post('http://127.0.0.1:8000/api/v1/quotations/estimate', {
```
**Impacto:** El componente NO funcionará en producción
**Solución:** Usar `import { api } from '@/services/api'` y cambiar a `api.post('/quotations/estimate', ...)`

---

### 1.2 Router Backend Duplica search_router
**Archivo:** `backend/app/api/v1/router.py`
**Líneas:** 138-141
**Problema:** El router de búsqueda se incluye DOS VECES
```python
if globals().get("search_router"):
    api_router.include_router(globals()["search_router"].router)
if globals().get("search_router"):  # <-- DUPLICADO
    api_router.include_router(globals()["search_router"].router)
```
**Impacto:** Puede causar conflictos de rutas o comportamiento inesperado
**Solución:** Eliminar las líneas 140-141

---

### 1.3 API_URL Definida en 3 Lugares Diferentes
**Archivos afectados:**
- `src/services/api.js` (línea 3)
- `src/composables/useApi.js` (línea 14)
- `src/composables/useAuth.js` (línea 15)

**Problema:** La misma constante está definida en 3 archivos diferentes
```javascript
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'
```
**Impacto:** Inconsistencia si se modifica uno pero no los otros
**Solución:** Centralizar en un solo archivo de configuración y exportar

---

## 2. PROBLEMAS IMPORTANTES

### 2.1 Páginas Admin Sin Ruta Definida
**Archivos existentes pero sin ruta en router:**

| Archivo | Existe | Ruta Definida |
|---------|--------|---------------|
| `StatsPage.vue` | ✓ | ✗ NO |
| `ManualsPage.vue` | ✓ | ✗ NO (solo redirect) |
| `WizardsPage.vue` | ✓ | ✗ NO |

**Ubicación:** `src/vue/content/pages/admin/`
**Impacto:** Funcionalidad desarrollada pero inaccesible
**Solución:** Agregar rutas al router o eliminar archivos no usados

---

### 2.2 Directorio de Avatares No Existe
**Referencia:** `src/vue/components/articles/items/ItemTestimonial.vue` (línea 5)
```vue
<ImageView :src="props.image || '/images/avatars/default.svg'"
```
**Problema:** El directorio `/public/images/avatars/` NO existe
**Impacto:** Fallback de imagen por defecto no funcionará
**Solución:** Crear directorio y agregar `default.svg`

---

### 2.3 Datos Placeholder en Páginas Legales
**Archivos afectados:**
- `src/vue/content/pages/TermsPage.vue` (línea 175)
- `src/vue/content/pages/PrivacyPage.vue` (línea 186)

**Problema:** Teléfono de contacto con placeholder
```html
<li>Teléfono: +56 9 XXXX XXXX</li>
```
**Impacto:** Información de contacto incompleta en páginas legales
**Solución:** Reemplazar con número real

---

### 2.4 Enlace Hardcodeado a Backend Docs
**Archivo:** `src/vue/components/nav/navbar-wrappers/RouteNavbar.vue` (líneas 54-55)
```javascript
if (!base.find(b => String(b.path).includes('127.0.0.1:8000')) ) {
    base.push({ path: 'http://127.0.0.1:8000/docs', label: 'BACK', ... })
}
```
**Impacto:** Enlace de desarrollo visible/no funcional en producción
**Solución:** Condicionar a modo desarrollo o usar variable de entorno

---

### 2.5 Iconos SVG Son Placeholders
**Archivos:**
- `src/assets/icons/facebook.svg`
- `src/assets/icons/instagram.svg`
- `src/assets/icons/twitter.svg`

**Contenido actual:** Solo rectángulos de color, no iconos reales
```svg
<svg ...><rect width="24" height="24" rx="4" fill="#1877F2"/></svg>
```
**Impacto:** Iconos de redes sociales no reconocibles
**Solución:** Reemplazar con iconos SVG reales o usar FontAwesome

---

### 2.6 Lógica de Imports Compleja en Backend Router
**Archivo:** `backend/app/api/v1/router.py`
**Problema:** Sistema de importación con múltiples try/except que pueden fallar silenciosamente
**Impacto:** Routers pueden no cargarse sin errores visibles
**Solución:** Simplificar arquitectura de imports o agregar logging

---

## 3. PROBLEMAS MENORES

### 3.1 Console.log en Código de Producción
**Total encontrados:** 43 ocurrencias en 23 archivos

**Archivos con más ocurrencias:**
| Archivo | Cantidad |
|---------|----------|
| `admin/RepairDetailAdminPage.vue` | 5 |
| `admin/InventoryPage.vue` | 5 |
| `admin/AppointmentsPage.vue` | 4 |
| `admin/repair/RepairComponentsManager.vue` | 4 |
| `SchedulePage.vue` | 3 |

**Solución:** Reemplazar con servicio de logging o eliminar antes de producción

---

### 3.2 Variables SCSS Redundantes
**Archivo:** `src/scss/_variables.scss`

| Variable 1 | Variable 2 | Valor |
|------------|------------|-------|
| `$primary` | `$orange-primary` | `#ec6b00` |
| `$dark` | `$vintage-black` | `#3e3c38` |
| `$light` | `$background-color` / `$vintage-beige` | `#d3d0c3` |

**Solución:** Unificar nombres de variables

---

### 3.3 Comentario AGREGAR Pendiente
**Archivo:** `src/vue/content/pages/HomePage.vue` (línea 17)
```javascript
import DiagnosticSection from "/src/vue/sections/DiagnosticSection.vue"  // ← AGREGAR
```
**Impacto:** Comentario de desarrollo visible en código
**Solución:** Remover comentario

---

### 3.4 Variables SCSS Potencialmente No Usadas
**Archivo:** `src/scss/_variables.scss`
- `$fluor-green: #d9ff4e` - Sin uso encontrado
- `$vintage-orange: #cc7d43` - Uso limitado
- `$success: #038600` - Sin uso encontrado

---

### 3.5 Router TypeScript Obsoleto
**Archivo:** `src/router/index.ts` (20 líneas)
**Problema:** Existe archivo `.ts` obsoleto junto al `.js` activo
**Solución:** Eliminar `index.ts` si no se usa

---

## 4. MAPEO DE ENDPOINTS

### 4.1 Frontend -> Backend (Verificados)

| Frontend Endpoint | Backend Router | Estado |
|-------------------|----------------|--------|
| `/auth/login` | `auth.router` | ✓ OK |
| `/auth/register` | `auth.router` | ✓ OK |
| `/auth/me` | `auth.router` | ✓ OK |
| `/repairs` | `repair.router` | ✓ OK |
| `/repairs/{id}` | `repair.router` | ✓ OK |
| `/repairs/archived` | `repair.router` | ✓ OK |
| `/clients` | `clients.router` | ✓ OK |
| `/inventory` | `inventory.router` | ✓ OK |
| `/categories` | `category.router` | ✓ OK |
| `/instruments` | `instrument.router` | ✓ OK |
| `/diagnostic` | `diagnostic.router` | ✓ OK |
| `/quotations/estimate` | `quotation.router` | ✓ OK |
| `/appointments` | `appointment.router` | ✓ OK |
| `/stock-movements` | `stock_movement.router` | ✓ OK |
| `/contact` | `contact.router` | ✓ OK |
| `/newsletter` | `newsletter.router` | ✓ OK |
| `/tickets` | `tickets.router` | ✓ OK |
| `/purchase-requests` | `purchase_requests.router` | ✓ OK |
| `/signatures` | `signature.router` | ✓ OK |
| `/photo-requests` | `photo_requests.router` | ✓ OK |
| `/manuals` | `manuals.router` | ✓ OK |
| `/uploads` | `uploads.router` | ✓ OK |
| `/stats` | `stats.router` | ✓ OK |

### 4.2 Endpoints Backend Sin Uso en Frontend

| Endpoint | Router | Observación |
|----------|--------|-------------|
| `/warranties` | `warranty.router` | Sin UI |
| `/analytics` | `analytics.router` | Sin UI |
| `/payments` | `payments.router` | Sin UI |
| `/invoices` | `invoice.router` | Sin UI |
| `/tools` | `tools.router` | Sin UI |
| `/brands` | `brands.router` | Usado internamente |
| `/ai/analyze` | `ai.router` | Sin UI directa |

---

## 5. RUTAS VUE ROUTER

### 5.1 Rutas Públicas
| Path | Componente | Estado |
|------|------------|--------|
| `/` | HomePage | ✓ OK |
| `/license` | LicensePage | ✓ OK |
| `/policy` | PolicyPage | ✓ OK |
| `/terminos` | TermsPage | ✓ OK |
| `/privacidad` | PrivacyPage | ✓ OK |
| `/cotizador-ia` | CotizadorIAPage | ✓ OK |
| `/calculadoras` | CalculatorsPage | ✓ OK |

### 5.2 Rutas Autenticadas
| Path | Componente | Estado |
|------|------------|--------|
| `/dashboard` | DashboardPage | ✓ OK |
| `/repairs` | RepairsPage | ✓ OK |
| `/repairs/:id` | RepairDetailPage | ✓ OK |
| `/profile` | ProfilePage | ✓ OK |
| `/agendar` | SchedulePage | ✓ OK |

### 5.3 Rutas Admin
| Path | Componente | Estado |
|------|------------|--------|
| `/admin` | AdminDashboard | ✓ OK |
| `/admin/inventory` | InventoryPage | ✓ OK |
| `/admin/inventory/unified` | InventoryUnified | ✓ OK |
| `/admin/clients` | ClientsPage | ✓ OK |
| `/admin/repairs` | RepairsAdminPage | ✓ OK |
| `/admin/repairs/:id` | RepairDetailAdminPage | ✓ OK |
| `/admin/categories` | CategoriesPage | ✓ OK |
| `/admin/contact` | ContactMessagesPage | ✓ OK |
| `/admin/newsletter` | NewsletterSubscriptionsPage | ✓ OK |
| `/admin/appointments` | AppointmentsPage | ✓ OK |
| `/admin/tickets` | TicketsPage | ✓ OK |
| `/admin/purchase-requests` | PurchaseRequestsPage | ✓ OK |
| `/admin/archive` | ArchivePage | ✓ OK |
| `/admin/stats` | StatsPage | ⚠ SIN RUTA |
| `/admin/wizards` | WizardsPage | ⚠ SIN RUTA |
| `/admin/manuals` | ManualsPage | ⚠ REDIRECT ONLY |

### 5.4 Rutas Calculadoras (Lazy Loading)
| Path | Módulo | Estado |
|------|--------|--------|
| `/calc/555` | Timer555View | ✓ OK |
| `/calc/resistor-color` | ResistorColorView | ✓ OK |
| `/calc/smd-capacitor` | SmdCapacitorView | ✓ OK |
| `/calc/smd-resistor` | SmdResistorView | ✓ OK |
| `/calc/ohms-law` | OhmsLawView | ✓ OK |
| `/calc/temperature` | TemperatureView | ✓ OK |
| `/calc/number-system` | NumberSystemView | ✓ OK |
| `/calc/length` | LengthView | ✓ OK |
| `/calc/awg` | AwgView | ✓ OK |

---

## 6. ESTRUCTURA DE ARCHIVOS

### 6.1 Archivos Muy Pequeños (<15 líneas)
| Archivo | Líneas | Observación |
|---------|--------|-------------|
| `src/analytics/index.js` | 2 | Re-export, OK |
| `src/domain/common/calculationState.ts` | 7 | Type def, OK |
| `src/domain/common/types.ts` | 8 | Type def, OK |
| `src/scss/_theming.scss` | 10 | Config, OK |
| `src/validation/index.ts` | 10 | Export, OK |
| `src/composables/useStockMovements.js` | 11 | Wrapper, OK |
| `src/composables/useCategories.js` | 13 | Wrapper, OK |
| `src/composables/useDiagnostics.js` | 13 | Wrapper, OK |
| `src/composables/useInstruments.js` | 13 | Wrapper, OK |
| `src/composables/useRepairs.js` | 13 | Wrapper, OK |
| `src/composables/useUsers.js` | 13 | Wrapper, OK |

### 6.2 Archivos Más Grandes
| Archivo | Líneas |
|---------|--------|
| `DiagnosticWizard.vue` | 1,092 |
| `Timer555View.vue` | 846 |
| `SchedulePage.vue` | 817 |
| `DashboardPage.vue` | 764 |
| `ResistorColorView.vue` | 695 |
| `UnifiedIntakeForm.vue` | 671 |
| `ProfilePage.vue` | 666 |
| `SmdResistorView.vue` | 643 |
| `AboutSection.vue` | 623 |
| `QuotationResult.vue` | 609 |

---

## 7. GUARDIAS DE NAVEGACIÓN

### 7.1 Implementación Actual
```javascript
router.beforeEach(async (to, from, next) => {
  // ✓ Verifica autenticación
  // ✓ Protege rutas admin
  // ✓ Redirige guests autenticados
  // ✓ Maneja redirect post-login
})
```
**Estado:** Correctamente implementado

### 7.2 Rutas Protegidas
| Meta Flag | Rutas Afectadas | Estado |
|-----------|-----------------|--------|
| `requiresAuth` | dashboard, repairs, profile, agendar, admin/* | ✓ OK |
| `requiresAdmin` | admin/* | ✓ OK |
| `requiresGuest` | login, register, password-reset | ✓ OK |

---

## 8. CHECKLIST DE ACCIONES

### Críticas (Resolver inmediatamente)
- [ ] Corregir URL hardcodeada en `QuoteGenerator.vue`
- [ ] Eliminar duplicado de `search_router` en `router.py`
- [ ] Centralizar definición de `API_URL`

### Importantes (Resolver esta semana)
- [ ] Agregar rutas para StatsPage, WizardsPage
- [ ] Crear directorio `/public/images/avatars/` con `default.svg`
- [ ] Actualizar teléfono en páginas legales
- [ ] Condicionar enlace a backend docs
- [ ] Reemplazar iconos SVG placeholder

### Menores (Resolver antes de producción)
- [ ] Eliminar console.log de producción
- [ ] Unificar variables SCSS redundantes
- [ ] Eliminar comentario AGREGAR
- [ ] Eliminar `src/router/index.ts` obsoleto
- [ ] Revisar variables SCSS no usadas

---

## 9. ESTADISTICAS FINALES

```
FRONTEND:
├── Componentes Vue: 185
├── Archivos TypeScript: 27
├── Archivos JavaScript: 40
├── Archivos SCSS: 11
├── Rutas definidas: 32
└── Total líneas: ~30,836

BACKEND:
├── Routers: 29
├── Endpoints: ~11
├── Models: 34
├── Services: 18
└── Total líneas: ~105,799

TESTS:
├── Frontend (Vitest): Configurado
└── Backend (Pytest): Configurado
```

---

## 10. CONCLUSIONES

El proyecto **Cirujano de Sintetizadores** está en un estado **funcional** con arquitectura sólida. Los problemas encontrados son principalmente:

1. **Deuda técnica menor** - URLs hardcodeadas, código duplicado
2. **Contenido placeholder** - Teléfonos, iconos
3. **Código no accesible** - Páginas admin sin rutas

**Prioridad de corrección:**
1. Primero: Problemas críticos (URLs hardcodeadas)
2. Segundo: Rutas faltantes y assets
3. Tercero: Limpieza de código

**El proyecto está listo para QA** una vez resueltos los problemas críticos.

---

---

# PARTE II: MIGRANDO A SASS - GUIA DESDE CERO

## 11. DIAGNÓSTICO DEL ESTADO ACTUAL

### 11.1 Estructura Actual de SCSS
```
src/scss/
├── style.scss          # Archivo principal (24 líneas) - Entry point
├── _variables.scss     # Variables Bootstrap + custom (98 líneas)
├── _brand.scss         # Fuentes + paleta marca (208 líneas)
├── _mixins.scss        # Mixins custom (33 líneas)
├── _theming.scss       # Import para componentes Vue (10 líneas)
├── _reset.scss         # CSS Reset básico (29 líneas)
├── _layout.scss        # Layout general (138 líneas)
├── _typography.scss    # Tipografía (93 líneas)
├── _global.scss        # Estilos globales (49 líneas)
├── _admin.scss         # Estilos admin (32 líneas)
└── _public.scss        # Estilos público (111 líneas)
```

### 11.2 Problemas Identificados en SCSS Actual

| Problema | Severidad | Archivo(s) |
|----------|-----------|------------|
| Variables duplicadas (mismo color, distintos nombres) | Media | `_variables.scss`, `_brand.scss` |
| Reglas CSS en archivos de configuración | Media | `_brand.scss` (body, h1-h6) |
| No sigue arquitectura estándar (7-1) | Baja | Todos |
| Orden de imports puede causar conflictos | Media | `style.scss` |
| Variables no usadas | Baja | `_variables.scss` |
| Mezcla de responsabilidades | Media | `_layout.scss` |
| Estilos de componentes en archivos globales | Media | `_public.scss` |

### 11.3 Orden de Imports Actual (style.scss)
```scss
@import "variables";        // 1. Variables custom
@import "brand";            // 2. Fuentes + más variables (PROBLEMA: define reglas CSS)
@import "mixins";           // 3. Mixins
@import "reset";            // 4. Reset
@import "bootstrap";        // 5. Bootstrap completo
@import "fontawesome";      // 6. Iconos
@import "primeicons";       // 7. Más iconos
@import "layout";           // 8. Layout
@import "typography";       // 9. Tipografía
@import "global";           // 10. Global
@import "admin";            // 11. Admin
@import "public";           // 12. Público
```

**Problema principal:** Bootstrap se importa DESPUÉS de las variables, lo cual es correcto, pero `_brand.scss` define reglas CSS (`body {}`, `h1-h6 {}`) que pueden ser sobrescritas.

---

## 12. ARQUITECTURA SASS PROFESIONAL (PATRÓN 7-1)

### 12.1 ¿Qué es el Patrón 7-1?
El patrón 7-1 organiza SASS en 7 carpetas + 1 archivo principal:

```
scss/
├── abstracts/      # Variables, funciones, mixins (sin output CSS)
├── base/           # Reset, tipografía, animaciones base
├── components/     # Componentes reutilizables (botones, cards, forms)
├── layout/         # Estructura (header, footer, grid, navigation)
├── pages/          # Estilos específicos por página
├── themes/         # Temas (dark mode, admin, etc.)
├── vendors/        # Estilos de terceros (Bootstrap overrides)
└── main.scss       # Archivo principal que importa todo
```

### 12.2 Estructura Propuesta para CDS

```
src/scss/
│
├── abstracts/
│   ├── _index.scss           # Forward de todo el módulo
│   ├── _variables.scss       # TODAS las variables (unificadas)
│   ├── _functions.scss       # Funciones SASS custom
│   ├── _mixins.scss          # Mixins (responsive, etc.)
│   └── _placeholders.scss    # Placeholders (%extend)
│
├── base/
│   ├── _index.scss
│   ├── _reset.scss           # CSS Reset/Normalize
│   ├── _typography.scss      # Fuentes, tamaños, line-height
│   ├── _fonts.scss           # @font-face declarations
│   └── _animations.scss      # Keyframes globales
│
├── components/
│   ├── _index.scss
│   ├── _buttons.scss         # .btn-hero, .btn-primary-light
│   ├── _cards.scss           # .card, .wizard-card
│   ├── _forms.scss           # Inputs, selects, checkboxes
│   ├── _modals.scss          # Modales globales
│   ├── _spinners.scss        # Loaders, spinners
│   ├── _badges.scss          # Badges, tags
│   ├── _alerts.scss          # Alertas, toasts
│   └── _swiper.scss          # Swiper overrides
│
├── layout/
│   ├── _index.scss
│   ├── _grid.scss            # Sistema de grid custom
│   ├── _header.scss          # .foxy-header
│   ├── _footer.scss          # .foxy-footer
│   ├── _navigation.scss      # Navbar, sidebar
│   ├── _sections.scss        # .foxy-section
│   └── _containers.scss      # .container-xxl overrides
│
├── pages/
│   ├── _index.scss
│   ├── _home.scss            # Estilos específicos home
│   ├── _admin.scss           # Panel admin
│   ├── _calculators.scss     # Páginas de calculadoras
│   └── _auth.scss            # Login, register, reset
│
├── themes/
│   ├── _index.scss
│   ├── _default.scss         # Tema por defecto (vintage)
│   └── _dark.scss            # Tema oscuro (futuro)
│
├── vendors/
│   ├── _index.scss
│   ├── _bootstrap.scss       # Bootstrap customizado
│   └── _fontawesome.scss     # FontAwesome config
│
└── main.scss                 # Entry point
```

---

## 13. GUÍA DE MIGRACIÓN PASO A PASO

### FASE 1: Preparación (Sin romper nada)

#### Paso 1.1: Crear estructura de carpetas
```bash
cd src/scss
mkdir -p abstracts base components layout pages themes vendors
```

#### Paso 1.2: Crear archivos _index.scss vacíos
```bash
touch abstracts/_index.scss
touch base/_index.scss
touch components/_index.scss
touch layout/_index.scss
touch pages/_index.scss
touch themes/_index.scss
touch vendors/_index.scss
```

### FASE 2: Migrar Abstracts (Variables, Mixins, Functions)

#### Paso 2.1: Crear abstracts/_variables.scss (UNIFICADO)
```scss
// ============================================
// VARIABLES UNIFICADAS - Cirujano de Sintetizadores
// ============================================

// ---------------------------------------------
// 1. CONFIGURACIÓN DE TERCEROS
// ---------------------------------------------
$fa-font-path: "@fortawesome/fontawesome-free/webfonts";
$min-contrast-ratio: 1.5 !default;

// ---------------------------------------------
// 2. PALETA DE COLORES (Manual de Identidad)
// ---------------------------------------------

// Colores Primarios
$color-primary: #ec6b00;           // Orange (PANTONE 7577 C)
$color-primary-light: #e8935a;     // Orange pastel
$color-primary-dark: #cc5500;      // Orange oscuro

// Colores Neutros
$color-dark: #3e3c38;              // Vintage Black (PANTONE Black 7 C)
$color-light: #d3d0c3;             // Vintage Beige (PANTONE 7527 C)
$color-white: #ffffff;
$color-black: #000000;

// Colores Secundarios
$color-secondary: #ac612a;         // Warm brown
$color-accent: #c7814e;            // Accent tone
$color-muted: #8f9799;             // Neutral gray

// Colores de Estado
$color-success: #038600;
$color-warning: #ffc107;
$color-danger: #dc3545;
$color-info: #0dcaf0;

// Colores Especiales
$color-fluor-green: #d9ff4e;       // Acentos especiales

// ---------------------------------------------
// 3. MAPEO PARA BOOTSTRAP
// ---------------------------------------------
$primary: $color-primary;
$secondary: $color-secondary;
$success: $color-success;
$warning: $color-warning;
$danger: $color-danger;
$info: $color-info;
$light: $color-light;
$dark: $color-dark;

// ---------------------------------------------
// 4. TIPOGRAFÍA
// ---------------------------------------------

// Font Families
$font-family-base: 'Cervo Neue', system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
$font-family-heading: 'Steelfish', 'Cervo Neue', 'Oswald', serif;
$font-family-display: 'Steelfish', 'Impact', 'Arial Black', sans-serif;
$font-family-serif: 'Cormorant Garamond', 'Georgia', 'Times New Roman', serif;

// Font Sizes Base
$font-size-base: 1rem;
$font-size-sm: 0.875rem;
$font-size-lg: 1.125rem;

// Headings
$h1-font-size: 3rem;
$h2-font-size: 2.5rem;
$h3-font-size: 2rem;
$h4-font-size: 1.5rem;
$h5-font-size: 1.3rem;
$h6-font-size: 1.1rem;

// Line Heights
$line-height-base: 1.6;
$line-height-heading: 1.2;

// ---------------------------------------------
// 5. ESPACIADO Y DIMENSIONES
// ---------------------------------------------
$navbar-height: 86px;
$container-max-width: 1400px;
$section-padding-y: 5.5rem;
$section-padding-y-mobile: 3rem;

// ---------------------------------------------
// 6. BREAKPOINTS CUSTOM
// ---------------------------------------------
$breakpoint-multipliers: (
    xxxxl: 1.15,    // >1920px - 4K
    xxxl: 1.1,      // Desktop grande
    xxl: 1.0,       // Desktop
    xl: 0.95,       // Laptop
    lg: 0.95,       // Tablet landscape
    md: 1.0,        // Tablet portrait
    sm: 1.05        // Mobile
);

// ---------------------------------------------
// 7. COLORES DE TEXTO
// ---------------------------------------------
$text-color: $color-dark;
$text-color-muted: #5a5652;
$text-color-light: #adb5bd;
$text-color-inverse: $color-white;

// ---------------------------------------------
// 8. FONDOS
// ---------------------------------------------
$bg-body: $color-dark;
$bg-light: $color-light;
$bg-paper: #f5f5f5;

// ---------------------------------------------
// 9. LIGHT SHADES (para utilities)
// ---------------------------------------------
$light-1: #f8f9fa;
$light-2: #e9ecef;
$light-3: #dee2e6;
$light-4: #ced4da;
$light-5: #adb5bd;
$light-6: #6c757d;
$light-7: #495057;

// ---------------------------------------------
// 10. SOMBRAS
// ---------------------------------------------
$shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
$shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
$shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
$shadow-trace: rgba(0, 0, 0, 0.1) 5px 5px, rgba(10, 10, 10, 0.15) 10px 10px;

// ---------------------------------------------
// 11. TRANSICIONES
// ---------------------------------------------
$transition-base: all 0.3s ease;
$transition-fast: all 0.15s ease;
$transition-slow: all 0.5s ease;

// ---------------------------------------------
// 12. BORDER RADIUS
// ---------------------------------------------
$border-radius-sm: 4px;
$border-radius-md: 8px;
$border-radius-lg: 12px;
$border-radius-pill: 50rem;
```

#### Paso 2.2: Crear abstracts/_mixins.scss
```scss
// ============================================
// MIXINS - Cirujano de Sintetizadores
// ============================================

// ---------------------------------------------
// 1. RESPONSIVE HELPERS
// ---------------------------------------------

// Normalizar breakpoints extendidos a Bootstrap
@function normalize-breakpoint($bp) {
    @if $bp == 'xxxl' or $bp == 'xxxxl' { @return 'xxl'; }
    @return $bp;
}

// Generar estilos dinámicos con hash
@mixin dynamic-styles-hash($styles-hash) {
    @each $breakpoint, $styles in $styles-hash {
        $bp: normalize-breakpoint($breakpoint);
        @include media-breakpoint-down($bp) {
            @each $property, $value in $styles {
                #{$property}: $value;
            }
        }
    }
}

// Generar estilos con multiplicadores
@mixin dynamic-styles-multipliers($base-sizes, $multipliers) {
    @each $breakpoint, $multiplier in $multipliers {
        $bp: normalize-breakpoint($breakpoint);
        @include media-breakpoint-down($bp) {
            @each $property, $value in $base-sizes {
                #{$property}: $value * $multiplier;
            }
        }
    }
}

// ---------------------------------------------
// 2. FLEXBOX SHORTCUTS
// ---------------------------------------------
@mixin flex-center {
    display: flex;
    align-items: center;
    justify-content: center;
}

@mixin flex-between {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

@mixin flex-column {
    display: flex;
    flex-direction: column;
}

// ---------------------------------------------
// 3. TYPOGRAPHY
// ---------------------------------------------
@mixin heading-style {
    font-family: $font-family-heading;
    font-weight: 700;
    line-height: $line-height-heading;
    color: $text-color;
}

@mixin text-truncate {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

@mixin text-clamp($lines: 2) {
    display: -webkit-box;
    -webkit-line-clamp: $lines;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

// ---------------------------------------------
// 4. INTERACTIVE STATES
// ---------------------------------------------
@mixin hover-lift {
    transition: transform 0.2s ease, box-shadow 0.2s ease;

    &:hover {
        transform: translateY(-2px);
        box-shadow: $shadow-md;
    }
}

@mixin focus-ring {
    &:focus {
        outline: none;
        box-shadow: 0 0 0 3px rgba($color-primary, 0.25);
    }
}

// ---------------------------------------------
// 5. SCROLLBAR CUSTOM
// ---------------------------------------------
@mixin custom-scrollbar($width: 8px, $track-color: transparent, $thumb-color: $light-6) {
    &::-webkit-scrollbar {
        width: $width;
        height: $width;
    }

    &::-webkit-scrollbar-track {
        background: $track-color;
    }

    &::-webkit-scrollbar-thumb {
        background: $thumb-color;
        border-radius: $width / 2;

        &:hover {
            background: darken($thumb-color, 10%);
        }
    }
}

// ---------------------------------------------
// 6. ASPECT RATIO (Legacy support)
// ---------------------------------------------
@mixin aspect-ratio($width, $height) {
    position: relative;

    &::before {
        content: "";
        display: block;
        padding-top: ($height / $width) * 100%;
    }

    > * {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
    }
}

// ---------------------------------------------
// 7. VISUALLY HIDDEN (Accessibility)
// ---------------------------------------------
@mixin visually-hidden {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
}
```

#### Paso 2.3: Crear abstracts/_functions.scss
```scss
// ============================================
// FUNCIONES SASS - Cirujano de Sintetizadores
// ============================================

// Obtener color de la paleta de marca
@function brand-color($key) {
    $colors: (
        'primary': $color-primary,
        'secondary': $color-secondary,
        'accent': $color-accent,
        'dark': $color-dark,
        'light': $color-light,
        'muted': $color-muted
    );

    @if map-has-key($colors, $key) {
        @return map-get($colors, $key);
    }

    @warn "Color '#{$key}' no encontrado en paleta.";
    @return null;
}

// Convertir px a rem
@function rem($px, $base: 16) {
    @return ($px / $base) * 1rem;
}

// Calcular contraste de texto
@function text-contrast($bg-color) {
    $luminance: (red($bg-color) * 0.299 + green($bg-color) * 0.587 + blue($bg-color) * 0.114) / 255;

    @if $luminance > 0.5 {
        @return $color-dark;
    } @else {
        @return $color-white;
    }
}

// Obtener shade de light palette
@function light-shade($index) {
    $shades: ($light-1, $light-2, $light-3, $light-4, $light-5, $light-6, $light-7);

    @if $index >= 1 and $index <= 7 {
        @return nth($shades, $index);
    }

    @warn "Shade index debe ser entre 1 y 7.";
    @return $light-4;
}
```

#### Paso 2.4: Crear abstracts/_index.scss
```scss
// Forward all abstracts
@forward 'variables';
@forward 'functions';
@forward 'mixins';
```

### FASE 3: Migrar Base (Reset, Fonts, Typography)

#### Paso 3.1: Crear base/_fonts.scss
```scss
// ============================================
// WEBFONTS - Cirujano de Sintetizadores
// ============================================

// Cervo Neue - Familia completa
@font-face {
    font-family: 'Cervo Neue';
    src: url('/fonts/CERVO/CervoNeueCon-Thin.woff2') format('woff2'),
         url('/fonts/CERVO/CervoNeueCon-Thin.woff') format('woff');
    font-weight: 100;
    font-style: normal;
    font-display: swap;
}

// ... (resto de pesos: 200, 400, 500, 600, 800, 900 con sus italics)

@font-face {
    font-family: 'Cervo Neue';
    src: url('/fonts/CERVO/CervoNeueCon-Regular.woff2') format('woff2'),
         url('/fonts/CERVO/CervoNeueCon-Regular.woff') format('woff');
    font-weight: 400;
    font-style: normal;
    font-display: swap;
}

@font-face {
    font-family: 'Cervo Neue';
    src: url('/fonts/CERVO/CervoNeueCon-SemiBold.woff2') format('woff2'),
         url('/fonts/CERVO/CervoNeueCon-SemiBold.woff') format('woff');
    font-weight: 600;
    font-style: normal;
    font-display: swap;
}

@font-face {
    font-family: 'Cervo Neue';
    src: url('/fonts/CERVO/CervoNeueCon-XtrBold.woff2') format('woff2'),
         url('/fonts/CERVO/CervoNeueCon-XtrBold.woff') format('woff');
    font-weight: 800;
    font-style: normal;
    font-display: swap;
}

// Steelfish - Display
@font-face {
    font-family: 'Steelfish';
    src: url('/fonts/steelfish rg.woff2') format('woff2'),
         url('/fonts/steelfish rg.woff') format('woff');
    font-weight: 700;
    font-style: normal;
    font-display: swap;
}
```

#### Paso 3.2: Crear base/_reset.scss
```scss
// ============================================
// CSS RESET - Cirujano de Sintetizadores
// ============================================

*,
*::before,
*::after {
    box-sizing: border-box;
}

html,
body {
    margin: 0;
    padding: 0;
}

html {
    scroll-padding-top: $navbar-height;
    font-size: clamp(16px, 0.8vw + 14px, 20px);
}

body {
    font-family: $font-family-base;
    font-size: $font-size-base;
    line-height: $line-height-base;
    color: $text-color;
    background-color: $bg-body;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

img,
picture,
video,
canvas,
svg {
    display: block;
    max-width: 100%;
    height: auto;
}

input,
button,
textarea,
select {
    font: inherit;
}

a {
    color: lighten($color-primary, 10%);
    text-decoration: none;

    &:hover {
        color: lighten($color-primary, 15%);
    }
}

// Prevent horizontal overflow (mobile fix)
html,
body {
    overflow-x: hidden;
    overscroll-behavior-y: contain;
}
```

#### Paso 3.3: Crear base/_typography.scss
```scss
// ============================================
// TIPOGRAFÍA - Cirujano de Sintetizadores
// ============================================

// Headings
h1, h2, h3, h4, h5, h6 {
    font-family: $font-family-heading;
    font-weight: 700;
    line-height: $line-height-heading;
    color: $text-color;
    margin-top: 0;
}

h1 { font-size: clamp(2.4rem, 3.6vw + 0.6rem, 3.4rem); }
h2 { font-size: clamp(2rem, 2.8vw + 0.5rem, 2.8rem); }
h3 { font-size: clamp(1.6rem, 2.1vw + 0.3rem, 2.2rem); }
h4 { font-size: $h4-font-size; }
h5 { font-size: $h5-font-size; }
h6 { font-size: $h6-font-size; }

// Paragraphs
p {
    margin-top: 0;
    margin-bottom: 1rem;
    color: $text-color;
}

// Text utilities
.text-muted { color: $text-color-muted !important; }
.text-light { color: $text-color-light !important; }
.text-primary { color: $color-primary !important; }

// Lead text
.lead {
    font-size: 1.2rem;
    font-weight: 400;
}

.lead-2 {
    font-size: 1.4rem;
    font-weight: 400;
}

// Reading width
.readable {
    max-width: 75ch;
    margin-left: auto;
    margin-right: auto;
}

// Selection
::selection {
    color: $color-dark;
    background: lighten($color-primary, 30%);
}

::-moz-selection {
    color: $color-dark;
    background: $color-primary;
}
```

### FASE 4: Crear main.scss Nuevo

```scss
// ============================================
// MAIN.SCSS - Entry Point
// Cirujano de Sintetizadores
// ============================================

// 1. ABSTRACTS (sin output CSS)
// Usar @use para módulos modernos
@use 'abstracts' as *;

// 2. VENDORS - Configuración antes de Bootstrap
@import 'vendors/bootstrap';
@import 'vendors/fontawesome';

// 3. BASE
@import 'base/fonts';
@import 'base/reset';
@import 'base/typography';

// 4. LAYOUT
@import 'layout/containers';
@import 'layout/grid';
@import 'layout/header';
@import 'layout/footer';
@import 'layout/navigation';
@import 'layout/sections';

// 5. COMPONENTS
@import 'components/buttons';
@import 'components/cards';
@import 'components/forms';
@import 'components/modals';
@import 'components/spinners';
@import 'components/swiper';

// 6. PAGES
@import 'pages/home';
@import 'pages/admin';
@import 'pages/calculators';
@import 'pages/auth';

// 7. THEMES
@import 'themes/default';

// 8. UTILITIES (al final para máxima especificidad)
// Bootstrap utilities ya incluidas
```

---

## 14. CONVENCIONES Y MEJORES PRÁCTICAS

### 14.1 Nomenclatura de Archivos
```
✓ _variables.scss      # Con guión bajo = partial (no compila solo)
✓ _header.scss         # Componente específico
✗ variables.scss       # Sin guión bajo = archivo compilable
✗ _Variables.scss      # No usar mayúsculas
✗ _variablesNew.scss   # No usar camelCase
```

### 14.2 Nomenclatura de Variables
```scss
// ✓ CORRECTO
$color-primary: #ec6b00;
$font-size-base: 1rem;
$navbar-height: 86px;
$shadow-md: 0 4px 6px rgba(0,0,0,0.1);

// ✗ INCORRECTO
$primary: #ec6b00;              // Muy genérico
$orangePrimary: #ec6b00;        // No usar camelCase
$NAVBAR_HEIGHT: 86px;           // No usar SCREAMING_CASE
$vintage-black: #3e3c38;        // Evitar nombres descriptivos de color
```

### 14.3 Nomenclatura de Clases (BEM)
```scss
// Block__Element--Modifier
.foxy-header { }                    // Block
.foxy-header__logo { }              // Element
.foxy-header__logo--large { }       // Modifier
.foxy-header--sticky { }            // Block modifier

// Componentes con prefijo del proyecto
.cds-button { }
.cds-card { }
.cds-modal { }
```

### 14.4 Orden de Propiedades CSS
```scss
.component {
    // 1. Posicionamiento
    position: relative;
    top: 0;
    z-index: 10;

    // 2. Display y Box Model
    display: flex;
    width: 100%;
    padding: 1rem;
    margin: 0;

    // 3. Tipografía
    font-family: $font-family-base;
    font-size: 1rem;
    color: $text-color;

    // 4. Visual
    background: $color-light;
    border: 1px solid $color-dark;
    border-radius: $border-radius-md;

    // 5. Misc
    transition: $transition-base;
    cursor: pointer;
}
```

### 14.5 Anidamiento (Máximo 3 niveles)
```scss
// ✓ CORRECTO (máximo 3 niveles)
.foxy-header {
    .container {
        .logo {
            img { }
        }
    }
}

// ✗ INCORRECTO (demasiado anidado)
.foxy-header {
    .container {
        .logo {
            .wrapper {
                img {
                    &:hover { }  // 6 niveles!
                }
            }
        }
    }
}
```

---

## 15. ARCHIVO _theming.scss PARA COMPONENTES VUE

### 15.1 Uso en Componentes Vue
El archivo `_theming.scss` se importa en cada componente Vue que necesite variables/mixins:

```vue
<style lang="scss" scoped>
@import "@/scss/abstracts";  // Nueva forma

// o si usas la estructura actual:
@import "/src/scss/_theming.scss";

.my-component {
    color: $color-primary;
    @include flex-center;
}
</style>
```

### 15.2 Contenido de _theming.scss (Actualizado)
```scss
// ============================================
// THEMING - Import para componentes Vue
// ============================================

// Bootstrap functions (necesarias para manipular colores)
@import "/node_modules/bootstrap/scss/functions";

// Nuestras variables y mixins
@import "./abstracts/variables";
@import "./abstracts/functions";
@import "./abstracts/mixins";

// Bootstrap variables (para acceder a $grid-breakpoints, etc.)
@import "/node_modules/bootstrap/scss/variables";
@import "/node_modules/bootstrap/scss/mixins";
```

---

## 16. CHECKLIST DE MIGRACIÓN

### Fase 1: Estructura (1-2 horas)
- [ ] Crear carpetas: `abstracts/`, `base/`, `components/`, `layout/`, `pages/`, `themes/`, `vendors/`
- [ ] Crear archivos `_index.scss` en cada carpeta
- [ ] NO eliminar archivos actuales todavía

### Fase 2: Abstracts (2-3 horas)
- [ ] Unificar variables en `abstracts/_variables.scss`
- [ ] Migrar mixins a `abstracts/_mixins.scss`
- [ ] Crear `abstracts/_functions.scss`
- [ ] Eliminar variables duplicadas

### Fase 3: Base (1-2 horas)
- [ ] Separar `@font-face` en `base/_fonts.scss`
- [ ] Limpiar reset en `base/_reset.scss`
- [ ] Organizar tipografía en `base/_typography.scss`

### Fase 4: Layout (2-3 horas)
- [ ] Extraer estilos de `.foxy-header` a `layout/_header.scss`
- [ ] Extraer estilos de `.foxy-footer` a `layout/_footer.scss`
- [ ] Extraer estilos de `.foxy-section` a `layout/_sections.scss`
- [ ] Mover `.container-xxl` overrides a `layout/_containers.scss`

### Fase 5: Components (2-3 horas)
- [ ] Crear `components/_buttons.scss` con `.btn-hero`, etc.
- [ ] Crear `components/_swiper.scss` con overrides de Swiper
- [ ] Identificar más componentes reutilizables

### Fase 6: Pages (1-2 horas)
- [ ] Mover estilos de `_admin.scss` a `pages/_admin.scss`
- [ ] Mover estilos de `_public.scss` a `pages/_home.scss`

### Fase 7: Actualizar Imports (1 hora)
- [ ] Crear nuevo `main.scss` con imports ordenados
- [ ] Actualizar `_theming.scss` para componentes Vue
- [ ] Probar que todo compila sin errores

### Fase 8: Limpieza (1 hora)
- [ ] Eliminar archivos SCSS antiguos no usados
- [ ] Verificar que no hay estilos rotos
- [ ] Documentar estructura final

---

## 17. COMANDOS ÚTILES

### Verificar compilación SASS
```bash
# Compilar y ver errores
npx sass src/scss/main.scss dist/test.css --no-source-map

# Watch mode para desarrollo
npx sass --watch src/scss/main.scss:dist/style.css
```

### Encontrar variables no usadas
```bash
# Buscar definiciones de variables
grep -r '^\$' src/scss/ --include="*.scss" | grep -v '//'

# Buscar usos de una variable específica
grep -r '\$color-primary' src/ --include="*.scss" --include="*.vue"
```

### Verificar imports circulares
```bash
# Listar todos los @import
grep -r '@import' src/scss/ --include="*.scss"
```

---

## 18. RECURSOS Y REFERENCIAS

### Documentación
- [Sass Guidelines](https://sass-guidelin.es/)
- [7-1 Pattern](https://sass-guidelin.es/#the-7-1-pattern)
- [Bootstrap SASS](https://getbootstrap.com/docs/5.3/customize/sass/)

### Herramientas
- [Sass Lint](https://github.com/sasstools/sass-lint) - Linter para SASS
- [Stylelint](https://stylelint.io/) - Linter moderno CSS/SCSS

---

*Sección añadida a la auditoría - 26/01/2026*
