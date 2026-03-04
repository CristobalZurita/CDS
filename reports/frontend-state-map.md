# Mapa de Estado Frontend

Estado auditado despues de la pasada progresiva del 2026-03-04.

## Resumen ejecutivo

- CDS ya funciona como una SPA Vue real en router, auth, stores, cliente API y paneles cliente/admin.
- La arquitectura de estilos sigue siendo hibrida y controlada: `src/scss/main.scss` sigue siendo el entry global real, con consolidacion progresiva de patrones repetidos.
- El cuello de botella actual ya no es "migrar Sass a CSS variables", sino reducir duplicacion puntual y subir cobertura sobre superficies TS/Vue que siguen en `0%`.

## Capas reales del frontend

### Controlado en Vue

- [src/router/index.ts](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/router/index.ts)
- stores/composables JS activos usados por la SPA
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

- nueve modulos en [src/modules](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/modules) con cobertura Vue aun en `0%`
- duplicidad paralela JS/TS en `stores/`, `composables/` y parte de `services/`
- superficies grandes sin test en `src/views/`, `src/services/*.ts`, `src/vue/components/dashboard/*`, `src/vue/components/articles/*`

## Foto por cluster

| Cluster | Estado | Evidencia | Nota real |
| --- | --- | --- | --- |
| Router y navegación | Controlado | `src/router/index.ts` con cobertura alta | El comportamiento real de redirects ya tiene pruebas unitarias y E2E. |
| Auth y sesión | Controlado | `LoginForm`, `PasswordReset`, store auth, flujos E2E | Sigue existiendo deuda de almacenamiento JWT en `localStorage`; no es un problema de migración CSS. |
| Cliente | Controlado | `tests/unit/client/*`, `integration-flows.spec.ts` | Panel cliente estable en lo validado. |
| Admin base | Controlado parcial | inventario, citas, cotizaciones, manuales, algunos wizards | La superficie admin completa todavia no está cubierta. |
| Public shell/legal | Hibrido controlado | `PageWrapper`, `_public.scss`, tests publicos | Ya no hay tanta duplicacion clara de estilos como en admin/auth. |
| Calculadoras grandes | Hibrido con deuda | `ResistorColorView`, `SmdCapacitorView`, `SmdResistorView`, `Timer555View` | Esta pasada extrajo el footer repetido a [src/vue/components/footer/WorkshopFooter.vue](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/vue/components/footer/WorkshopFooter.vue). |
| Calculadoras simples | Placeholder real | `AwgView`, `LengthView`, `NumberSystemView`, `OhmsLawView`, `TemperatureView` | Son wrappers minimos con contrato/calculo pero casi sin UI real. |
| Dominio TS puro | Mejorando | `src/domain/*/model.ts` | Esta pasada dejo cobertura real para todos los modelos de calculadora. |
| Servicios TS | Pendiente | `auth.ts`, `security.ts`, `logging.ts`, `alerts.ts` | Siguen en `0%`; son una de las deudas mas claras. |

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

## Estado medible actual

- `npm run build` -> OK
- `npm run test -- --run tests/unit/composables/useCalculator.test.ts tests/unit/domain/calculatorModels.test.ts tests/unit/footer/WorkshopFooter.test.ts` -> `13 passed`
- `npm run test:coverage` -> ejecuta la suite y genera reporte, pero termina en `exit 1` por thresholds globales
  - `44` archivos de test
  - `218 passed`
  - lines/statements: `45.63%`
  - functions: `48.19%`
  - branches: `62.47%`
- `cd backend && .venv/bin/python -m pytest -q` -> `64 passed`, `13 skipped`, `1 warning`
- `bash scripts/run_tests.sh` -> `backend: PASS`, `playwright: PASS`

## Riesgos reales que siguen abiertos

- `npm run test:coverage` no puede considerarse verde mientras existan thresholds globales de `90/90/85/90` con cobertura real de `45.63/48.19/62.47/45.63`.
- Los modulos Vue de calculadoras siguen sin cobertura de componente, aunque la logica pura ya este cubierta.
- La duplicidad JS/TS sigue siendo una deuda estructural: hoy la app usa sobre todo la capa JS activa, mientras varias capas TS espejo siguen en `0%`.

## Siguiente corte natural

- cubrir por componente los modulos de calculadora, empezando por los wrappers simples o por uno grande con menor riesgo de canvas
- atacar servicios TS en `0%` (`auth.ts`, `security.ts`, `logging.ts`, `alerts.ts`)
- recien despues decidir si conviene extraer mas shell comun de calculadoras, por ejemplo el bloque de retorno a `/calculadoras`
