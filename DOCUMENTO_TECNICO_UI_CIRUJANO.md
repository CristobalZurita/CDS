# DOCUMENTO TÉCNICO - ANÁLISIS UI/UX
## Cirujano de Sintetizadores
### Contexto: Firefox 100% / Samsung 19" / 1366x768 / Scale 0.75

---

## 1. HEADER / NAVBAR

### 1.1 Navbar tapado parcialmente por hero
```
PROBLEMA TÉCNICO: z-index incorrecto, hero se superpone al navbar
UBICACIÓN: src/scss/_layout.scss (líneas 466-503)
AJUSTE REQUERIDO:
  - ELIMINAR: .foxy-hero-header-logo.image-view { z-index: 3; }
  - MODIFICAR: header.foxy-header { z-index: 1; }
  - VERIFICAR: nav.foxy-navbar tiene z-index: 10 (correcto en Navbar.vue línea 1574)
```

### 1.2 Tipografía navbar demasiado pequeña
```
PROBLEMA TÉCNICO: font-size insuficiente para resolución 1366x768 con scale 0.75
UBICACIÓN: src/vue/components/nav/navbar/NavbarLinks.vue (líneas 1817-1844)
AJUSTE REQUERIDO:
  - ACTUAL: button.foxy-nav-link sin font-size explícito desktop
  - CAMBIAR A: añadir font-size: 0.95rem; en button.foxy-nav-link
  - EN @media-breakpoint-down(lg): cambiar font-size de 0.85rem a 0.9rem
```

### 1.3 Logo hero desproporcionadamente grande
```
PROBLEMA TÉCNICO: width: 85vw con !important sobreescribe estilos scoped
UBICACIÓN: src/scss/_layout.scss (líneas 466-473)
AJUSTE REQUERIDO:
  - ELIMINAR COMPLETAMENTE el bloque:
    .foxy-hero-header-logo.image-view {
        width: 85vw !important;
        max-width: 1400px !important;
        height: auto !important;
        ...
    }
  - El componente PageHeader.vue ya tiene estilos correctos (líneas 1025-1040)
```

### 1.4 Texto "MANTENCIÓN · RESTAURACIÓN · REPARACIÓN" muy pequeño
```
PROBLEMA TÉCNICO: font-size en h1.heading usa clamp muy conservador
UBICACIÓN: src/vue/components/layout/PageHeader.vue (líneas 1063-1069)
AJUSTE REQUERIDO:
  - ACTUAL: font-size: clamp(28px, 4.4vw, 64px)
  - CAMBIAR A: font-size: clamp(32px, 5vw, 72px)
  - AÑADIR: letter-spacing: 2px; para mejor legibilidad
```

### 1.5 Sección "Sobre el taller" tapada por botones CTA
```
PROBLEMA TÉCNICO: Botones hero-cta-buttons posicionados sin margen inferior suficiente
UBICACIÓN: src/vue/components/layout/PageHeader.vue (líneas 1071-1081)
AJUSTE REQUERIDO:
  - ACTUAL: margin-top: 1rem en .hero-cta-buttons
  - CAMBIAR A: margin: 2rem 0 3rem 0;
  - VERIFICAR: --height en header.foxy-header (línea 1020) debe ser min 55vh
```

### 1.6 Botones "Descubre más" y "Cotiza tu instrumento" sin acción
```
PROBLEMA TÉCNICO: Eventos @click no implementados correctamente
UBICACIÓN: src/vue/components/layout/PageHeader.vue (líneas 1006-1018)
AJUSTE REQUERIDO:
  - Botón "Descubre más": @click="$emit('scroll-to-top')" → CAMBIAR A: @click="scrollToAbout"
  - Añadir método: const scrollToAbout = () => document.getElementById('about')?.scrollIntoView({behavior:'smooth'})
  - Botón "Cotiza": href="#diagnostic-section" → VERIFICAR que existe id="diagnostic-section" en DiagnosticSection.vue
  - ACTUAL en DiagnosticSection.vue línea 3090: id="diagnostico" 
  - CAMBIAR href A: href="#diagnostico" O cambiar id en DiagnosticSection a "diagnostic-section"
```

---

## 2. HERO / CONTENIDO SUPERIOR

### 2.1 Texto descriptivo extremadamente pequeño
```
PROBLEMA TÉCNICO: h4.subheading usa cálculo proporcional muy pequeño
UBICACIÓN: src/vue/components/layout/PageHeader.vue (líneas 1071-1078)
AJUSTE REQUERIDO:
  - ACTUAL: font-size: clamp(16px, calc(var(--logo-proportion)/14), 100px)
  - CAMBIAR A: font-size: clamp(18px, 1.2vw + 14px, 24px)
  - AÑADIR: line-height: 1.6;
```

### 2.2 Jerarquía tipográfica incorrecta
```
PROBLEMA TÉCNICO: Subtítulo tiene padding excesivo, título principal muy pequeño
UBICACIÓN: src/vue/components/layout/PageHeader.vue
AJUSTE REQUERIDO:
  - h1.heading: padding: 1.25rem 0 0.5rem → CAMBIAR A: padding: 1.5rem 0 1rem
  - h4.subheading: padding: calc(var(--logo-proportion)/20) 0 → CAMBIAR A: padding: 0.5rem 0 1rem
```

### 2.3 Texto **Cirujano de Sintetizadores** sin negrita visible
```
PROBLEMA TÉCNICO: parseCustomText() no procesa markdown **texto** correctamente
UBICACIÓN: src/composables/utils.js (función parseCustomText)
AJUSTE REQUERIDO:
  - VERIFICAR que parseCustomText convierte **texto** a <strong>texto</strong>
  - EN AboutSection.vue línea 2282: `**Cirujano de Sintetizadores**` 
  - Si no funciona, CAMBIAR A: `<strong>Cirujano de Sintetizadores</strong>`
```

---

## 3. SECCIÓN "NUESTROS SERVICIOS"

### 3.1 Iconos dependientes de CDN
```
PROBLEMA TÉCNICO: Font Awesome cargado desde CDN externo
UBICACIÓN: src/scss/style.scss (líneas 675-679)
AJUSTE REQUERIDO:
  - Los iconos YA están instalados localmente via npm (@fortawesome/fontawesome-free)
  - VERIFICAR: package.json contiene "@fortawesome/fontawesome-free"
  - VERIFICAR: $fa-font-path apunta a ruta local (línea 273 _variables.scss)
  - Para iconos específicos de servicios: descargar SVGs a /public/images/icons/
```

### 3.2 Texto pequeño y mal compaginado
```
PROBLEMA TÉCNICO: ArticleFeatures o ServicesSection sin estilos de texto adecuados
UBICACIÓN: src/vue/components/articles/ArticleFeatures.vue (no incluido en volcado)
AJUSTE REQUERIDO:
  - Crear/modificar estilos en ServicesSection.vue:
    .service-description { font-size: 1.1rem; line-height: 1.7; }
  - VERIFICAR archivo: src/vue/content/sections/ServicesSection.vue
```

### 3.3 Desalineación iconos vs texto
```
PROBLEMA TÉCNICO: Flex container sin align-items correcto
UBICACIÓN: src/vue/components/articles/ArticleFeatures.vue / ItemFeature.vue
AJUSTE REQUERIDO:
  - Container de feature: display: flex; align-items: flex-start; gap: 1.5rem;
  - Icono: flex-shrink: 0; width: 64px; height: 64px;
```

---

## 4. TÍTULOS DE SECCIONES

### 4.1 Colores inconsistentes
```
PROBLEMA TÉCNICO: PageSectionHeader no tiene sistema de colores unificado
UBICACIÓN: src/vue/components/layout/PageSectionHeader.vue (archivo NO incluido en volcado)
AJUSTE REQUERIDO:
  - CREAR archivo si no existe con:
    .section-title { color: $dark; }
    .section-title strong, .section-title .highlight { color: $primary; }
  - Patrón actual en AboutSection: title="*Sobre* el taller" usa asteriscos para highlight
```

### 4.2 Tamaños inconsistentes
```
PROBLEMA TÉCNICO: Cada sección define su propio tamaño de título
UBICACIÓN: Múltiples archivos de sección
AJUSTE REQUERIDO:
  - CENTRALIZAR en PageSectionHeader.vue o _typography.scss:
    .foxy-section-header-title {
        font-size: clamp(2rem, 3vw + 1rem, 3rem);
        font-family: $headings-font-family;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }
    .foxy-section-header-subtitle {
        font-size: clamp(1rem, 1.2vw + 0.8rem, 1.25rem);
        color: $text-muted;
    }
```

---

## 5. SISTEMA DE COTIZACIÓN

### 5.1 Sistema funcionalmente roto
```
PROBLEMA TÉCNICO: DiagnosticWizard.vue no completa flujo de cotización
UBICACIÓN: src/vue/components/articles/DiagnosticWizard.vue (contenido no incluido completo)
AJUSTE REQUERIDO:
  - VERIFICAR: Wizard tiene steps completos (marca, modelo, fallas, datos cliente)
  - VERIFICAR: Botón final envía POST a backend /api/v1/diagnostics
  - VERIFICAR: useDiagnostic.js tiene método submitDiagnostic()
```

### 5.2 Botón "Cotiza" flotante sin acción
```
PROBLEMA TÉCNICO: FloatingQuoteButton.vue scrollToQuote busca id incorrecto
UBICACIÓN: src/vue/components/widgets/FloatingQuoteButton.vue (líneas 2078-2083)
AJUSTE REQUERIDO:
  - ACTUAL línea 2079: document.getElementById('diagnostic-section')
  - DiagnosticSection usa: id="diagnostico" (línea 3090)
  - CAMBIAR A: document.getElementById('diagnostico')
```

---

## 6. SECCIÓN "NUESTRA HISTORIA"

### 6.1 Diseño y diagramación deficiente
```
PROBLEMA TÉCNICO: ArticleTimeline sin responsive adecuado
UBICACIÓN: src/vue/components/articles/ArticleTimeline.vue (no incluido en volcado)
AJUSTE REQUERIDO:
  - Timeline items deben tener max-width: 800px; margin: 0 auto;
  - Imágenes: width: 100%; max-height: 300px; object-fit: cover;
  - Texto: font-size: 1.05rem; line-height: 1.7;
```

### 6.2 Mala jerarquía de contenido
```
PROBLEMA TÉCNICO: ItemTimelineEntry no tiene estilos de fecha prominentes
UBICACIÓN: src/vue/components/articles/items/ItemTimelineEntry.vue
AJUSTE REQUERIDO:
  - Fecha: font-size: 1.4rem; font-weight: 700; color: $primary;
  - Descripción: font-size: 1rem; color: $text-normal;
```

---

## 7. SECCIÓN "NOVEDADES / GALERÍA" (PortfolioSection/FeaturedProjectSection)

### 7.1 Totalmente desproporcionada
```
PROBLEMA TÉCNICO: ArticleProjectGrid sin grid responsive
UBICACIÓN: src/vue/components/articles/ArticleProjectGrid.vue (no incluido)
AJUSTE REQUERIDO:
  - Grid: display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 2rem;
  - Card: aspect-ratio: 4/3; overflow: hidden;
```

### 7.2 Funcionalidad de galería inexistente
```
PROBLEMA TÉCNICO: No existe componente de galería modal
UBICACIÓN: Crear nuevo componente
AJUSTE REQUERIDO:
  - CREAR: src/vue/components/projects/GalleryModal.vue
  - Cada proyecto debe tener array de imágenes
  - Click en proyecto abre modal con galería
  - Añadir sección "Ver todos los trabajos" con link a /galeria
```

---

## 8. SECCIÓN "PREGUNTAS FRECUENTES"

### 8.1 Tamaños descompaginados
```
PROBLEMA TÉCNICO: ArticleFaq items sin consistencia tipográfica
UBICACIÓN: src/vue/components/articles/ArticleFaq.vue / ItemFaqQuestion.vue
AJUSTE REQUERIDO:
  - Pregunta: font-size: 1.15rem; font-weight: 600;
  - Respuesta: font-size: 1rem; line-height: 1.7; color: $text-normal;
  - Container: padding: 1.5rem; border-bottom: 1px solid rgba(0,0,0,0.1);
```

---

## 9. SECCIÓN "OPINIONES DE CLIENTES"

### 9.1 Descompaginación general
```
PROBLEMA TÉCNICO: ArticleTestimonials / ArticleQuotes sin grid consistente
UBICACIÓN: src/vue/components/articles/ArticleTestimonials.vue
AJUSTE REQUERIDO:
  - Grid: display: grid; grid-template-columns: repeat(3, 1fr); gap: 2rem;
  - @media (max-width: 992px): grid-template-columns: repeat(2, 1fr);
  - @media (max-width: 768px): grid-template-columns: 1fr;
```

### 9.2 Falta icono de Instagram
```
PROBLEMA TÉCNICO: Icono Instagram renderiza como cuadrado genérico
UBICACIÓN: ReviewsSection.vue o ItemTestimonial.vue
AJUSTE REQUERIDO:
  - VERIFICAR: Font Awesome Brands está importado (style.scss línea 679 ✓)
  - Usar clase: fa-brands fa-instagram (no fa-solid)
  - Si persiste: descargar SVG de Instagram a /public/images/icons/instagram.svg
```

### 9.3 Iconos de redes dependientes de recursos externos
```
PROBLEMA TÉCNICO: Iconos deben ser locales
UBICACIÓN: /public/images/icons/
AJUSTE REQUERIDO:
  - Descargar y almacenar:
    /public/images/icons/instagram.svg
    /public/images/icons/facebook.svg
  - Usar como: <img src="/images/icons/instagram.svg" alt="Instagram" />
```

---

## 10. FOOTER (PRIMER NIVEL)

### 10.1 Caja de dirección demasiado grande
```
PROBLEMA TÉCNICO: .contact-box sin max-width, padding excesivo
UBICACIÓN: src/vue/content/sections/ContactSection.vue (líneas 2404-2410)
AJUSTE REQUERIDO:
  - ACTUAL: padding: 24px;
  - CAMBIAR A: padding: 1.25rem; max-width: 280px;
```

### 10.2 Mal contraste de color en caja
```
PROBLEMA TÉCNICO: background muy transparente, texto poco visible
UBICACIÓN: src/vue/content/sections/ContactSection.vue (línea 2409)
AJUSTE REQUERIDO:
  - ACTUAL: background: rgba(255,255,255,0.02);
  - CAMBIAR A: background: rgba(255,255,255,0.08);
  - AÑADIR: color: $light-2;
```

### 10.3 Mapa demasiado angosto
```
PROBLEMA TÉCNICO: Grid 1fr 1fr no optimiza espacio
UBICACIÓN: src/vue/content/sections/ContactSection.vue (líneas 2392-2396)
AJUSTE REQUERIDO:
  - ACTUAL: grid-template-columns: 1fr 1fr;
  - CAMBIAR A: grid-template-columns: minmax(200px, 300px) 1fr;
  - .map-frame: min-height: 350px;
```

---

## 11. FOOTER FINAL

### 11.1 Tipografía demasiado pequeña
```
PROBLEMA TÉCNICO: FooterCopyright sin font-size explícito
UBICACIÓN: src/vue/components/footer/FooterCopyright.vue (no incluido en volcado)
AJUSTE REQUERIDO:
  - AÑADIR: font-size: 0.9rem; color: $light-5;
```

### 11.2 Iconos de redes como cuadrados
```
PROBLEMA TÉCNICO: SocialLinks.vue no tiene estilos de iconos
UBICACIÓN: src/vue/components/widgets/SocialLinks.vue (no incluido en volcado)
AJUSTE REQUERIDO:
  - Usar: <i class="fa-brands fa-instagram"></i>
  - Estilo: font-size: 1.5rem; color: $light-3; transition: color 0.3s;
  - Hover: color: $primary;
```

---

## 12. ELEMENTOS FLOTANTES

### 12.1 Botón scroll-to-top fuera de estilo
```
PROBLEMA TÉCNICO: .scroll-top con estilo genérico negro
UBICACIÓN: src/vue/components/widgets/FloatingQuoteButton.vue (líneas 2210-2231)
AJUSTE REQUERIDO:
  - ACTUAL línea 2220: background: rgba(0,0,0,0.65);
  - CAMBIAR A: background: $primary; border: 2px solid darken($primary, 10%);
  - AÑADIR: font-family: $headings-font-family;
  - Icono: usar fa-arrow-up en lugar de texto "↑"
```

---

## 13. AUTENTICACIÓN / DASHBOARD

### 13.1 No existe acceso visible a login en navbar
```
PROBLEMA TÉCNICO: NavbarLinks no incluye link a /login
UBICACIÓN: src/router/index.js + componente que define linkList
AJUSTE REQUERIDO:
  - En Master.vue o App.vue donde se define linkList para Navbar:
    AÑADIR al array: { path: '/login', label: 'Iniciar Sesión', faIcon: 'fa-solid fa-user' }
  - Ruta YA EXISTE en router (línea 3615): path: '/login'
```

### 13.2 Dashboard no accesible desde UI
```
PROBLEMA TÉCNICO: Rutas existen pero no hay navegación visible
UBICACIÓN: src/router/index.js (líneas 3626-3649)
AJUSTE REQUERIDO:
  - Las rutas /dashboard, /repairs, /profile EXISTEN con meta: { requiresAuth: true }
  - FALTA: Mostrar menú de usuario cuando está autenticado
  - CREAR: UserMenu.vue con links a dashboard/perfil/logout
  - INTEGRAR: en Navbar.vue, mostrar UserMenu si user está autenticado
```

---

## 14. OPTIMIZACIÓN DE LAYOUT

### 14.1 Fusión FAQ + Opiniones
```
PROBLEMA TÉCNICO: Secciones separadas generan scroll excesivo
UBICACIÓN: src/vue/content/pages/HomePage.vue (líneas 3171-3180)
AJUSTE REQUERIDO:
  - CREAR: src/vue/content/sections/FaqReviewsSection.vue
  - Layout: display: grid; grid-template-columns: 1fr 1fr; gap: 4rem;
  - Columna izquierda: FAQ
  - Columna derecha: Opiniones destacadas (3 máximo)
  - Mobile: grid-template-columns: 1fr;
```

---

## RESUMEN DE ARCHIVOS A MODIFICAR

| Archivo | Prioridad | Cambios |
|---------|-----------|---------|
| src/scss/_layout.scss | CRÍTICA | Eliminar estilos hero con !important |
| src/vue/components/layout/PageHeader.vue | ALTA | Ajustar tamaños tipográficos, margins |
| src/vue/components/widgets/FloatingQuoteButton.vue | ALTA | Corregir id selector, estilo scroll-top |
| src/vue/content/sections/ContactSection.vue | MEDIA | Grid mapa/dirección, contraste |
| src/vue/components/nav/navbar/NavbarLinks.vue | MEDIA | Font-size navbar |
| src/vue/sections/DiagnosticSection.vue | MEDIA | Verificar id="diagnostic-section" |
| src/router/index.js | MEDIA | Ya tiene rutas, verificar guards |
| CREAR: PageSectionHeader.vue | MEDIA | Sistema unificado de títulos |
| CREAR: UserMenu.vue | BAJA | Menú usuario autenticado |
| CREAR: GalleryModal.vue | BAJA | Modal galería trabajos |

---

## ORDEN DE IMPLEMENTACIÓN RECOMENDADO

1. **INMEDIATO**: Eliminar estilos conflictivos en _layout.scss
2. **DÍA 1**: Ajustar PageHeader.vue (hero completo)
3. **DÍA 1**: Corregir FloatingQuoteButton (id selector)
4. **DÍA 2**: Unificar sistema de títulos (PageSectionHeader)
5. **DÍA 2**: Ajustar ContactSection (footer)
6. **DÍA 3**: Integrar login en navbar
7. **SEMANA 2**: Crear galería y fusionar FAQ+Opiniones
