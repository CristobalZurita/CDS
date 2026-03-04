# Resultado Migracion CSS

## Alcance real de esta pasada

Esta migracion se hizo de forma progresiva en tres frentes de bajo riesgo:

- consolidacion del patron repetido de paginas admin
- reduccion de utilidades duplicadas en wizards/formularios admin
- extraccion de estilos repetidos de auth/public hacia la capa compartida ya existente
- consolidacion del bloque legal publico dentro de la capa `_public.scss` ya existente

En la pasada mas reciente se agrego ademas una consolidacion estructural de calculadoras:

- extraccion del footer repetido de cuatro calculadoras grandes a [src/vue/components/footer/WorkshopFooter.vue](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/vue/components/footer/WorkshopFooter.vue)
- cobertura nueva para `useCalculator`, modelos de calculadora y el footer compartido

## Archivos modificados

### Capa compartida

- [src/scss/components/_app.scss](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/scss/components/_app.scss)
- [src/scss/pages/_admin.scss](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/scss/pages/_admin.scss)
- [src/scss/_public.scss](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/scss/_public.scss)
- [src/vue/components/footer/WorkshopFooter.vue](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/vue/components/footer/WorkshopFooter.vue)

### Paginas admin consolidadas

- [src/vue/content/pages/admin/TicketsPage.vue](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/vue/content/pages/admin/TicketsPage.vue)
- [src/vue/content/pages/admin/ManualsPage.vue](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/vue/content/pages/admin/ManualsPage.vue)
- [src/vue/content/pages/admin/ArchivePage.vue](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/vue/content/pages/admin/ArchivePage.vue)
- [src/vue/content/pages/admin/CategoriesPage.vue](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/vue/content/pages/admin/CategoriesPage.vue)
- [src/vue/content/pages/admin/PurchaseRequestsPage.vue](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/vue/content/pages/admin/PurchaseRequestsPage.vue)

### Wizards / formularios reducidos

- [src/vue/components/admin/wizard/WizardClientIntake.vue](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/vue/components/admin/wizard/WizardClientIntake.vue)
- [src/vue/components/admin/UnifiedIntakeForm.vue](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/vue/components/admin/UnifiedIntakeForm.vue)
- [src/vue/components/admin/wizard/WizardPurchaseRequest.vue](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/vue/components/admin/wizard/WizardPurchaseRequest.vue)
- [src/vue/components/admin/wizard/WizardSignatureRequest.vue](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/vue/components/admin/wizard/WizardSignatureRequest.vue)

### Auth / public consolidado

- [src/vue/components/auth/LoginForm.vue](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/vue/components/auth/LoginForm.vue)
- [src/vue/components/auth/PasswordReset.vue](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/vue/components/auth/PasswordReset.vue)
- [src/vue/content/pages/RegisterPage.vue](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/vue/content/pages/RegisterPage.vue)
- [src/vue/content/pages/TermsPage.vue](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/vue/content/pages/TermsPage.vue)
- [src/vue/content/pages/PrivacyPage.vue](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/vue/content/pages/PrivacyPage.vue)

### Cobertura progresiva agregada

- [tests/unit/layout/PageWrapper.test.ts](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/tests/unit/layout/PageWrapper.test.ts)
- [tests/unit/models/SectionInfo.test.ts](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/tests/unit/models/SectionInfo.test.ts)
- [tests/unit/public/StaticShellPages.test.ts](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/tests/unit/public/StaticShellPages.test.ts)
- [tests/unit/public/LegalPages.test.ts](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/tests/unit/public/LegalPages.test.ts)
- [tests/unit/composables/useCalculator.test.ts](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/tests/unit/composables/useCalculator.test.ts)
- [tests/unit/domain/calculatorModels.test.ts](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/tests/unit/domain/calculatorModels.test.ts)
- [tests/unit/footer/WorkshopFooter.test.ts](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/tests/unit/footer/WorkshopFooter.test.ts)

### Reportes

- [reports/css-audit.md](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/reports/css-audit.md)
- [reports/frontend-state-map.md](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/reports/frontend-state-map.md)

## Patrones consolidados

Se movio a la capa global admin existente:

- shell vertical base de pagina admin/purchase
- header de pagina
- titulo de pagina
- grupos de acciones
- panel/card base
- envoltorios de tabla
- tabla base
- botones admin/purchase y variantes comunes
- inputs/selects admin/purchase
- responsive base para estas paginas

Esto evita seguir repitiendo el mismo bloque en cada SFC `scoped`.

En la capa publica se consolido ademas:

- `terms` y `privacy` comparten ahora el mismo bloque estructural base en [src/scss/_public.scss](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/scss/_public.scss)
- los selectores genericos `.actions`, `.btn-back`, `.btn-next` y `.last-updated` quedaron acotados a `terms/privacy`, evitando derrame sobre otras paginas publicas

## Reduccion observada

Tomando `git diff --numstat` sobre los archivos de estilos afectados en esta pasada:

- lineas locales removidas o sustituidas en componentes/paginas: aproximadamente 805
- lineas centralizadas/agregadas en la capa compartida y overrides minimos: aproximadamente 186

Tomando solo la segunda ola auth/public:

- lineas locales removidas en SFC auth/public: aproximadamente 354
- lineas agregadas/centralizadas en la capa compartida auth existente: aproximadamente 148

No se eliminaron partials SCSS ni se borro infraestructura legacy. Esta pasada solo consolidó uso repetido.

## Overrides minimos mantenidos

Se conservaron overrides locales cuando seguian siendo realmente especificos:

- `TicketsPage`: ancho minimo del selector de estado
- `ArchivePage`: tamano del input principal de busqueda
- `CategoriesPage`: titulo del panel de formulario
- `PurchaseRequestsPage`: badge, notice, alert, estado de pago y link propios
- `UnifiedIntakeForm`: cards internas, botones propios, alertas y estado `.is-invalid`
- `WizardPurchaseRequest`: layout de grilla y alert de confirmacion
- `WizardSignatureRequest`: layout de grilla

## Validacion real

Comandos ejecutados despues de la migracion:

- `npm run build`
- `npm run test:coverage`
- `cd backend && .venv/bin/python -m pytest -q`
- `bash scripts/run_tests.sh`

Resultados:

- `npm run build` -> OK
- `npm run test:coverage` -> ejecuta y genera reporte, pero falla por thresholds globales
  - `44` test files
  - `218 passed`
  - coverage total:
    - lines/statements: `45.63%`
    - functions: `48.19%`
    - branches: `62.47%`
- `cd backend && .venv/bin/python -m pytest -q` -> OK
  - `64 passed`
  - `13 skipped`
  - `1 warning`
- `bash scripts/run_tests.sh` -> OK
- backend del runner -> `13 passed`
- playwright del runner -> `9 passed`

Observacion real:

- `scripts/run_tests.sh` cae a `pytest` sin coverage cuando `pytest-cov` no esta instalado en `backend/.venv`
- el warning backend que sigue vivo hoy viene desde `passlib` importando `crypt`, no desde codigo CDS modificado en esta pasada
- `npm run test:coverage` sigue siendo util para generar el informe, pero no puede considerarse verde mientras los thresholds globales sigan en `90/90/85/90`

## Lo que no se movio todavia

- capas SCSS globales legacy fuera del patron admin
- tokenizacion adicional en `:root`
- cualquier eliminacion de partials o dead code fisico

## Siguiente corte natural

Si se sigue esta misma estrategia, el siguiente paso de bajo riesgo es:

- reauditar paginas publicas mas amplias fuera de auth
- seguir consolidando solo duplicaciones comprobables
- subir cobertura en wrappers `.ts`/dominios que hoy siguen en `0%`
- recien despues marcar candidatos a SCSS muerto con evidencia
