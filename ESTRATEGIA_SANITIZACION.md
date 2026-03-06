# ESTRATEGIA DE SANITIZACIÓN MASIVA
## Cirujano de Sintetizadores - Migración SCSS → Vue + Design System

**Basado en:** Manual de Identidad (MANUAL_CIRUJANO.pdf)
**Filosofía:** DECONSTRUCTIVO - desarmar para armar algo nuevo
**Principio:** Aditivo, no destructivo. Usar lo que existe, no inventar.

---

## 🎯 PROBLEMA IDENTIFICADO

El código está **FRAGMENTADO EN CASCADA**:
- Mismos colores repetidos 100+ veces: `#ec6b00`, `#3e3c38`, `#6b7280`
- Mismos font-sizes repetidos: `1rem` (65 veces), `0.875rem` (21 veces)
- Mismos border-radius repetidos: `12px` (16 veces), `8px` (7 veces)
- 150+ colores "-legacy" redundantes en variables SCSS
- 24 componentes Vue con colores HARDCODEADOS

**Resultado:**
- `components/_app.scss` tiene 4,724 líneas con TONELADAS de duplicación
- Imposible mantener consistencia con el Manual de Identidad
- Verde y naranja se mezclan (antagonistas → café/caca)

---

## ✅ SOLUCIÓN: PLANILLA MAESTRA + REEMPLAZO EN CASCADA

### 1. **Design System Central**
✅ CREADO: `src/scss/_design-system.scss`
- CSS Custom Properties (`:root`) basadas 100% en Manual de Identidad
- Variables accesibles desde Vue components vía `var(--color-primary)`
- Sistema consolidado: colores, tipografía, espaciado, radios, sombras

### 2. **Patrón de Reemplazo Masivo**

#### ANTES (hardcoded - MAL):
```vue
<style scoped>
.card {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 1rem;
  color: #374151;
}
</style>
```

#### DESPUÉS (design system - BIEN):
```vue
<style scoped>
.card {
  background: var(--color-white);
  border: 1px solid var(--gray-200);
  border-radius: var(--radius-md);
  padding: var(--spacer-md);
  color: var(--gray-700);
}
</style>
```

---

## 📊 MAPEO DE COLORES (Manual página 13)

### Colores Principales
| Hardcoded | Variable CSS | Uso |
|-----------|--------------|-----|
| `#ec6b00` | `var(--color-primary)` | Naranja principal (HEGEMONÍA) |
| `#3e3c38` | `var(--color-dark)` | Vintage Black |
| `#d3d0c3` | `var(--color-light)` | Vintage Beige |
| `#ffffff` | `var(--color-white)` | Blanco |
| `#000000` | `var(--color-black)` | Negro |

### Grises (consolidados de 50+ legacy)
| Hardcoded | Variable CSS |
|-----------|--------------|
| `#fafafa` | `var(--gray-50)` |
| `#f3f4f6` | `var(--gray-100)` |
| `#e5e7eb` | `var(--gray-200)` |
| `#d1d5db` | `var(--gray-300)` |
| `#9ca3af` | `var(--gray-400)` |
| `#6b7280` | `var(--gray-500)` |
| `#4b5563` | `var(--gray-600)` |
| `#374151` | `var(--gray-700)` |
| `#1f2937` | `var(--gray-800)` |
| `#111827` | `var(--gray-900)` |

### ⚠️ VERDE ELIMINADO
**TODO verde → naranja** (excepto WhatsApp `#25d366`)
- `#28a745` → `var(--color-primary)`
- `#22c55e` → `var(--color-primary)`
- `#10b981` → `var(--color-primary)`

**Razón:** Verde + Naranja = Café (antagonistas)

---

## 🔤 TIPOGRAFÍA (Manual página 15)

### Font Sizes (AUMENTADOS para legibilidad)
| Antes | Después | Variable |
|-------|---------|----------|
| `0.6rem` | `1rem` | `var(--text-base)` |
| `0.75rem` | `0.75rem` | `var(--text-2xs)` ← mínimo absoluto |
| `0.8rem` | `1rem` | `var(--text-base)` |
| `0.875rem` | `0.875rem` | `var(--text-sm)` |
| `0.9rem` | `1rem` | `var(--text-base)` |
| `1rem` | `1rem` | `var(--text-base)` |

### Font Weights
- Normal: `var(--fw-normal)` = 400
- Medium: `var(--fw-medium)` = 500
- Semibold: `var(--fw-semibold)` = 600
- Bold: `var(--fw-bold)` = 700

---

## 📐 ESPACIADO Y GEOMETRÍA

### Spacers (sistema 4px)
```css
--spacer-xs: 0.25rem   /* 4px */
--spacer-sm: 0.5rem    /* 8px */
--spacer-md: 1rem      /* 16px */
--spacer-lg: 1.5rem    /* 24px */
--spacer-xl: 2rem      /* 32px */
```

### Border Radius
```css
--radius-sm: 8px
--radius-md: 12px
--radius-lg: 16px
--radius-pill: 999px
--radius-circle: 50%
```

---

## 🚀 PLAN DE EJECUCIÓN EN CASCADA

### Fase 1: Reemplazo Automático (buscar/reemplazar)

**Colores:**
```bash
# En TODOS los archivos .vue en src/vue/components/
color: #ec6b00     → color: var(--color-primary)
background: #ec6b00 → background: var(--color-primary)

color: #3e3c38     → color: var(--color-dark)
color: #6b7280     → color: var(--gray-500)
color: #e5e7eb     → color: var(--gray-200)
# ... etc para todos los grises
```

**Tipografía:**
```bash
font-size: 0.875rem → font-size: var(--text-sm)
font-size: 1rem     → font-size: var(--text-base)
font-size: 1.25rem  → font-size: var(--text-lg)
font-weight: 600    → font-weight: var(--fw-semibold)
```

**Geometría:**
```bash
border-radius: 12px → border-radius: var(--radius-md)
border-radius: 8px  → border-radius: var(--radius-sm)
border-radius: 999px → border-radius: var(--radius-pill)
padding: 1rem       → padding: var(--spacer-md)
gap: 0.75rem        → gap: var(--spacer-md)
```

### Fase 2: Consolidación SCSS
- Eliminar colores "-legacy" redundantes de `_variables.scss`
- Reemplazar en `components/_app.scss` todas las referencias legacy
- Reducir archivo de 4,724 → ~2,500 líneas

### Fase 3: Migración Vue Restante
- 24 componentes Vue con hardcoded values
- Aplicar patrón de reemplazo a cada uno
- Verificar que usen design system

---

## 📈 MÉTRICAS OBJETIVO

| Métrica | Antes | Objetivo |
|---------|-------|----------|
| Líneas `_app.scss` | 4,724 | 2,500 |
| Colores únicos hardcoded | ~150 | 10 |
| Font-sizes únicos | ~25 | 9 |
| Border-radius únicos | ~12 | 5 |
| Componentes con hardcode | 24 | 0 |
| Colores verdes (no-WhatsApp) | 59 | 0 |

---

## ✋ REGLAS DE ORO

1. **NO INVENTAR** - usar solo lo que existe en Manual + `_variables.scss`
2. **HEGEMONÍA NARANJA** - verde solo en WhatsApp (#25d366)
3. **MÍNIMO LEGIBILIDAD** - nada menor a 0.75rem (12px)
4. **CONTRASTE WCAG** - verificar grises sobre blancos
5. **DECONSTRUCTIVO** - desarmar para entender, armar algo nuevo
6. **ADITIVO** - no destruir, agregar capas de mejora

---

## 🎨 PALETA CROMÁTICA FINAL

```
PRIMARIO: #ec6b00 (Orange - PANTONE 7577 C)
DARK:     #3e3c38 (Vintage Black - PANTONE Black 7 C)
LIGHT:    #d3d0c3 (Vintage Beige - PANTONE 7527 C)
WHITE:    #ffffff
BLACK:    #000000

GRISES:   50, 100, 200, 300, 400, 500, 600, 700, 800, 900
ESTADOS:  success→primary, danger→red, warning→amber, info→blue
```

---

**Próximo paso:** Ejecutar reemplazos en cascada usando el mapeo de arriba.
