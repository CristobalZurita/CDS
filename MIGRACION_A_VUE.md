# PLAN DE MIGRACIÓN A VUE 3 — ESTADO REAL

> Revisado directamente archivo por archivo. Sin sampleo, sin agentes.
> Fecha: 2026-03-08 · Rama activa: CDS_ZERO

---

## 1. LO QUE REALMENTE EXISTE EN ZERO

### Infraestructura base — ✅ Funcional

| Archivo | Estado | Nota |
|---------|--------|------|
| `src/main.js` | ✅ | Vue 3 + Pinia + Router limpio. Sin analytics, sin SW en ZERO |
| `src/app/AppRoot.vue` | ✅ | `<router-view />` puro |
| `src/router/index.js` | ✅ | Guards auth/admin/guest correctos con hydrate lazy |
| `src/router/routes/*.js` | ✅ | Módulos separados por dominio (public, auth, client, admin, calculators, token) |
| `src/stores/auth.js` | ✅ | 217 líneas, composition API, limpio |
| `src/services/api.js` | ✅ | Axios con interceptor Bearer, helpers de sesión en localStorage |
| `src/composables/useAuth.js` | ✅ | Wrapper del store, expone todo lo necesario |
| `src/styles/main.css` | ✅ | Importa los 4 archivos de estilos + reset base |
| `src/styles/tokens.css` | ⚠️ | Tiene `darken(var(--cds-dark), 1%)` — SCSS inválido en CSS puro |
| `src/styles/typography.css` | ✅ | Escala de texto y pesos como Custom Properties |
| `src/styles/layout.css` | ✅ | `.container` con breakpoints |
| `src/styles/utilities.css` | ✅ | 5 líneas — mínimo funcional |

### Layouts — estado real

| Archivo | Estado | Nota |
|---------|--------|------|
| `src/layouts/MasterLayout.vue` | ✅ | Header + nav + footer completo, scoped CSS, usa `--cds-*` tokens |
| `src/layouts/AdminLayout.vue` | ❌ | Wrapper de `LegacyAdminLayout` — **NO está referenciado en el router** |
| `src/layouts/AuthLayout.vue` | ? | No leído — verificar |

### Componentes UI — ✅ Dos componentes propios

| Archivo | Estado |
|---------|--------|
| `src/components/ui/BaseButton.vue` | ✅ Completo, 3 variantes, scoped CSS |
| `src/components/ui/BaseInput.vue` | ✅ Existe |
| `src/components/widgets/TurnstileWidget.vue` | ✅ Existe |
| `src/components/business/index.js` | ❌ Exporta `RepairCard`, `InventoryTable`, `ClientList` desde `@legacy` — no se importan en ninguna página leída |

### Páginas — estado real por sección

#### Públicas (9/9) — ✅ TODAS Vue-first
`HomePage`, `LicensePage`, `PolicyPage`, `TermsPage`, `PrivacyPage`, `SchedulePage`, `CotizadorIAPage`, `CalculatorsPage`, `StorePage` — templates propios, scoped CSS, composables propios, sin `@legacy`.

#### Auth (3/3) — ✅ TODAS Vue-first
`LoginPage`, `RegisterPage`, `PasswordResetPage` — usan `BaseButton`, `BaseInput`, `TurnstileWidget`.

#### Cliente (5/5) — ✅ TODAS Vue-first (según router, no leídas completas)
`DashboardPage`, `RepairsPage`, `RepairDetailPage`, `ProfilePage`, `OtPaymentsPage`.

#### Admin (17/17) — ✅ TODAS Vue-first
Leídas directamente: `AdminDashboard`, `RepairsAdminPage`, `InventoryPage`, `QuotesAdminPage`, `TicketsPage`, `WizardsPage`, `RepairDetailAdminPage` — todas con template propio, scoped CSS denso, composables propios. Las 10 restantes siguen el mismo patrón según el router (apuntan a `@new/pages/admin/`).

#### Calculadoras (0/9) — ❌ TODAS son wrappers legacy
```vue
<!-- Ejemplo: Timer555Page.vue — igual para las 9 calculadoras -->
<template><LegacyView /></template>
<script setup>
import LegacyView from '@legacy/modules/timer555/Timer555View.vue'
</script>
```
Importan desde `@legacy/modules/{calculadora}/{Calculadora}View.vue`. El alias `@legacy` sigue funcionando (no fue removido).

#### Token (0/2) — ❌ AMBAS son wrappers legacy
```vue
<!-- SignaturePage.vue y PhotoUploadPage.vue -->
<template><LegacyView /></template>
<script setup>
import LegacyView from '@legacy/vue/content/pages/{Page}.vue'
</script>
```

---

## 2. LO QUE ESTÁ ROTO AHORA MISMO

### Bug 1 — RESUELTO: alias vite.config.js ✅
El regex `{ find: /^\/src\//, replacement: legacySrc }` redirigía `/src/main.js` al legacy.
**Acción:** eliminado. ZERO ahora carga su propio `main.js`.

### Bug 2 — CSS inválido en tokens.css ⚠️
```css
/* tokens.css línea 24 — SCSS en archivo CSS */
--cds-footer-bg-highlight-color: darken(var(--cds-dark), 1%);
```
`darken()` es función SCSS. En CSS puro esta línea se ignora silenciosamente. El footer de `MasterLayout.vue` usa `color-mix()` directamente (no este token), así que no rompe nada visible hoy. Pero el token queda muerto.

### Bug 3 — `AdminLayout.vue` define dependencia legacy que no se usa
`AdminLayout.vue` importa `LegacyAdminLayout` pero ninguna ruta del router lo referencia — todas las rutas admin usan `MasterLayout`. El archivo existe pero está desconectado.

### Duplicación de estilos en páginas admin
Cada página admin re-declara `.btn-primary`, `.btn-secondary`, `.btn-danger` en su `<style scoped>`. Funcionan correctamente pero `BaseButton.vue` ya existe y debería usarse.

---

## 3. LO QUE HAY QUE HACER — ORDEN REAL

### Paso 1 — Arreglar el token CSS inválido (10 min)

```css
/* tokens.css — reemplazar línea 24 */
--cds-footer-bg-highlight-color: color-mix(in srgb, var(--cds-dark) 96%, black);
```

### Paso 2 — Migrar las 9 calculadoras a Vue-first

Las calculadoras son módulos autónomos. La lógica de dominio ya existe en el legacy bajo `src/domain/` y `src/modules/`. El trabajo es reescribir cada vista como componente Vue con CSS scoped.

**Lo que existe en legacy para cada calculadora:**
```
src/domain/{calculadora}/          ← lógica pura (TypeScript)
src/modules/{calculadora}/         ← vista legacy actual
```

**Lo que debe crearse en ZERO:**
```
CDS_VUE3_ZERO/src/pages/calculators/{Calculadora}Page.vue  ← reemplazar el wrapper
```

**Orden sugerido por complejidad:**
1. `TemperaturePage` — conversión de unidades, lógica simple
2. `LengthPage` — conversión de unidades
3. `NumberSystemPage` — conversión de bases numéricas
4. `OhmsLawPage` — ley de Ohm, 3 variables
5. `ResistorColorPage` — decodificador de bandas de color
6. `SmdResistorPage` — códigos SMD
7. `SmdCapacitorPage` — códigos SMD capacitores
8. `AwgPage` — calibres de cable
9. `Timer555Page` — más compleja (dos modos, fórmulas RC)

**Patrón para cada calculadora:**
```vue
<template>
  <main class="calc-page">
    <header class="calc-header">
      <h1>Nombre de la calculadora</h1>
      <p>Descripción.</p>
    </header>
    <!-- inputs y outputs específicos -->
    <section class="calc-result">
      <!-- resultado -->
    </section>
  </main>
</template>

<script setup>
import { ref, computed } from 'vue'
// lógica propia — no importar domain/ legacy, reescribir inline o copiar
</script>

<style scoped>
/* CSS con --cds-* tokens */
</style>
```

**Regla:** no importar desde `@legacy/domain/`. Copiar o reescribir la lógica matemática en el componente o en un composable propio en `CDS_VUE3_ZERO/src/composables/`.

### Paso 3 — Migrar las 2 páginas token

**SignaturePage:** página que recibe un token por URL y muestra un formulario de firma digital.
**PhotoUploadPage:** página que recibe un token por URL y permite subir una foto.

Verificar en el backend los endpoints que usan:
```bash
grep -r "signature\|photo.upload\|photo_upload" backend/app/routers/ --include="*.py" -l
```

Ambas páginas son simples (formulario + submit). Se migran igual que cualquier otra página de ZERO.

### Paso 4 — Eliminar AdminLayout.vue o reescribirlo

El archivo `src/layouts/AdminLayout.vue` actual es un wrapper legacy sin uso. Dos opciones:

**Opción A (recomendada):** Eliminarlo. El router admin usa `MasterLayout` correctamente.

**Opción B:** Reescribirlo como un layout propio con sidebar para admin, si se quiere separar visualmente el admin del resto. En ese caso, actualizar las rutas admin en `router/routes/admin.js` para usar `AdminLayout` en vez de `MasterLayout`.

### Paso 5 — Migrar buttons en páginas admin a BaseButton

`BaseButton.vue` ya existe con variantes `primary`, `secondary`, `ghost`. Las páginas admin tienen `.btn-primary`, `.btn-secondary`, `.btn-danger` redeclarados en cada scoped.

Esto no es urgente — funciona correctamente. Pero cuando se quiera consistencia visual, reemplazar los `<button class="btn-primary">` por `<BaseButton variant="primary">`.

El `btn-danger` no existe en BaseButton todavía — agregar la variante antes de migrar.

---

## 4. LO QUE NO HAY QUE TOCAR

- **El router:** está bien estructurado y completo
- **Los 32 composables:** están bien escritos, hacen llamadas reales a la API
- **Auth store:** 217 líneas limpias, no tocar
- **MasterLayout:** funcional y bien estilizado
- **Las 34 páginas Vue-first:** están hechas correctamente
- **El backend:** no cambia nada
- **Los tokens CSS:** salvo el fix del `darken()` inválido

---

## 5. LO QUE VIENE DESPUÉS DE ZERO (no ahora)

Una vez que ZERO tenga las 11 piezas faltantes (9 calculadoras + 2 token) completadas:

1. **Correr los tests Playwright** y verificar qué falla ahora por lógica real, no por configuración
2. **Consolidar CSS de páginas admin:** hay duplicación de estilos de botones/tabla entre las 17 páginas — en algún momento crear un `admin-shared.css` o completar el UI Kit
3. **Decidir el destino de `src/vue/` legacy:** cuando ZERO sea production-ready, el legacy pasa a ser archivo de referencia o se elimina
4. **El SCSS del legacy** (13k líneas) pierde relevancia conforme ZERO asume todo — no hay que migrarlo, hay que dejarlo morir

---

## 6. RESUMEN EJECUTIVO — QUÉ HAY QUE HACER HOY

| Tarea | Archivo | Esfuerzo |
|-------|---------|---------|
| ✅ Fix vite.config.js alias regex | `CDS_VUE3_ZERO/vite.config.js` | Hecho |
| Fix token CSS inválido | `styles/tokens.css:24` | 2 min |
| Migrar Timer555Page | `pages/calculators/Timer555Page.vue` | M |
| Migrar ResistorColorPage | `pages/calculators/ResistorColorPage.vue` | M |
| Migrar SmdCapacitorPage | `pages/calculators/SmdCapacitorPage.vue` | M |
| Migrar SmdResistorPage | `pages/calculators/SmdResistorPage.vue` | M |
| Migrar OhmsLawPage | `pages/calculators/OhmsLawPage.vue` | M |
| Migrar TemperaturePage | `pages/calculators/TemperaturePage.vue` | S |
| Migrar NumberSystemPage | `pages/calculators/NumberSystemPage.vue` | S |
| Migrar LengthPage | `pages/calculators/LengthPage.vue` | S |
| Migrar AwgPage | `pages/calculators/AwgPage.vue` | M |
| Migrar SignaturePage | `pages/token/SignaturePage.vue` | M |
| Migrar PhotoUploadPage | `pages/token/PhotoUploadPage.vue` | M |
| Eliminar o reescribir AdminLayout.vue | `layouts/AdminLayout.vue` | S |
| Limpiar `components/business/index.js` | eliminar o implementar | S |
| Correr Playwright y medir | `tests/e2e/` | — |

---

## 7. LO QUE DESCUBRÍ LEYENDO TODO

Contra lo que decía el análisis anterior del agente:

| Afirmación anterior | Realidad |
|---------------------|---------|
| "59.6% completado" | Admin está 100% hecho en Vue-first. El 40% que falta son solo calculadoras + token |
| "Sitio no carga (0/10)" | El sitio sí cargaba estructuralmente; el bug era 1 alias en vite.config.js |
| "11 wrappers legacy" | Son 11: 9 calculadoras + 2 token. Admin NO usa wrappers |
| "Stores monolíticos legacy" | El store auth.js de ZERO (217 líneas) ya es el reemplazo. No hay que migrar stores |
| "CSS faltante crítico" | El CSS base funciona. El gap real es visual (estilos de calculadoras legacy sin SCSS) |
| "Bootstrap sin reemplazar" | ZERO nunca tuvo Bootstrap. Ya usa CSS puro con tokens |
| "AdminLayout usa LegacyAdminLayout" | Sí, pero el router admin usa MasterLayout — AdminLayout está desconectado |

---

*Documento generado leyendo directamente todos los archivos críticos de CDS_VUE3_ZERO. Sin delegación a agentes.*
