# MIGRACIÓN A VUE REAL - Proceso Completo

## OBJETIVO
Migrar TODO el sitio CDS de SASS global → Vue real (componentes auto-contenidos con estilos inline/scoped mínimos)

## PRINCIPIOS
- ✅ **Aditivo, no destructivo ni sustractivo**
- ✅ **Deconstructivo**: desarmar para armar algo nuevo
- ✅ **Si existe, se ocupa; si no, se crea**
- ✅ **Sin inventar variables**, usar lo que hay
- ✅ **Leer todo completo** antes de cambiar
- ❌ **NO inventar** cosas que no se piden

---

## EJEMPLO COMPLETADO: PageSection.vue

### ANTES (SASS global):
```vue
<template>
  <section class="foxy-section" :class="classList">
    <!-- Depende de _layout.scss -->
  </section>
</template>

<script setup>
const classList = computed(() =>
  props.variant ? `foxy-section-${props.variant}` : ''
)
</script>

<style scoped lang="scss">
@use "@/scss/_core.scss" as *;

section.foxy-section {
  opacity: 0;
  @include dynamic-styles-hash((
    xxxl: (padding: 5rem 0),
    xxl: (padding: 4rem 0),
    // etc...
  ));
  background-color: var(--color-light);
}
</style>
```

**Problemas:**
- ❌ Depende de clases CSS globales
- ❌ Usa mixins SASS
- ❌ Estilos en archivo separado (_layout.scss)
- ❌ Padding responsive con SASS

---

### DESPUÉS (Vue REAL):
```vue
<template>
  <section
    ref="sectionRef"
    :id="id"
    :style="sectionStyles"
    :class="animationClass">
    <!-- Estilos 100% controlados por Vue -->
  </section>
</template>

<script setup>
// Colores existentes (copiados de _variables.scss)
const COLORS = {
  light: '#d3d0c3',
  primary: '#ec6b00',
  primaryLight: '#f9d4b3',
  dark: '#3e3c38',
  darkLight: '#565450',
  white: '#ffffff'
}

// Breakpoints existentes
const BREAKPOINTS = {
  sm: 576,
  md: 768,
  lg: 992,
  xl: 1200,
  xxl: 1400,
  xxxl: 1600
}

// Responsive con Vue (NO con SASS)
const windowWidth = ref(window.innerWidth)
const updateWidth = () => { windowWidth.value = window.innerWidth }

onMounted(() => window.addEventListener('resize', updateWidth))
onBeforeUnmount(() => window.removeEventListener('resize', updateWidth))

// Padding responsive con computed
const sectionPadding = computed(() => {
  const w = windowWidth.value
  if (w >= BREAKPOINTS.xxxl) return '5rem 0 5.5rem'
  if (w >= BREAKPOINTS.xxl) return '4rem 0 4.5rem'
  if (w >= BREAKPOINTS.lg) return '3rem 0 3.5rem'
  if (w >= BREAKPOINTS.md) return '3rem 0 3.5rem'
  return '2.5rem 0 3rem'
})

// Estilos dinámicos con computed
const sectionStyles = computed(() => {
  const baseStyles = {
    position: 'relative',
    padding: sectionPadding.value,
    opacity: animationClass.value === 'is-visible' ? 1 : 0,
    transform: animationClass.value === 'is-visible' ? 'translateY(0)' : 'translateY(16px)',
    transition: 'opacity 0.6s ease, transform 0.6s ease'
  }

  const variants = {
    default: { backgroundColor: COLORS.light },
    primary: { backgroundColor: COLORS.primaryLight },
    dark: { backgroundColor: COLORS.darkLight, color: COLORS.white },
    promo: { backgroundColor: 'transparent' }
  }

  return { ...baseStyles, ...(variants[props.variant] || variants.default) }
})
</script>

<style scoped>
/* Scoped SOLO para selectores descendientes que no se pueden inline */
section[data-variant="dark"] h5 {
  color: #adb5bd;
}
</style>
```

**Ventajas:**
- ✅ NO depende de SASS global
- ✅ Estilos inline controlados por Vue
- ✅ Props con validación
- ✅ Computed properties para lógica
- ✅ Responsive con Vue (window.innerWidth)
- ✅ Scoped CSS SOLO para lo necesario
- ✅ Auto-contenido (se puede reusar sin SASS)

---

## PROCESO PASO A PASO (Replicar en todos los componentes)

### 1. LEER TODO
```bash
# Leer el componente actual
cat src/vue/components/.../MiComponente.vue

# Buscar qué clases CSS usa
grep -n "class=" src/vue/components/.../MiComponente.vue

# Buscar estilos en SASS global
grep -rn ".mi-clase" src/scss/
```

### 2. IDENTIFICAR VARIABLES EXISTENTES
```bash
# Buscar valores de colores
grep "^\$color-primary:" src/scss/abstracts/_variables.scss
grep "^\$color-dark:" src/scss/abstracts/_variables.scss

# NO inventar colores nuevos, usar los existentes
```

**Variables existentes (usar ESTAS):**
```scss
// Colores
$color-primary: #ec6b00
$color-dark: #3e3c38
$color-light: #d3d0c3
$color-white: #ffffff
$color-success: #038600
$color-danger: #dc3545
$color-warning: #ffc107

// Espaciado
$spacer: 1rem
$spacer-sm: 0.5rem
$spacer-md: 1rem
$spacer-lg: 1.5rem
$spacer-xl: 2rem

// Breakpoints
sm: 576px
md: 768px
lg: 992px
xl: 1200px
xxl: 1400px
xxxl: 1600px
```

### 3. CREAR COMPUTED PROPERTIES
```vue
<script setup>
// Props tipadas
const props = defineProps({
  variant: {
    type: String,
    default: 'default',
    validator: (v) => ['default', 'primary', 'dark'].includes(v)
  },
  size: {
    type: String,
    default: 'md',
    validator: (v) => ['sm', 'md', 'lg'].includes(v)
  }
})

// Colores (copiar valores exactos de _variables.scss)
const COLORS = {
  primary: '#ec6b00',
  dark: '#3e3c38',
  light: '#d3d0c3'
}

// Computed para estilos dinámicos
const styles = computed(() => {
  const base = {
    padding: '1rem',
    borderRadius: '8px'
  }

  const variants = {
    default: { backgroundColor: COLORS.light },
    primary: { backgroundColor: COLORS.primary, color: 'white' },
    dark: { backgroundColor: COLORS.dark, color: 'white' }
  }

  const sizes = {
    sm: { padding: '0.5rem', fontSize: '0.875rem' },
    md: { padding: '1rem', fontSize: '1rem' },
    lg: { padding: '1.5rem', fontSize: '1.125rem' }
  }

  return {
    ...base,
    ...variants[props.variant],
    ...sizes[props.size]
  }
})
</script>

<template>
  <div :style="styles">
    <slot />
  </div>
</template>
```

### 4. RESPONSIVE CON VUE (NO con SASS)
```vue
<script setup>
const BREAKPOINTS = {
  sm: 576,
  md: 768,
  lg: 992,
  xl: 1200,
  xxl: 1400
}

const windowWidth = ref(window.innerWidth)
const updateWidth = () => { windowWidth.value = window.innerWidth }

onMounted(() => window.addEventListener('resize', updateWidth))
onBeforeUnmount(() => window.removeEventListener('resize', updateWidth))

const responsiveStyles = computed(() => {
  const w = windowWidth.value

  if (w >= BREAKPOINTS.xl) {
    return { padding: '3rem', fontSize: '1.5rem' }
  } else if (w >= BREAKPOINTS.lg) {
    return { padding: '2rem', fontSize: '1.25rem' }
  } else if (w >= BREAKPOINTS.md) {
    return { padding: '1.5rem', fontSize: '1rem' }
  } else {
    return { padding: '1rem', fontSize: '0.875rem' }
  }
})
</script>
```

### 5. ELIMINAR DEL SASS GLOBAL
```scss
// En src/scss/_layout.scss o donde esté

// ============================================
// MIGRADO A VUE: src/vue/components/.../MiComponente.vue
// Los estilos ahora están en el componente Vue
// Se puede ELIMINAR después de verificar
// ============================================
// .mi-clase {
//   padding: 1rem;
//   background: $color-primary;
// }
```

### 6. SCOPED CSS SOLO PARA CASOS ESPECIALES
```vue
<style scoped>
/* SOLO para:
   - Selectores descendientes (.parent > .child)
   - Pseudo-elementos (::before, ::after)
   - Pseudo-clases complejas (:nth-child, :hover con lógica)
   - Animaciones @keyframes
*/

/* Ejemplo: selector descendiente */
section[data-variant="dark"] h5 {
  color: #adb5bd;
}

/* Ejemplo: pseudo-elemento */
.badge::before {
  content: '';
  position: absolute;
}

/* Ejemplo: animación */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.animated {
  animation: fadeIn 0.3s ease;
}
</style>
```

---

## CASOS ESPECIALES

### A. Componentes con Bootstrap (btn, form-control)
**NO migrar todavía** - esperar a crear sistema de componentes custom

Componentes que usan Bootstrap:
- Botones → Esperar Button.vue custom
- Forms → Esperar Input.vue, Select.vue custom
- Grid → Esperar Grid.vue custom

### B. Componentes con lógica compleja
**Migrar en fases:**
1. Primero: estilos simples (colores, tamaños)
2. Segundo: estilos responsive
3. Tercero: animaciones y transiciones

### C. Componentes legacy sin props
**Añadir props progresivamente:**
```vue
// ANTES
<div class="card card-primary">

// DESPUÉS
<div :style="cardStyles">

<script setup>
const props = defineProps({
  variant: { type: String, default: 'default' }
})

const cardStyles = computed(() => ({
  padding: '1.5rem',
  borderRadius: '8px',
  backgroundColor: props.variant === 'primary' ? '#ec6b00' : '#d3d0c3'
}))
</script>
```

---

## CHECKLIST POR COMPONENTE

- [ ] 1. Leer componente actual
- [ ] 2. Identificar clases CSS que usa
- [ ] 3. Buscar estilos en SASS global
- [ ] 4. Identificar variables SASS usadas (copiar valores exactos)
- [ ] 5. Crear computed properties para estilos
- [ ] 6. Reemplazar clases por :style
- [ ] 7. Responsive con windowWidth (si aplica)
- [ ] 8. Scoped CSS SOLO para casos especiales
- [ ] 9. Comentar/eliminar del SASS global
- [ ] 10. Probar en navegador
- [ ] 11. Verificar responsive en todos los breakpoints
- [ ] 12. Commit con mensaje: "migrate: [ComponentName] to Vue real"

---

## ESTADÍSTICAS DE PROGRESO

### Componentes Migrados: 1/127 (0.8%)
- ✅ PageSection.vue (100% Vue)

### SASS Eliminado
- ✅ _layout.scss: 57 líneas (PageSection)

### Próximos componentes a migrar
1. PageSectionHeader.vue
2. PageSectionContent.vue
3. PageSectionFooter.vue
4. BackgroundPromo.vue
5. PageWrapper.vue

### Meta Final
- **127 componentes** → 100% Vue
- **~8,000 líneas SASS** → casi 0
- **components/_app.scss (105KB)** → eliminar completamente

---

## RESULTADO ESPERADO

### ANTES (actual):
```
src/scss/
├── main.scss (orquestador)
├── _layout.scss (914 líneas)
├── _public.scss (4,575 líneas)
├── _admin.scss (1,871 líneas)
├── components/_app.scss (105KB)
└── pages/_admin.scss (1,220 líneas)

Total: ~8,000 líneas de SASS global
```

### DESPUÉS (meta):
```
src/scss/
├── _variables.scss (solo variables globales)
└── _critical.scss (solo estilos críticos que no se pueden migrar)

Total: ~500 líneas de SASS (reducción del 94%)

src/vue/components/
└── Cada componente con sus propios estilos inline/scoped
```

---

## NOTAS IMPORTANTES

1. **NO eliminar SASS hasta verificar** - comentar primero, eliminar después
2. **Usar valores exactos de variables existentes** - NO inventar colores
3. **Props con validación** - siempre validator en props
4. **Computed para lógica** - NO mezclar estilos en template
5. **Responsive con Vue** - NO con media queries SASS
6. **Scoped CSS mínimo** - solo para casos especiales
7. **Probar en todos los breakpoints** - usar DevTools responsive
8. **Commit por componente** - NO cambios masivos

---

## COMANDOS ÚTILES

```bash
# Buscar componentes que usan una clase
grep -rn "foxy-section" src/vue/

# Buscar estilos de una clase en SASS
grep -rn ".foxy-section" src/scss/

# Contar líneas de SASS
wc -l src/scss/**/*.scss

# Buscar variables SASS
grep "^\$color-" src/scss/abstracts/_variables.scss

# Ver tamaño de archivos SASS
du -h src/scss/components/_app.scss
```

---

Este documento debe actualizarse conforme se migran componentes.
Última actualización: [Fecha actual]
