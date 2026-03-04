# Mapa de Estado Frontend

Estado auditado despues de la pasada progresiva del 2026-03-04 (actualizado al cierre del dia).

## Resumen ejecutivo

- CDS ya funciona como una SPA Vue real en router, auth, stores, cliente API y paneles cliente/admin.
- La arquitectura de estilos sigue siendo hibrida y controlada: `src/scss/main.scss` sigue siendo el entry global real, con consolidacion progresiva de patrones repetidos.
- El cuello de botella actual ya no es "migrar Sass a CSS variables", sino reducir duplicacion puntual JS/TS y subir cobertura fuera del bloque de calculadoras.

## Capas reales del frontend

### Controlado en Vue

- [src/router/index.ts](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/router/index.ts)
- wrappers JS -> TS activos en composables y stores principales (`auth`, `inventory`, `quotation`, `repairs`, `categories`, `users`, `instruments`, `diagnostics`, `stockMovements`)
- auth UI y guards ya cubiertos por tests
- panel cliente base y varios flujos admin ya cubiertos
- cliente API real en [src/services/api.ts](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/services/api.ts)

### Hibrido controlado

- entry global de estilos en [src/scss/main.scss](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/scss/main.scss)
- capas compartidas reales:
  - [src/scss/pages/_admin.scss](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/scss/pages/_admin.scss)
  - [src/scss/components/_app.scss](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/scss/components/_app.scss)
  - [src/scss/_public.scss](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/scss/_public.scss)
- paginas shell publicas montadas con `PageWrapper`
- varias paginas publicas con `scoped` local encima de la capa global

### Hibrido con deuda visible

- los modulos grandes en [src/modules](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/modules) ya tienen cobertura de componente, pero siguen con deuda de complejidad visual/canvas
- duplicidad residual JS/TS en parte de `services/*` y en pares JS/TS legacy no unificados por contrato
- superficies grandes sin test en varias capas admin/articles/dashboard, aunque `src/views/*` ya tiene cobertura base

## Foto por cluster

| Cluster | Estado | Evidencia | Nota real |
| --- | --- | --- | --- |
| Router y navegación | Controlado | `src/router/index.ts` con cobertura alta | El comportamiento real de redirects ya tiene pruebas unitarias y E2E. |
| Auth y sesión | Controlado | `LoginForm`, `PasswordReset`, store auth, flujos E2E | Sigue existiendo deuda de almacenamiento JWT en `localStorage`; no es un problema de migración CSS. |
| Cliente | Controlado | `tests/unit/client/*`, `integration-flows.spec.ts` | Panel cliente estable en lo validado. |
| Admin base | Controlado parcial | inventario, citas, cotizaciones, manuales, algunos wizards | La superficie admin completa todavia no está cubierta. |
| Public shell/legal | Hibrido controlado | `PageWrapper`, `_public.scss`, tests publicos | Ya no hay tanta duplicacion clara de estilos como en admin/auth. |
| Calculadoras grandes | Controlado parcial | `tests/unit/modules/ResistorColorView.test.ts`, `SmdCapacitorView.test.ts`, `SmdResistorView.test.ts`, `Timer555View.test.ts` | El bloque completo de `src/modules/*` ya corre en verde, con deuda restante centrada en vistas/admin fuera de calculadoras. |
| Calculadoras simples | Controlado parcial | `AwgView`, `LengthView`, `NumberSystemView`, `OhmsLawView`, `TemperatureView`, `tests/unit/modules/CalculatorWrappers.test.ts` | Son wrappers minimos con contrato/calculo y ahora ya tienen cobertura de componente. |
| Dominio TS puro | Mejorando | `src/domain/*/model.ts` | Esta pasada dejo cobertura real para todos los modelos de calculadora. |
| Servicios TS | Controlado parcial | `auth.ts`, `security.ts`, `logging.ts`, `alerts.ts`, `tests/unit/services/*` | Ya no estan en `0%`; la deuda pendiente se mueve a otras capas TS espejo y servicios mas amplios. |

## Lo que se aplico en esta pasada

- Se extrajo el footer repetido de las cuatro calculadoras grandes a [src/vue/components/footer/WorkshopFooter.vue](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/vue/components/footer/WorkshopFooter.vue).
- Se reemplazo ese bloque repetido en:
  - [src/modules/resistorColor/ResistorColorView.vue](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/modules/resistorColor/ResistorColorView.vue)
  - [src/modules/smdCapacitor/SmdCapacitorView.vue](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/modules/smdCapacitor/SmdCapacitorView.vue)
  - [src/modules/smdResistor/SmdResistorView.vue](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/modules/smdResistor/SmdResistorView.vue)
  - [src/modules/timer555/Timer555View.vue](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/modules/timer555/Timer555View.vue)
- Se agrego cobertura de calculadoras para:
  - [tests/unit/composables/useCalculator.test.ts](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/tests/unit/composables/useCalculator.test.ts)
  - [tests/unit/domain/calculatorModels.test.ts](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/tests/unit/domain/calculatorModels.test.ts)
  - [tests/unit/footer/WorkshopFooter.test.ts](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/tests/unit/footer/WorkshopFooter.test.ts)
- Se agrego cobertura de componente para wrappers simples en:
  - [tests/unit/modules/CalculatorWrappers.test.ts](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/tests/unit/modules/CalculatorWrappers.test.ts)
- Se agrego cobertura de componente para calculadoras grandes en:
  - [tests/unit/modules/ResistorColorView.test.ts](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/tests/unit/modules/ResistorColorView.test.ts)
  - [tests/unit/modules/SmdCapacitorView.test.ts](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/tests/unit/modules/SmdCapacitorView.test.ts)
  - [tests/unit/modules/SmdResistorView.test.ts](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/tests/unit/modules/SmdResistorView.test.ts)
  - [tests/unit/modules/Timer555View.test.ts](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/tests/unit/modules/Timer555View.test.ts)
- Se agrego cobertura de servicios TS en:
  - [tests/unit/services/authService.test.ts](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/tests/unit/services/authService.test.ts)
  - [tests/unit/services/security.test.ts](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/tests/unit/services/security.test.ts)
  - [tests/unit/services/logging.test.ts](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/tests/unit/services/logging.test.ts)
  - [tests/unit/services/alerts.test.ts](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/tests/unit/services/alerts.test.ts)
- Se extendio convergencia JS/TS en composables con wrappers aditivos JS -> TS:
  - [src/composables/emails.js](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/composables/emails.js)
  - [src/composables/layout.js](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/composables/layout.js)
  - [src/composables/scheduler.js](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/composables/scheduler.js)
  - [src/composables/utils.js](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/composables/utils.js)
  - [src/composables/useAuth.js](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/composables/useAuth.js)
  - [src/composables/useDiagnostic.js](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/composables/useDiagnostic.js)
  - [src/composables/useDiagnostics.js](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/composables/useDiagnostics.js)
  - [src/composables/useInstruments.js](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/composables/useInstruments.js)
  - [src/composables/useInstrumentsCatalog.js](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/composables/useInstrumentsCatalog.js)
  - [src/composables/useInventory.js](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/composables/useInventory.js)
  - [src/composables/useQuotation.js](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/composables/useQuotation.js)
  - [src/composables/useRepairs.js](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/composables/useRepairs.js)
  - [src/composables/useCategories.js](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/composables/useCategories.js)
  - [src/composables/useUsers.js](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/composables/useUsers.js)
  - [src/composables/useStockMovements.js](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/composables/useStockMovements.js)
- Se extendio convergencia JS/TS en stores con wrappers aditivos JS -> TS:
  - [src/stores/auth.js](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/stores/auth.js)
  - [src/stores/inventory.js](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/stores/inventory.js)
  - [src/stores/quotation.js](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/stores/quotation.js)
  - [src/stores/repairs.js](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/stores/repairs.js)
  - [src/stores/categories.js](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/stores/categories.js)
  - [src/stores/users.js](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/stores/users.js)
  - [src/stores/instruments.js](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/stores/instruments.js)
  - [src/stores/diagnostics.js](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/stores/diagnostics.js)
  - [src/stores/stockMovements.js](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/stores/stockMovements.js)
  - [src/stores/shopCart.js](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/stores/shopCart.js)
- Se agrego cobertura nueva para `src/views/*` y admin base de bajo riesgo:
  - [tests/unit/views/HomeView.test.ts](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/tests/unit/views/HomeView.test.ts)
  - [tests/unit/views/InstrumentDetail.test.ts](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/tests/unit/views/InstrumentDetail.test.ts)
  - [tests/unit/views/InventoryUnified.test.ts](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/tests/unit/views/InventoryUnified.test.ts)
  - [tests/unit/views/ErrorDashboard.test.ts](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/tests/unit/views/ErrorDashboard.test.ts)
  - [tests/unit/admin/BasicAdminComponents.test.ts](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/tests/unit/admin/BasicAdminComponents.test.ts)

## Estado medible actual

- `npm run build` -> OK
- `npm run test -- --run tests/unit/modules` -> `26 passed`
- `npm run test:coverage` -> ejecuta la suite y genera reporte, pero termina en `exit 1` por thresholds globales
  - `58` archivos de test
  - `273 passed`
  - lines/statements: `64.07%`
  - functions: `56.62%`
  - branches: `66.59%`
- `cd backend && .venv/bin/python -m pytest -q` -> `66 passed`, `14 skipped`, `1 warning`
- `bash scripts/run_tests.sh` -> `backend: PASS`, `playwright: PASS`

## Riesgos reales que siguen abiertos

- `npm run test:coverage` no puede considerarse verde mientras existan thresholds globales de `90/90/85/90` con cobertura real de `64.07/56.62/66.59/64.07`.
- La duplicidad JS/TS se redujo en stores/composables principales incluyendo utilitarios (`emails/layout/scheduler/utils`), pero sigue deuda en capas de servicios y módulos admin/articles de gran superficie.

## Siguiente corte natural

- revisar convergencia gradual de `services/*` donde siga habiendo doble capa JS/TS
- seguir cobertura en `src/vue/components/admin/*`, `src/vue/components/articles/*` y `src/vue/components/dashboard/*` (los mayores bloques en 0%)
- recien despues decidir si conviene extraer mas shell comun de calculadoras, por ejemplo el bloque de retorno a `/calculadoras`
