# Auditoria CSS Actual

## Resumen

- El frontend carga un solo entry point global en [src/main.js](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/main.js): `src/scss/main.scss`.
- La arquitectura actual ya mezcla SCSS global + estilos de componente en Vue. No parte de una base "todo global" ni "todo scoped".
- La capa vendor sigue siendo real y activa: Bootstrap, FontAwesome y PrimeIcons se cargan desde [src/scss/vendors/_index.scss](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/scss/vendors/_index.scss).
- Los estilos Vue no están desordenados por falta de `scoped`: los 25 bloques `<style>` encontrados en `src/` ya usan `scoped`.

## Capas Globales Reales

### Entry point

- [src/scss/main.scss](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/scss/main.scss)
  - vendors
  - reset
  - layout
  - sections
  - typography
  - global
  - admin
  - public
  - pages/admin
  - components

### Vendor layer

- [src/scss/vendors/_index.scss](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/scss/vendors/_index.scss)
  - Bootstrap SCSS compilado con variables del proyecto
  - FontAwesome CSS
  - PrimeIcons CSS
  - Google Fonts

### Fuente de variables Sass

- [src/scss/abstracts/_variables.scss](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/scss/abstracts/_variables.scss)
  - paleta principal
  - aliases legacy
  - escalas tipograficas
  - spacing
  - radios
  - sombras
  - transiciones

### Puente Sass -> CSS custom properties

- [src/scss/_global.scss](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/scss/_global.scss)
  - ya expone variables runtime en `:root`
  - no hace falta crear una segunda capa tipo `tokens.css`

Variables CSS ya publicadas:

- `--color-primary`
- `--color-dark`
- `--color-light`
- `--color-white`
- `--color-danger`
- `--color-warning`
- `--color-info`
- `--text-xs`
- `--text-sm`
- `--text-base`
- `--text-lg`
- `--text-xl`
- `--spacer-sm`
- `--spacer-md`
- `--spacer-lg`
- `--radius-sm`
- `--radius-md`
- `--radius-lg`
- `--shadow-sm`
- `--shadow-md`
- `--transition-base`

### Capa Sass consumida desde Vue

- 24 componentes con `style scoped lang="scss"` importan [src/scss/_core.scss](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/scss/_core.scss)
- `_core.scss` solo reexporta variables y mixins; no añade CSS por si mismo

## Estado de Vue Styles

### Bloques `<style>`

- Bloques `<style>` en componentes Vue: 25
- Bloques `scoped`: 25
- Bloques no scoped: 0

### Uso de custom properties en Vue

- Los estilos Vue ya consumen de forma dominante `var(--...)`
- El problema principal no es "migrar Sass a CSS variables", porque esa migracion parcial ya existe

## Duplicacion Real Detectada

### 1. Patron de paginas admin repetido

Archivos con la misma estructura base repetida en local:

- [src/vue/content/pages/admin/TicketsPage.vue](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/vue/content/pages/admin/TicketsPage.vue)
- [src/vue/content/pages/admin/ManualsPage.vue](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/vue/content/pages/admin/ManualsPage.vue)
- [src/vue/content/pages/admin/ArchivePage.vue](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/vue/content/pages/admin/ArchivePage.vue)
- [src/vue/content/pages/admin/CategoriesPage.vue](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/vue/content/pages/admin/CategoriesPage.vue)
- [src/vue/content/pages/admin/PurchaseRequestsPage.vue](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/vue/content/pages/admin/PurchaseRequestsPage.vue)

Selectores repetidos:

- contenedor vertical de pagina
- header con `justify-content: space-between`
- title
- acciones
- panel/card base
- envoltorio de tabla
- tabla base
- botones con variantes `success`, `primary`, `secondary`, `danger`, `ghost`
- inputs/selects basicos de admin

Esto calza mejor como extension de [src/scss/pages/_admin.scss](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/scss/pages/_admin.scss) que como mas CSS local repetido.

### 2. Wizards y formularios que reimplementan Bootstrap/admin globals

Archivos con mayor duplicacion local de utilidades ya presentes:

- [src/vue/components/admin/wizard/WizardClientIntake.vue](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/vue/components/admin/wizard/WizardClientIntake.vue)
- [src/vue/components/admin/UnifiedIntakeForm.vue](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/vue/components/admin/UnifiedIntakeForm.vue)
- [src/vue/components/admin/wizard/WizardPurchaseRequest.vue](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/vue/components/admin/wizard/WizardPurchaseRequest.vue)
- [src/vue/components/admin/wizard/WizardSignatureRequest.vue](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/vue/components/admin/wizard/WizardSignatureRequest.vue)

Duplicaciones observadas:

- `.row`, `.col-*`
- `.d-flex`, `.justify-content-*`, `.align-items-*`
- `.form-label`, `.form-control`, `.form-select`
- `.btn`, `.btn-primary`, `.btn-outline-*`, `.btn-sm`
- `.alert`
- `.mt-*`

En estos casos el riesgo bajo es quitar redefiniciones redundantes y conservar solo:

- layout propio del wizard
- cards o paneles exclusivos del componente
- estados propios como `.is-invalid`

### 3. Lo que no conviene migrar a ciegas

- La capa vendor de Bootstrap
- resets, tipografia base y layout global
- variables Sass legacy mientras sigan siendo usadas por capas globales
- transiciones hover/focus que no son equivalentes a `<Transition>`

## Transiciones y estados

- El repo tiene uso muy bajo de `<Transition>` o `<TransitionGroup>` comparado con la cantidad de CSS base
- No existe una oportunidad real para una migracion masiva a `<Transition>` sin inventar flujos
- El uso de `:class` ya existe en varios componentes; no es el principal cuello de botella actual

## Prioridades de migracion recomendadas

### Prioridad A

- Consolidar el patron repetido de paginas admin en [src/scss/pages/_admin.scss](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/scss/pages/_admin.scss)
- Recortar CSS local redundante en las paginas admin ya listadas

### Prioridad B

- Reducir redefiniciones locales de utilidades Bootstrap/admin en wizards y formularios
- Mantener solo layout especifico y estados propios

### Prioridad C

- Reauditar auth/public despues de A y B
- Tocar auth/public solo si la duplicacion sigue siendo clara y de bajo riesgo

## Riesgos reales

- Quitar reglas locales de formularios o botones sin revisar el contexto `admin-content` puede cambiar espaciados si el componente no vive dentro del shell admin
- Cambiar naming o crear una segunda arquitectura de tokens duplicaria el sistema actual
- Borrar partials SCSS ahora seria prematuro: primero hay que consolidar usos y luego marcar candidatos muertos con evidencia
