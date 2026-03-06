# AUDITORÍA DE PROBLEMAS - MIGRACIÓN SASS → VUE

## 1. VERDES PROHIBIDOS (URGENTE)

**REGLA:** El ÚNICO verde permitido es el botón de WhatsApp (#25d366).
**PROBLEMA:** Verde y naranja hacen café, se ve horrible (colores antagonistas).

### Ubicaciones detectadas:

#### pages/_admin.scss
- `background: rgba($color-success, 0.15)` → CAMBIAR A rgba($color-primary, 0.15)
- `color: darken($color-success, 10%)` → CAMBIAR A darken($color-primary, 10%)
- `border-left-color: $color-green-700-legacy` → CAMBIAR A $color-primary

#### components/_app.scss (múltiples ocurrencias)
- `background: $color-green-100-legacy` → CAMBIAR A $color-orange-100-legacy
- `color: $color-green-800-legacy` → CAMBIAR A $color-orange-800-legacy
- `color: $color-success` → CAMBIAR A $color-primary
- `border-color: $color-green-primary-legacy` → CAMBIAR A $color-primary
- `box-shadow: 0 0 0 3px rgba($color-green-primary-legacy, 0.1)` → rgba($color-primary, 0.1)
- `background: $color-green-light-bg-legacy` → CAMBIAR A $color-orange-50-legacy
- `color: $color-green-primary-legacy` → CAMBIAR A $color-primary
- `border: 2px solid $color-green-border-legacy` → $color-primary
- `color: $color-green-text-legacy` → CAMBIAR A $color-primary

**ACCIÓN:** Reemplazar TODOS los verdes por naranja/primary.

---

## 2. TIPOGRAFÍA PEQUEÑA Y FLAQUITA (URGENTE)

**PROBLEMA:** Texto muy chico, cuesta leerlo. Especialmente en:
- Formularios (inputs, textareas)
- Casillas de texto
- Menús desplegables (selects)
- Filtros de tienda (marcas, categorías)
- Fuente muy flaquita (font-weight bajo)

### Ocurrencias por archivo:
- _public.scss: 38 ocurrencias de font-size pequeños
- components/_app.scss: 26 ocurrencias
- _admin.scss: 24 ocurrencias
- pages/_admin.scss: 20 ocurrencias
- _typography.scss: 5 ocurrencias
- _email.scss: 3 ocurrencias
- _layout.scss: 2 ocurrencias
- base/_typography.scss: 2 ocurrencias

**TOTAL: 122 ocurrencias**

### Font-sizes problemáticos detectados:
- 0.6rem, 0.7rem, 0.75rem, 0.8rem, 0.85rem, 0.9rem
- 12px, 13px, 14px

### Font-weights problemáticos:
- 300 (light) → CAMBIAR A 400 (regular) o 500 (medium)
- 400 en textos importantes → CAMBIAR A 500 o 600

**ACCIÓN:**
1. Aumentar todos los font-size a mínimo 1rem (16px) o 0.95rem (15px)
2. Aumentar font-weight a mínimo 400 (regular), preferir 500 (medium) para mejor legibilidad
3. Prioridad: inputs, selects, formularios, filtros

---

## 3. CONTRASTES MALOS

**PROBLEMA:** Combinaciones de colores con bajo contraste dificultan la lectura.

### Combinaciones problemáticas a buscar:
- Gris claro sobre blanco
- Gris oscuro sobre negro
- Texto claro sobre fondo claro
- Cualquier contraste < 4.5:1 (WCAG AA)

**VARIABLES SOSPECHOSAS:**
- $light-5, $light-6 (grises claros sobre fondos claros)
- $color-gray-* sobre fondos blancos
- Texto muted/secondary sobre fondos claros

**ACCIÓN:** Auditar todos los usos de colores grises y verificar contraste.

---

## 4. WIDGETS RESTANTES POR MIGRAR

### FilterTabs
- Filtros de tienda (marcas, categorías)
- **CRÍTICO:** Texto muy pequeño aquí

### FloatingQuoteButton
- Botón flotante para cotizaciones

### InlineLinkList
- Listas de links inline (footer, etc.)

### StoreCartWidget
- Widget de carrito flotante

### TurnstileWidget
- Widget de Cloudflare Turnstile

---

## PRIORIDAD DE EJECUCIÓN

1. **URGENTE:** Eliminar todos los verdes prohibidos
2. **URGENTE:** Aumentar tipografía en formularios/inputs/selects/filtros
3. **ALTA:** Mejorar contrastes grises
4. **MEDIA:** Completar migración de 5 widgets restantes
5. **BAJA:** Migrar componentes de articles (foxy heredado)

---

## PALETA DE COLORES APROBADA

### Colores Principales
- **Primary (Naranja):** #ec6b00 (PANTONE 7577 C)
- **Dark (Vintage Black):** #3e3c38 (PANTONE Black 7 C)
- **Light (Vintage Beige):** #d3d0c3 (PANTONE 7527 C)
- **White:** #ffffff

### Colores Secundarios
- **Warm Brown:** #ac612a
- **Accent:** #c7814e
- **Neutral Gray:** #8f9799

### El ÚNICO Verde Permitido
- **WhatsApp:** #25d366 (SOLO para botón de WhatsApp)

### Colores PROHIBIDOS
- ❌ Todo verde que NO sea WhatsApp button
- ❌ $color-success (verde #038600)
- ❌ $color-green-*-legacy (todos)
