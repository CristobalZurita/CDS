# Arquitectura SASS - Cirujano de Sintetizadores

## Estructura de Carpetas (7-1 Pattern)

```
scss/
├── abstracts/          # Variables, mixins (SIN output CSS)
│   ├── _variables.scss # ÚNICA fuente de verdad para variables
│   ├── _mixins.scss    # Mixins reutilizables
│   └── _index.scss     # Exporta todo
│
├── base/               # Reset, tipografía base
│   ├── _typography.scss
│   └── _index.scss
│
├── components/         # Botones, cards, forms (futuro)
│   └── _index.scss
│
├── layout/             # Header, footer, secciones
│   ├── _sections.scss
│   └── _index.scss
│
├── pages/              # Estilos por página
│   ├── _admin.scss
│   └── _index.scss
│
├── themes/             # Temas (dark mode, etc.)
│   └── _index.scss
│
├── vendors/            # Overrides de Bootstrap, etc.
│   └── _index.scss
│
├── _core.scss          # IMPORT PARA COMPONENTES VUE
├── main.scss           # ENTRY POINT PRINCIPAL
│
└── [archivos legacy]   # Mantener por compatibilidad
    ├── style.scss      # Entry point antiguo (backup)
    ├── _brand.scss     # Fuentes
    ├── _variables.scss # Variables antiguas
    └── ...
```

## Cómo Usar en la Capa Sass

### CORRECTO - Heredar del sistema global
```scss
@use "@/scss/_core.scss" as *;

.mi-componente {
    color: $color-primary;
    background: $color-light;

    p {
        @include text-body;
    }

    h2 {
        @include h2-style;
    }

    .content {
        @include section-content;
    }
}
```

### INCORRECTO - Hardcodear valores
```scss
.mi-componente {
    // ❌ NO hacer esto - pisa los estilos globales
    color: #ec6b00;
    font-size: 14px;

    p {
        font-size: 0.9rem;
        line-height: 1.4;
    }
}
```

## Variables Disponibles

### Colores
```scss
$color-primary        // #ec6b00 - Naranja principal
$color-primary-light  // #e8935a - Naranja pastel
$color-dark          // #3e3c38 - Negro vintage
$color-light         // #d3d0c3 - Beige vintage
$color-white         // #ffffff
$color-success       // #038600
$color-warning       // #ffc107
$color-danger        // #dc3545
```

### Escala de Texto (USAR SOLO ESTOS)
```scss
// De 67 valores encontrados → Reducido a 9
$text-2xs   // 0.75rem   = 12px - Badges, labels mínimos
$text-xs    // 0.8125rem = 13px - Texto muy pequeño
$text-sm    // 0.875rem  = 14px - Captions, metadata
$text-base  // 1rem      = 16px - Texto normal ← DEFAULT
$text-md    // 1.0625rem = 17px - Texto medio
$text-lg    // 1.125rem  = 18px - Texto grande
$text-xl    // 1.25rem   = 20px - Texto extra grande
$text-2xl   // 1.5rem    = 24px - Lead text
```

### Headings (Responsivos)
```scss
$h6-size    // 1.125rem                             = 18px
$h5-size    // 1.25rem                              = 20px
$h4-size    // 1.5rem                               = 24px
$h3-size    // clamp(1.75rem, 2vw + 1rem, 2.25rem)  = 28-36px
$h2-size    // clamp(2rem, 2.5vw + 1rem, 2.75rem)   = 32-44px
$h1-size    // clamp(2.5rem, 3vw + 1rem, 3.5rem)    = 40-56px
$display-size // clamp(3rem, 4vw + 1rem, 4.5rem)    = 48-72px (Hero)
```

### Line Heights (Solo 5)
```scss
$lh-none     // 1   - Iconos, inline
$lh-tight    // 1.2 - Headings grandes
$lh-snug     // 1.4 - Headings pequeños
$lh-normal   // 1.5 - Texto UI
$lh-relaxed  // 1.6 - Texto corrido ← DEFAULT
$lh-loose    // 1.8 - Mucho espacio
```

### Letter Spacing (Solo 5)
```scss
$ls-tighter  // -0.02em - Headings grandes
$ls-tight    // -0.01em - Headings
$ls-normal   // 0       - Default
$ls-wide     // 0.02em  - UI elements
$ls-wider    // 0.05em  - Buttons, labels ← MÁS USADO
$ls-widest   // 0.1em   - All caps
```

### Font Weights
```scss
$fw-light     // 300
$fw-normal    // 400
$fw-medium    // 500
$fw-semibold  // 600 ← MÁS USADO (105 veces en proyecto)
$fw-bold      // 700
$fw-extrabold // 800
```

### Espaciado
```scss
$spacer-xs   // 4px
$spacer-sm   // 8px
$spacer-md   // 16px
$spacer-lg   // 24px
$spacer-xl   // 32px
$spacer-xxl  // 48px
```

## Mixins Disponibles

### Tipografía
```scss
@include text-body;        // Párrafo estándar
@include text-small;       // Texto pequeño
@include text-large;       // Texto grande
@include h1-style;         // Estilo H1
@include h2-style;         // Estilo H2
// ... hasta h6-style
@include heading-style;    // Base para headings
@include readable-content; // Contenedor de lectura óptima
```

### Layout
```scss
@include section-content;  // Contenido de sección pública
@include flex-center;      // Centrar con flexbox
@include flex-between;     // Space-between con flexbox
@include flex-column;      // Columna flexbox
```

### Admin
```scss
@include admin-section;    // Card de sección admin
@include admin-title;      // Título de sección admin
@include form-input;       // Input de formulario
@include form-label;       // Label de formulario
```

### Interactivos
```scss
@include hover-lift;       // Efecto hover con elevación
@include focus-ring;       // Anillo de focus accessible
@include custom-scrollbar; // Scrollbar personalizado
```

## Proceso de Migración de Componentes

Para limpiar un componente Vue que tiene estilos hardcodeados:

1. Usar `_core.scss` con `@use`
2. Reemplazar valores hardcodeados por variables
3. Usar mixins en vez de redefinir estilos
4. Eliminar `!important` innecesarios

### Ejemplo de migración:

**ANTES:**
```scss
.section h2 {
    font-size: 28px;
    font-weight: bold;
    color: #3e3c38;
    margin-bottom: 20px;
}
.section p {
    font-size: 16px;
    line-height: 1.5;
    color: #5a5652;
}
```

**DESPUÉS:**
```scss
@use "@/scss/_core.scss" as *;

.section {
    h2 {
        @include h2-style;
        margin-bottom: $spacer-lg;
    }
    p {
        @include text-body;
        color: $text-color-muted;
    }
}
```

## Rollback

Si algo se rompe, en `src/main.js` cambiar:
```js
import "./scss/main.scss"
```
Por:
```js
import "./scss/style.scss"
```
