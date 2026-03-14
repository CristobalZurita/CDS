# ANÁLISIS FORENSE - DUPLICADOS Y CÓDIGO MUERTO

**Proyecto:** CDS_VUE3_ZERO (Cirujano de Sintetizadores)  
**Fecha:** Marzo 2026  
**Metodología:** Búsqueda exhaustiva con grep, find, diff, análisis de imports  
**Archivos analizados:** 176 archivos (.vue, .js, .ts)  

---

## RESUMEN EJECUTIVO

| Categoría | Hallazgos | Líneas afectadas | Severidad |
|-----------|-----------|------------------|-----------|
| Funciones duplicadas | 13 funciones repetidas | ~400 líneas | 🔴 Crítico |
| Constantes duplicadas | 5 estructuras repetidas | ~150 líneas | 🔴 Crítico |
| Componentes duplicados | 2 componentes idénticos | 232 líneas | 🟠 Alto |
| Componentes muertos | 8 componentes sin uso | 1,083 líneas | 🟠 Alto |
| Composables huérfanos | 0 (todos usados) | 0 | ✅ OK |
| Páginas huérfanas | 0 (todas en router) | 0 | ✅ OK |
| Layouts vacíos | 2 layouts sin valor | 23 líneas | 🟡 Medio |
| Options duplicadas | 18 estructuras similares | ~270 líneas | 🟡 Medio |

**Total estimado de código duplicado/muerto:** ~2,158 líneas

---

## PARTE 1: FUNCIONES DUPLICADAS (ANÁLISIS FORENSE)

### 1.1 normalizeDecimal - EL PEOR CULPABLE

**Repeticiones:** 13 veces en 13 archivos diferentes  
**Líneas duplicadas:** ~39 líneas (3 líneas × 13)  
**Ubicación correcta:** `src/utils/format.js` (ya existe, líneas 10-13)

```javascript
// FUNCIÓN ORIGINAL EN utils/format.js
export function normalizeDecimal(value, decimals = 6) {
  if (!Number.isFinite(value)) return null
  return Number(value.toFixed(decimals))
}
```

**Archivos que duplican esta función:**

| Archivo | Líneas | Variación | Idéntica? |
|---------|--------|-----------|-----------|
| useOhmsLawCalculator.js | 1-4 | decimals = 6 | ✅ Sí |
| usePowerCalculator.js | 1-4 | decimals = 6 | ✅ Sí |
| useVoltageDividerCalculator.js | 1-4 | decimals = 6 | ✅ Sí |
| useAwgCalculator.js | 1-4 | decimals = 6 | ✅ Sí |
| useSmdResistorCalculator.js | 1-4 | decimals = 6 | ✅ Sí |
| useOpAmpCalculator.js | 1-4 | decimals = 6 | ✅ Sí |
| useResistorColorCalculator.js | 80-83 | decimals = 6 (inline) | ⚠️ Ligeramente diferente |
| useReactanceCalculator.js | 35-38 | decimals = 9 | ⚠️ Diferente precisión |
| useCurrentDividerCalculator.js | 27-30 | decimals = 9 | ⚠️ Diferente precisión |
| useLcResonanceCalculator.js | 27-30 | decimals = 9 | ⚠️ Diferente precisión |
| useFilterCalculator.js | 27-30 | decimals = 9 | ⚠️ Diferente precisión |
| useRcTimeConstantCalculator.js | 17-20 | decimals = 9/12 | ⚠️ Diferente precisión |
| useLedSeriesResistorCalculator.js | 27-30 | decimals = 9 | ⚠️ Diferente precisión |

**Análisis:**
- 6 calculadoras usan `decimals = 6` (resistencias, potencia, ley de Ohm)
- 6 calculadoras usan `decimals = 9` (reactancia, filtros, resonancia)
- 1 calculadora usa `decimals = 12` para constantes de tiempo RC

**Recomendación:** La función en utils/format.js debería aceptar el parámetro decimals, y todas las calculadoras deberían importarla.

---

### 1.2 toOhm - Conversión de unidades de resistencia

**Repeticiones:** 5 veces  
**Líneas duplicadas:** ~15 líneas  
**Ubicación correcta:** `src/utils/units.js` (líneas 13-16)

```javascript
// ORIGINAL EN utils/units.js
export function toOhm(value, unit) {
  const factor = resistanceUnitFactor[unit] || 1
  return Number(value) * factor
}
```

**Archivos que duplican:**

| Archivo | Líneas | Notas |
|---------|--------|-------|
| useVoltageDividerCalculator.js | 13-16 | Ídem |
| useCurrentDividerCalculator.js | 15-18 | Ídem |
| useLedSeriesResistorCalculator.js | 15-18 | Ídem |
| useRcTimeConstantCalculator.js | 23-26 | Ídem |
| useLowHighPassFilterCalculator.js | 29-32 | Ídem |

---

### 1.3 toFarad - Conversión de unidades de capacitancia

**Repeticiones:** 4 veces  
**Líneas duplicadas:** ~12 líneas  
**Ubicación correcta:** `src/utils/units.js` (líneas 33-36)

**Archivos que duplican:**
- useReactanceCalculator.js
- useLcResonanceCalculator.js
- useFilterCalculator.js
- useRcTimeConstantCalculator.js

---

### 1.4 Funciones de normalización de datos

**normalizeRepair** - 5 repeticiones en páginas admin:
- useRepairsAdminPage.js
- useRepairDetailAdminPage.js
- useQuotesAdminPage.js
- useArchivePage.js
- (y posiblemente otros)

**normalizeClient** - 4 repeticiones:
- useClientsPage.js
- useRepairsAdminPage.js
- useQuotesAdminPage.js
- useArchivePage.js

**Análisis:** Estas funciones normalizan respuestas de API a un formato consistente. Son idénticas o muy similares entre archivos.

---

## PARTE 2: CONSTANTES Y ESTRUCTURAS DUPLICADAS

### 2.1 resistanceUnitFactor - 5 REPETICIONES

```javascript
// ESTRUCTURA IDÉNTICA EN 5 ARCHIVOS
const resistanceUnitFactor = {
  ohm: 1,
  kohm: 1000,
  mohm: 1000000,
}
```

**Ubicación correcta:** `src/utils/units.js` (líneas 1-5)  
**Archivos que duplican:**
- useVoltageDividerCalculator.js
- useCurrentDividerCalculator.js
- useLedSeriesResistorCalculator.js
- useRcTimeConstantCalculator.js
- useLowHighPassFilterCalculator.js

### 2.2 capacitanceUnitFactor - 4 REPETICIONES

```javascript
// ESTRUCTURA IDÉNTICA EN 4 ARCHIVOS
const capacitanceUnitFactor = {
  pf: 1e-12,
  nf: 1e-9,
  uf: 1e-6,
  mf: 1e-3,
  f: 1,
}
```

**Ubicación correcta:** `src/utils/units.js` (líneas 19-25)  
**Archivos que duplican:**
- useReactanceCalculator.js
- useFilterCalculator.js
- useRcTimeConstantCalculator.js
- useLowHighPassFilterCalculator.js

### 2.3 frequencyUnitFactor - 2 REPETICIONES

**Ubicación correcta:** `src/utils/units.js` (líneas 39-45)  
**Archivos que duplican:**
- useReactanceCalculator.js
- useFilterCalculator.js

### 2.4 inductanceUnitFactor - 2 REPETICIONES (parcial)

En useReactanceCalculator.js y useLcResonanceCalculator.js - pero utils/units.js tiene una versión más completa con `nh` incluido.

---

## PARTE 3: OPTIONS/ARRAYS DUPLICADOS - "LA PLAGA DE LAS OPCIONES"

### 3.1 Opciones de unidades de resistencia

```javascript
// ESTA ESTRUCTURA APARECE CON DIFERENTES NOMBRES:

// useVoltageDividerCalculator.js
export const resistorUnitOptions = [
  { value: 'ohm', label: 'Ω' },
  { value: 'kohm', label: 'kΩ' },
  { value: 'mohm', label: 'MΩ' },
]

// useCurrentDividerCalculator.js  
export const currentDividerResistanceUnitOptions = [
  { value: 'ohm', label: 'Ω' },
  { value: 'kohm', label: 'kΩ' },
  { value: 'mohm', label: 'MΩ' },
]

// useRcTimeConstantCalculator.js
export const rcResistanceUnitOptions = [
  { value: 'ohm', label: 'Ω' },
  { value: 'kohm', label: 'kΩ' },
  { value: 'mohm', label: 'MΩ' },
]

// useFilterCalculator.js
export const filterResistanceUnitOptions = [
  { value: 'ohm', label: 'Ω' },
  { value: 'kohm', label: 'kΩ' },
  { value: 'mohm', label: 'MΩ' },
]

// useLowHighPassFilterCalculator.js
export const filterResistanceUnitOptions = [
  { value: 'ohm', label: 'Ω' },
  { value: 'kohm', label: 'kΩ' },
  { value: 'mohm', label: 'MΩ' },
]
```

**Análisis:** Son exactamente los mismos datos, solo cambia el nombre de la constante exportada. Esto sugiere que cada calculadora fue desarrollada de forma aislada sin revisar utilidades compartidas.

### 3.2 Opciones de unidades de capacitancia

```javascript
// DIFERENTES NOMBRES, MISMO CONTENIDO:

// reactanceCapacitanceUnitOptions
// rcCapacitanceUnitOptions  
// filterCapacitanceUnitOptions

// TODAS SON:
[
  { value: 'pf', label: 'pF' },
  { value: 'nf', label: 'nF' },
  { value: 'uf', label: 'µF' },
  { value: 'mf', label: 'mF' },
  { value: 'f', label: 'F' },
]
```

### 3.3 Lista completa de options duplicadas

| Nombre | Uso | Duplicado de |
|--------|-----|--------------|
| resistorUnitOptions | VoltageDivider | resistanceUnits (utils) |
| currentDividerResistanceUnitOptions | CurrentDivider | resistanceUnits (utils) |
| rcResistanceUnitOptions | RcTimeConstant | resistanceUnits (utils) |
| filterResistanceUnitOptions | Filter | resistanceUnits (utils) |
| reactanceCapacitanceUnitOptions | Reactance | capacitanceUnits (utils) |
| rcCapacitanceUnitOptions | RcTimeConstant | capacitanceUnits (utils) |
| filterCapacitanceUnitOptions | Filter | capacitanceUnits (utils) |
| reactanceFrequencyUnitOptions | Reactance | frequencyUnits (utils) |
| filterFrequencyUnitOptions | Filter | frequencyUnits (utils) |
| reactanceInductanceUnitOptions | Reactance | inductanceUnits (utils) |
| reactanceModeOptions | Reactance | (específico) |
| filterModeOptions | Filter | (específico) |
| smdResistorTypeOptions | SmdResistor | (específico) |
| smdCapacitorTypeOptions | SmdCapacitor | (específico) |

---

## PARTE 4: COMPONENTES DUPLICADOS

### 4.1 BaseButton DUPLICADO COMPLETO

**Componente A:** `src/components/base/BaseButton.vue` (usado ✅)  
**Componente B:** `src/components/ui/BaseButton.vue` (muerto ❌)  
**Diferencias:** Son implementaciones COMPLETAMENTE DIFERENTES

| Aspecto | base/BaseButton | ui/BaseButton |
|---------|-----------------|---------------|
| Tamaño | 110 líneas | 78 líneas |
| Props | 8 props | 5 props |
| Variantes | 6 variantes | 3 variantes |
| Tamaños | sm/md/lg | (no tiene) |
| Features | loadingText, block, rounded | Básico |
| Estilos | Completo con hover states | Básico |

**Análisis forense:**  
`ui/BaseButton.vue` parece ser una versión anterior/más simple. `base/BaseButton.vue` es la versión evolucionada con más features. Nadie importa `ui/BaseButton.vue`.

**Verificación:**
```bash
grep -r "ui/BaseButton" src/  # Sin resultados
grep -r "base/BaseButton" src/  # Múltiples resultados
```

### 4.2 BaseInput DUPLICADO COMPLETO

**Componente A:** `src/components/base/BaseInput.vue` (usado ✅)  
**Componente B:** `src/components/ui/BaseInput.vue` (muerto ❌)  

Mismo patrón: `ui/` contiene versiones antiguas, `base/` contiene versiones actuales.

---

## PARTE 5: CÓDIGO MUERTO - COMPONENTES HUÉRFANOS

### 5.1 AdminSidebar.vue - EL FANTASMA DEL ADMIN

**Archivo:** `src/components/admin/layout/AdminSidebar.vue`  
**Líneas:** 125  
**Usos encontrados:** 0  
**Estado:** ❌ MUERTO

**Contenido:**
- Menú de navegación completo para admin
- Links a: Dashboard, Reparaciones, Cotizaciones, Clientes, Inventario, Nuevo Ingreso, Citas
- Lógica de active state basada en route
- Estilos CSS completos para sidebar oscuro

**Análisis forense:**
Este componente fue reemplazado por la navegación inline en `AdminShellLayout.vue`. La evidencia:
1. AdminShellLayout.vue tiene su propio sidebar (líneas 10-35)
2. AdminShellLayout.vue tiene los mismos items de menú
3. Nadie importa AdminSidebar.vue

**Por qué quedó:**
Probablemente durante un refactor del layout admin, se movió el sidebar del componente separado al layout directo, y el componente antiguo nunca se eliminó.

### 5.2 AdminTopbar.vue - COMPAÑERO MUERTO

**Archivo:** `src/components/admin/layout/AdminTopbar.vue`  
**Líneas:** 90  
**Usos encontrados:** 0  
**Estado:** ❌ MUERTO

**Contenido:**
- Barra superior con título de página
- Breadcrumbs
- User menu con logout
- Notificaciones

**Análisis:**
Similar al sidebar, fue absorbido por AdminShellLayout.vue o nunca se terminó de integrar.

### 5.3 AdminLayout.vue - WRAPPER VACÍO

**Archivo:** `src/components/admin/layout/AdminLayout.vue`  
**Líneas:** 12  
**Contenido:** Solo `<div class="admin-layout"><slot /></div>`  
**Estado:** ❌ MUERTO

### 5.4 DataTable.vue - COMPONENTE AVANZADO SIN USO

**Archivo:** `src/components/composite/DataTable.vue`  
**Líneas:** 359  
**Usos encontrados:** 0 (en pages/)  
**Usos en componentes:** Solo FormField.vue  
**Estado:** 🟡 SEMI-MUERTO

**Contenido:**
- Tabla con sorting, filtering, pagination
- Slots para personalización
- Integración con BaseCard y BaseTable

**Análisis:**
DataTable es un componente sofisticado que usa BaseTable internamente. Ninguna página lo usa directamente, pero podría ser código preparado para futuro uso o reemplazado por tablas más simples.

### 5.5 StatusBadge.vue - COMPONENTE HUÉRFANO

**Archivo:** `src/components/composite/StatusBadge.vue`  
**Líneas:** 221  
**Usos encontrados:** 0  
**Estado:** ❌ MUERTO

**Contenido:**
- Badge de estado con múltiples variantes (success, warning, danger, info)
- Iconos integrados
- Animaciones

### 5.6 Business Components - WRAPPERS VACÍOS

| Componente | Líneas | Contenido | Estado |
|------------|--------|-----------|--------|
| ClientList.vue | 15 | Solo renderiza slot | ❌ Wrapper innecesario |
| InventoryTable.vue | 27 | Tabla básica, no usada | ❌ Sin uso |
| RepairCard.vue | 14 | Solo envuelve BaseCard | ❌ Wrapper innecesario |

### 5.7 StatsCards.vue - COMPONENTE SIN USO

**Archivo:** `src/components/admin/StatsCards.vue`  
**Líneas:** ~100 (estimado)  
**Usos:** 0  
**Estado:** ❌ MUERTO

---

## PARTE 6: LAYOUTS VACÍOS / INNECESARIOS

### 6.1 AdminLayout.vue (en layouts/, no en components/admin/layout)

**Archivo:** `src/layouts/AdminLayout.vue`  
**Líneas:** 12  
**Contenido:**
```vue
<template>
  <main class="admin-layout">
    <slot />
  </main>
</template>
```

**Estado:** ❌ MUERTO (reemplazado por AdminShellLayout.vue)

### 6.2 AuthLayout.vue

**Archivo:** `src/layouts/AuthLayout.vue`  
**Líneas:** 11  
**Contenido:** Similar a AdminLayout.vue, solo un `<main>` con slot  
**Estado:** ❌ MUERTO

**Análisis:**
Los layouts vacíos no aportan valor. Podrían eliminarse y usar el layout por defecto de Vue Router.

---

## PARTE 7: COMPOSABLES - PATRONES REPETIDOS

### 7.1 Patrón "CRUD Page" Duplicado

Todos los composables de páginas admin siguen este patrón:

```javascript
export function use[Nombre]Page() {
  // 1. State
  const items = ref([])
  const loading = ref(false)
  const error = ref(null)
  
  // 2. Formularios
  const createForm = reactive({ ... })
  const editForm = reactive({ ... })
  
  // 3. Fetch
  const fetchItems = async () => { ... }
  
  // 4. CRUD
  const createItem = async () => { ... }
  const updateItem = async () => { ... }
  const deleteItem = async () => { ... }
  
  // 5. Normalización (DUPLICADA)
  const normalizeItem = (entry) => { ... }
  
  return { items, loading, error, fetchItems, createItem, ... }
}
```

**Composables con este patrón:**
- useAppointmentsPage.js
- useArchivePage.js
- useCategoriesPage.js
- useClientsPage.js
- useContactMessagesPage.js
- useManualsPage.js
- useNewsletterSubscriptionsPage.js
- usePurchaseRequestsPage.js
- useQuotesAdminPage.js
- useRepairsAdminPage.js
- useRepairDetailAdminPage.js
- useTicketsPage.js

**Líneas de código similares:** ~60-80 líneas por archivo × 12 archivos = ~840 líneas de patrón repetido

### 7.2 Patrón "Calculator" Duplicado

Ya documentado en VUE_APLICADO.md:
- reactive(form)
- computed(canCalculate)
- computed(result)
- reset()
- normalizeDecimal() duplicada

**17 calculadoras con este patrón**

---

## PARTE 8: ANÁLISIS DE IMPORTS NO USADOS

### 8.1 Verificación de imports en composables

Busqué imports que se declaran pero no se usan:

```bash
grep -r "import.*from" src/composables/*.js | wc -l
# Resultado: ~120 imports

# Verificación visual de los principales:
```

**Hallazgo:** No encontré imports obviamente no usados en composables (requeriría análisis más profundo con herramientas como ESLint).

---

## PARTE 9: HISTORIA FORENSE - ¿POR QUÉ EXISTE ESTE CÓDIGO?

### Hipótesis 1: Evolución del Layout Admin

**Secuencia probable:**
1. Se creó `AdminSidebar.vue` y `AdminTopbar.vue` como componentes separados
2. Se intentó usar `AdminLayout.vue` (wrapper vacío) como layout base
3. Se decidió crear un layout más completo: `AdminShellLayout.vue`
4. El sidebar/topbar se integraron directamente en `AdminShellLayout.vue`
5. Los componentes originales quedaron huérfanos

**Evidencia:**
- `AdminShellLayout.vue` tiene su propia navegación (líneas 14-35)
- Los items de menú son casi idénticos a los de `AdminSidebar.vue`

### Hipótesis 2: Migración de UI a Base

**Secuencia probable:**
1. Se crearon componentes en `ui/` como versión inicial
2. Se decidió crear una versión más completa en `base/`
3. Los componentes `ui/` quedaron obsoletos pero nunca eliminados

**Evidencia:**
- `ui/BaseButton.vue` es más simple que `base/BaseButton.vue`
- `ui/BaseInput.vue` tiene menos features que `base/BaseInput.vue`
- Ningún archivo importa desde `ui/`

### Hipótesis 3: Desarrollo Aislado de Calculadoras

**Secuencia probable:**
1. Se creó `utils/units.js` y `utils/format.js` como utilidades centrales
2. Los desarrolladores de calculadoras no conocían/no usaban estas utilidades
3. Cada calculadora definió sus propias funciones de forma independiente
4. Resultado: 13 versiones de `normalizeDecimal`

**Evidencia:**
- Las funciones duplicadas son idénticas a las de utils/
- Los archivos utils/ tienen comentarios "ADITIVO: Extraído de los composables"
- Esto sugiere que utils/ se creó DESPUÉS de las calculadoras, pero nadie hizo el refactor

---

## PARTE 10: IMPACTO Y RECOMENDACIONES

### 10.1 Impacto del código duplicado

| Métrica | Valor |
|---------|-------|
| Líneas duplicadas (funciones) | ~400 |
| Líneas duplicadas (constantes) | ~150 |
| Líneas duplicadas (options) | ~270 |
| Líneas de código muerto | ~1,083 |
| Líneas de wrappers vacíos | ~50 |
| **Total** | **~1,953 líneas** |

### 10.2 Riesgos de mantener código muerto

1. **Confusión para nuevos desarrolladores:** No saben qué versión usar
2. **Doble mantenimiento:** Si se encuentra un bug, ¿en qué versión se arregla?
3. **Tamaño de bundle:** Aunque tree-shaking elimine código no importado, el código sigue ahí
4. **Tiempo de build:** Más archivos = más tiempo de compilación

### 10.3 Recomendaciones por prioridad

#### 🔴 CRÍTICO - Fase 0: Unificar utils (1-2 horas)
- Reemplazar todas las `normalizeDecimal` locales con import de utils/format.js
- Reemplazar todas las constantes de unidades con imports de utils/units.js
- Impacto: ~550 líneas eliminadas, consistencia garantizada

#### 🟠 ALTO - Fase 1: Eliminar componentes muertos (30 min)
- Eliminar `AdminSidebar.vue`
- Eliminar `AdminTopbar.vue`
- Eliminar `AdminLayout.vue` (layout vacío)
- Eliminar `AuthLayout.vue` (layout vacío)
- Eliminar `ui/BaseButton.vue`
- Eliminar `ui/BaseInput.vue`
- Impacto: ~632 líneas eliminadas

#### 🟡 MEDIO - Fase 2: Evaluar composite/ (1 hora)
- Evaluar si `DataTable.vue` se usará en el futuro
- Evaluar si `StatusBadge.vue` se usará
- Decidir: eliminar o integrar
- Impacto potencial: ~580 líneas

#### 🟢 BAJO - Fase 3: Wrappers innecesarios (30 min)
- Evaluar si `ClientList.vue`, `RepairCard.vue` aportan valor
- Si son solo wrappers, eliminar y usar el componente base directamente
- Impacto: ~29 líneas

---

## APÉNDICE A: MAPA COMPLETO DE DUPLICACIONES

### A.1 Funciones duplicadas

```
normalizeDecimal (13):
  ├── useOhmsLawCalculator.js
  ├── usePowerCalculator.js
  ├── useVoltageDividerCalculator.js
  ├── useAwgCalculator.js
  ├── useSmdResistorCalculator.js
  ├── useOpAmpCalculator.js
  ├── useResistorColorCalculator.js (inline)
  ├── useReactanceCalculator.js (decimals=9)
  ├── useCurrentDividerCalculator.js (decimals=9)
  ├── useLcResonanceCalculator.js (decimals=9)
  ├── useFilterCalculator.js (decimals=9)
  ├── useRcTimeConstantCalculator.js (decimals=9/12)
  └── useLedSeriesResistorCalculator.js (decimals=9)
  
  ORIGEN: utils/format.js ✅

toOhm (5):
  ├── useVoltageDividerCalculator.js
  ├── useCurrentDividerCalculator.js
  ├── useLedSeriesResistorCalculator.js
  ├── useRcTimeConstantCalculator.js
  └── useLowHighPassFilterCalculator.js
  
  ORIGEN: utils/units.js ✅

toFarad (4):
  ├── useReactanceCalculator.js
  ├── useLcResonanceCalculator.js
  ├── useFilterCalculator.js
  └── useRcTimeConstantCalculator.js
  
  ORIGEN: utils/units.js ✅

normalizeRepair (5):
  ├── useRepairsAdminPage.js
  ├── useRepairDetailAdminPage.js
  ├── useQuotesAdminPage.js
  ├── useArchivePage.js
  └── useTicketsPage.js (probable)
  
  ORIGEN: ??? (crear utils/normalization.js)

normalizeClient (4):
  ├── useClientsPage.js
  ├── useRepairsAdminPage.js
  ├── useQuotesAdminPage.js
  └── useArchivePage.js
  
  ORIGEN: ??? (crear utils/normalization.js)
```

### A.2 Constantes duplicadas

```
resistanceUnitFactor (5):
  ├── useVoltageDividerCalculator.js
  ├── useCurrentDividerCalculator.js
  ├── useLedSeriesResistorCalculator.js
  ├── useRcTimeConstantCalculator.js
  └── useLowHighPassFilterCalculator.js
  
  ORIGEN: utils/units.js ✅

capacitanceUnitFactor (4):
  ├── useReactanceCalculator.js
  ├── useFilterCalculator.js
  ├── useRcTimeConstantCalculator.js
  └── useLowHighPassFilterCalculator.js
  
  ORIGEN: utils/units.js ✅
```

---

## CONCLUSIÓN

El análisis forense revela **~2,000 líneas de código duplicado o muerto** en un proyecto de ~15,000 líneas (estimado). Esto representa un **13% de código innecesario**.

### Hallazgos más críticos:

1. **normalizeDecimal en 13 archivos** - El caso más grave de duplicación
2. **Componentes ui/ vs base/** - Dos versiones de los mismos componentes
3. **AdminSidebar/Topbar muertos** - Código funcional pero huérfano
4. **utils/ existe pero no se usa** - Las calculadoras ignoran las utilidades centralizadas

### Próximos pasos recomendados:

1. Inmediato: Eliminar componentes muertos (bajo riesgo)
2. Corto plazo: Unificar imports de utils (bajo riesgo, alto impacto)
3. Mediano plazo: Crear factory para composables CRUD (refactor mayor)

---

*Documento generado para auditoría técnica. No se modificó ningún archivo.*
