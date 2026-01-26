# INVENTARIO DE TIPOGRAFÍA - Cirujano de Sintetizadores

**Fecha:** 26/01/2026
**Propósito:** Identificar todas las variantes de tamaño para unificar

---

## 1. FONT-SIZE (Tamaños de Texto)

### Valores Fijos (de menor a mayor)

| Valor | Usos | Equivalente px (base 16) | Categoría Propuesta |
|-------|------|--------------------------|---------------------|
| `0.5rem` | 1 | 8px | ❌ Muy pequeño |
| `0.65rem` | 1 | 10.4px | ❌ Muy pequeño |
| `0.7rem` | 3 | 11.2px | ❌ Muy pequeño |
| `0.72rem` | 1 | 11.5px | ❌ Muy pequeño |
| `0.75rem` | 11 | 12px | `$text-xs` |
| `0.8rem` | 12 | 12.8px | `$text-xs` |
| `0.85rem` | **47** | 13.6px | `$text-sm` |
| `0.875rem` | 1 | 14px | `$text-sm` |
| `0.9rem` | **35** | 14.4px | `$text-sm` |
| `0.95rem` | **33** | 15.2px | `$text-base` |
| `0.98rem` | 3 | 15.7px | `$text-base` |
| `1rem` | **48** | 16px | `$text-base` |
| `1.05rem` | 12 | 16.8px | `$text-base` |
| `1.1rem` | **22** | 17.6px | `$text-md` |
| `1.2rem` | 12 | 19.2px | `$text-md` |
| `1.25rem` | 11 | 20px | `$text-lg` |
| `1.3rem` | 9 | 20.8px | `$text-lg` |
| `1.35rem` | 1 | 21.6px | `$text-lg` |
| `1.4rem` | 6 | 22.4px | `$text-xl` |
| `1.45rem` | 1 | 23.2px | `$text-xl` |
| `1.5rem` | 11 | 24px | `$text-xl` / `$h4` |
| `1.6rem` | 2 | 25.6px | `$h4` |
| `1.7rem` | 1 | 27.2px | `$h4` |
| `1.75rem` | 2 | 28px | `$h4` |
| `1.8rem` | 6 | 28.8px | `$h3` |
| `2rem` | 10 | 32px | `$h3` |
| `2.05rem` | 1 | 32.8px | `$h3` |
| `2.1rem` | 1 | 33.6px | `$h3` |
| `2.25rem` | 1 | 36px | `$h2` |
| `2.3rem` | 1 | 36.8px | `$h2` |
| `2.5rem` | 3 | 40px | `$h2` |
| `3rem` | 5 | 48px | `$h1` |

### Valores con clamp() (Responsivos)

| Valor | Usos | Rango | Categoría |
|-------|------|-------|-----------|
| `clamp(16px, 0.8vw + 14px, 20px)` | 1 | 16-20px | Root HTML |
| `clamp(1rem, 1.2vw, 1.4rem)` | 1 | 16-22px | Subtítulo |
| `clamp(1rem, 1.6vw, 1.2rem)` | 2 | 16-19px | Subtítulo |
| `clamp(1.05rem, 0.6vw + 0.9rem, 1.25rem)` | 1 | 17-20px | **Párrafo** |
| `clamp(1.05rem, 0.9vw + 0.9rem, 1.35rem)` | 2 | 17-22px | Párrafo |
| `clamp(1.05rem, 1.1vw, 1.35rem)` | 1 | 17-22px | Párrafo |
| `clamp(1.6rem, 2.1vw + 0.3rem, 2.2rem)` | 1 | 26-35px | **H3** |
| `clamp(1.6rem, 2.4vw, 2.2rem)` | 2 | 26-35px | H3 |
| `clamp(2rem, 2.8vw + 0.5rem, 2.8rem)` | 1 | 32-45px | **H2** |
| `clamp(2rem, 4vw, 3.2rem)` | 2 | 32-51px | H2/Section |
| `clamp(2rem, 4.5vw, 3.5rem)` | 1 | 32-56px | H1/Hero |
| `clamp(2.4rem, 3.6vw + 0.6rem, 3.4rem)` | 1 | 38-54px | **H1** |
| `clamp(2.4rem, 5.2vw, 4.4rem)` | 1 | 38-70px | Hero |

---

## 2. RESUMEN DE DISPERSIÓN

### Font-size: **67 valores diferentes**

| Rango | Cantidad de variantes | Problema |
|-------|----------------------|----------|
| 0.5-0.75rem (8-12px) | 6 valores | Demasiado pequeño |
| 0.8-0.9rem (13-14px) | 4 valores | Redundantes |
| 0.95-1.05rem (15-17px) | 4 valores | Redundantes |
| 1.1-1.4rem (18-22px) | 6 valores | Redundantes |
| 1.5-1.8rem (24-29px) | 5 valores | Redundantes |
| 2-2.5rem (32-40px) | 5 valores | Redundantes |
| 3rem+ (48px+) | 1 valor | OK |
| clamp() | ~13 valores | Muchos similares |

---

## 3. LINE-HEIGHT

| Valor | Usos | Propuesta |
|-------|------|-----------|
| `1` | 3 | `$lh-none` |
| `1.1` | 5 | `$lh-tight` |
| `1.2` | 1 | `$lh-tight` |
| `1.4` | 1 | `$lh-snug` |
| `1.45` | 1 | `$lh-snug` |
| `1.5` | 6 | `$lh-normal` |
| `1.55` | 1 | `$lh-normal` |
| `1.6` | **17** | `$lh-normal` ← MÁS USADO |
| `1.65` | 1 | `$lh-relaxed` |
| `1.7` | 5 | `$lh-relaxed` |

**Total: 10 valores diferentes** → Reducir a 5

---

## 4. LETTER-SPACING

| Valor | Usos | Propuesta |
|-------|------|-----------|
| `0.01em` | 2 | `$ls-tight` |
| `0.02em` | 5 | `$ls-tight` |
| `0.03em` | 10 | `$ls-normal` |
| `0.04em` | 11 | `$ls-normal` |
| `0.05em` | **15** | `$ls-wide` ← MÁS USADO |
| `0.06em` | 4 | `$ls-wide` |
| `0.08em` | 7 | `$ls-wider` |
| `0.1em` | 1 | `$ls-widest` |
| `0.3px` | 2 | Convertir a em |
| `0.5px` | 2 | Convertir a em |

**Total: 10 valores diferentes** → Reducir a 5

---

## 5. FONT-WEIGHT

| Valor | Usos | Propuesta |
|-------|------|-----------|
| `100` | 2 | `$fw-thin` |
| `200` | 1 | `$fw-extralight` |
| `300` | 1 | `$fw-light` |
| `400` | 8 | `$fw-normal` |
| `500` | 22 | `$fw-medium` |
| `600` | **105** | `$fw-semibold` ← MÁS USADO |
| `700` | 47 | `$fw-bold` |
| `800` | 19 | `$fw-extrabold` |
| `900` | 2 | `$fw-black` |

**Total: 9 valores** → OK, pero estandarizar nombres

---

## 6. PROPUESTA DE ESCALA UNIFICADA

### Font Sizes (Solo 9 valores)

```scss
// Escala de texto - USAR SOLO ESTOS
$text-2xs: 0.75rem;    // 12px - Etiquetas mínimas
$text-xs:  0.8125rem;  // 13px - Texto muy pequeño
$text-sm:  0.875rem;   // 14px - Texto pequeño
$text-base: 1rem;      // 16px - Texto normal
$text-md:  1.125rem;   // 18px - Texto medio
$text-lg:  1.25rem;    // 20px - Texto grande
$text-xl:  1.5rem;     // 24px - Texto extra grande

// Headings
$h6-size: 1.125rem;    // 18px
$h5-size: 1.25rem;     // 20px
$h4-size: 1.5rem;      // 24px
$h3-size: clamp(1.75rem, 2vw + 1rem, 2.25rem);   // 28-36px
$h2-size: clamp(2rem, 2.5vw + 1rem, 2.75rem);    // 32-44px
$h1-size: clamp(2.5rem, 3vw + 1rem, 3.5rem);     // 40-56px
```

### Line Heights (Solo 5 valores)

```scss
$lh-none:    1;
$lh-tight:   1.2;
$lh-normal:  1.5;
$lh-relaxed: 1.6;   // Default para texto corrido
$lh-loose:   1.8;
```

### Letter Spacing (Solo 5 valores)

```scss
$ls-tighter: -0.02em;
$ls-tight:   -0.01em;
$ls-normal:  0;
$ls-wide:    0.02em;
$ls-wider:   0.05em;
$ls-widest:  0.1em;
```

### Font Weights (Estandarizado)

```scss
$fw-light:     300;
$fw-normal:    400;
$fw-medium:    500;
$fw-semibold:  600;  // Default para UI
$fw-bold:      700;
$fw-extrabold: 800;
```

---

## 7. ARCHIVOS CON MÁS VALORES HARDCODEADOS

Para priorizar la limpieza, estos archivos tienen más valores inline:

```
47 usos de 0.85rem → Revisar estos archivos
35 usos de 0.9rem  → Muchos componentes Vue
33 usos de 0.95rem → Dispersión alta
48 usos de 1rem    → OK (es el base)
```

---

## 8. ACCIONES RECOMENDADAS

1. **Actualizar `abstracts/_variables.scss`** con la escala unificada
2. **Crear mixins de texto** que usen la escala
3. **Gradualmente** reemplazar valores hardcodeados en componentes Vue
4. **Eliminar** tamaños menores a 0.75rem (muy pequeños para accesibilidad)

---

*Inventario generado automáticamente - 26/01/2026*
