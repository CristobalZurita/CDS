# AUDITORÍA DE PROBLEMAS - MIGRACIÓN SASS → VUE

## 1. VERDES PROHIBIDOS ✅ COMPLETADO

**REGLA:** El ÚNICO verde permitido es el botón de WhatsApp (#25d366).
**PROBLEMA:** Verde y naranja hacen café, se ve horrible (colores antagonistas).

### ✅ STATUS: 100% ELIMINADOS

**Total eliminados: 59 instancias de verde prohibido**

#### ✅ pages/_admin.scss (2 eliminados)
- Badge success variant → rgba($color-primary, 0.15)
- Status confirmado border → $color-primary

#### ✅ components/_app.scss (43 eliminados)
- Status badges (completed, archivado, noventena)
- Success content icons
- Search input focus states
- Brand card & instrument card active states
- Instrument values
- Confirmation sections
- Summary rows borders
- Proceed buttons with gradients
- Progress tracker completed steps
- Photos count boxes
- Success icons & gradients
- Min price boxes
- Fault prices
- Disclaimer boxes
- Budget details
- Toast success notifications
- Spinner border colors
- Turnstile bypass widget

#### ✅ _public.scss (12 eliminados)
- Stat icon completed
- Repair status (entregado, noventena, archivado, completed, delivered)
- Notification card success
- Status colors
- Success step gradients

#### ✅ _admin.scss (2 eliminados)
- Status changer CSS variables (--status-color-4, --status-color-7)

**ACCIÓN:** ✅ COMPLETADA - Todos los verdes reemplazados por naranja/primary.
**HEGEMONÍA NARANJA MANTENIDA:** Solo #25d366 (WhatsApp) permitido en todo el sitio.

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

## 4. WIDGETS ✅ COMPLETADO (14/14)

### ✅ TODOS MIGRADOS A VUE
Migración 100% completada de 14 widgets:

1. ✅ **Divider** - Línea divisoria negra
2. ✅ **XLButton** - Botón extra-large con 3 variantes (orange, pastel, outline)
3. ✅ **CircleIcon** - Ícono circular responsive
4. ✅ **Spinner** - Indicador de carga
5. ✅ **FloatingWhatsAppButton** - Único verde permitido (#25d366)
6. ✅ **Breadcrumbs** - Migas de pan con separador ›
7. ✅ **QuotedText** - Texto sin wrap
8. ✅ **ProgressBar** - Barra de progreso con cálculo dinámico
9. ✅ **SocialLinks** - Links sociales con sizing responsive complejo
10. ✅ **TurnstileWidget** - Cloudflare Turnstile (VERDE ELIMINADO)
11. ✅ **FilterTabs** - Filtros de tienda (TIPOGRAFÍA AUMENTADA: 1rem, fw:500-600)
12. ✅ **FloatingQuoteButton** - Botón scroll-to-top
13. ✅ **InlineLinkList** - Links inline con separador ·
14. ✅ **StoreCartWidget** - Carrito flotante (TIPOGRAFÍA AUMENTADA: 1rem+)

---

## PRIORIDAD DE EJECUCIÓN

1. ✅ **URGENTE:** ~~Eliminar todos los verdes prohibidos~~ **COMPLETADO** (59 verdes eliminados)
2. 🔄 **URGENTE:** Aumentar tipografía en formularios/inputs/selects/filtros (122 ocurrencias pendientes)
3. ⏳ **ALTA:** Mejorar contrastes grises (pendiente auditoría detallada)
4. ✅ **MEDIA:** ~~Completar migración de widgets~~ **COMPLETADO** (14/14 widgets migrados)
5. ⏳ **BAJA:** Migrar componentes de articles (foxy heredado)

### PRÓXIMOS PASOS

**Inmediato:** Abordar las 122 instancias de tipografía pequeña (0.6rem-0.9rem) en:
- _public.scss (38 ocurrencias) - PRIORIDAD ALTA
- components/_app.scss (26 ocurrencias) - PRIORIDAD ALTA
- _admin.scss (24 ocurrencias) - PRIORIDAD MEDIA
- pages/_admin.scss (20 ocurrencias) - PRIORIDAD MEDIA
- Otros archivos (14 ocurrencias) - PRIORIDAD BAJA

**Estrategia:**
1. Auditar contexto de cada font-size pequeño
2. Aumentar a mínimo 1rem donde sea texto de lectura
3. Mantener 0.9rem solo para labels/captions secundarios
4. Aumentar font-weight a 500-600 donde sea necesario

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
