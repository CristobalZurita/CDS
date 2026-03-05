PF1161 - Auditoría Técnica y Plan Priorizado de Cierre (CDS-RESCATE)
Fecha de auditoría: 2026-03-05
Repositorio local: /mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN
Branch auditada: CDS-RESCATE

PHASE 0 - Estado real leído antes de actuar

- Paquete frontend leído: package.json
- Entradas de app leídas: src/main.js:1-69, src/router/index.js:1-337, src/router/index.ts:1
- Variables SASS leídas: src/scss/_variables.scss:1-97
- Auditoría completa de componentes Vue (lectura archivo por archivo) exportada en:
  reports/PF1161_PHASE0_VUE_AUDIT.tsv
- Total archivos .vue auditados: 186
- Clasificación real:
  COMPLIANT: 159
  PARTIAL: 24
  LEGACY WRAPPER: 3
- LEGACY WRAPPER detectados:
  src/vue/components/layout/PageWrapper.vue
  src/vue/components/nav/navbar-wrappers/InPageNavbar.vue
  src/vue/components/nav/navbar-wrappers/RouteNavbar.vue

PHASE 1 - Gap analysis contra PF1161 (Módulos 6 y 7)

REQUIREMENT | STATUS | WHERE IT EXISTS OR WHY IT IS MISSING
v-if usage | found | src/vue/content/pages/admin/InventoryPage.vue:14, src/vue/content/pages/admin/InventoryPage.vue:19, src/vue/content/pages/RepairsPage.vue:32
v-for usage | found | src/vue/components/admin/InventoryTable.vue:14, src/vue/components/admin/InventoryForm.vue:13, src/vue/content/pages/RepairsPage.vue:34
v-model on form | found | src/vue/components/auth/LoginForm.vue:8, src/vue/components/auth/LoginForm.vue:23, src/vue/components/admin/InventoryForm.vue:7
v-bind :class | found | src/vue/content/pages/RepairsPage.vue:43, src/vue/content/sections/AboutSection.vue:63
Vue Router dynamic route | found | src/router/index.js:133, src/router/index.js:177, src/router/index.js:223
404 route | found | src/router/index.js:293, src/vue/content/pages/NotFoundPage.vue:1
props + emit | found | src/vue/components/admin/InventoryForm.vue:61, src/vue/components/admin/InventoryForm.vue:68, src/vue/components/dashboard/RepairCard.vue:23, src/vue/components/dashboard/RepairCard.vue:27
onMounted hook | found | src/vue/content/pages/admin/InventoryPage.vue:168, src/vue/content/pages/RepairsPage.vue:158, src/vue/components/admin/InventoryForm.vue:97
Axios API call | found | src/services/api.js:1, src/services/api.js:5, src/vue/content/pages/RepairsPage.vue:149, src/stores/inventory.js:20
Pinia store | found | src/main.js:5, src/main.js:15, src/stores/auth.js:14, src/stores/inventory.js:4
JWT in frontend | found | src/composables/useAuth.js:69, src/composables/useAuth.js:79, src/composables/useAuth.js:84, src/composables/useAuth.js:154, src/services/api.js:10, src/services/api.js:12, src/router/index.js:311
Complete CRUD in UI | found | Módulo Inventario: src/stores/inventory.js:12 (read), src/stores/inventory.js:52 (create), src/stores/inventory.js:44 (update), src/stores/inventory.js:30 (delete), orquestado en src/vue/content/pages/admin/InventoryPage.vue:83-124 y 95-104
Unit test exists | missing | Existen tests unitarios parciales (tests/unit/components/InventoryForm.spec.js:16, tests/unit/components/InventoryCard.spec.js:6, tests/unit/stores/inventory.spec.js:29), pero no hay al menos 1 test por componente Vue

PHASE 2 - Backend health check (estado real)

- Import backend OK:
  backend imports OK (comando: backend/.venv/bin/python -c "from app.main import app; ...")
- Health endpoint definido:
  backend/app/main.py:166-168 -> GET /health
- OpenAPI generado localmente desde app.main sin levantar red externa:
  total paths: 145
- Primeros 10 endpoints detectados:
  /api/v1/brands/
  /api/v1/brands/{brand_id}/models
  /api/v1/instruments/{instrument_id}
  /api/v1/instruments/{instrument_id}/image
  /api/v1/auth/register
  /api/v1/auth/login
  /api/v1/auth/verify-2fa
  /api/v1/auth/logout
  /api/v1/auth/me
  /api/v1/auth/refresh
- Nota de entorno:
  En este sandbox, curl a localhost devuelve "Operation not permitted", por lo que la comprobación HTTP directa no fue posible aquí. Se validó por import de app + esquema OpenAPI.

PHASE 3 - Conexiones corregidas en esta auditoría

- Router principal unificado y sin desalineación JS/TS:
  src/router/index.ts:1 reexporta src/router/index.js
- 404 real agregada y conectada:
  src/router/index.js:45, src/router/index.js:293-296
  src/vue/content/pages/NotFoundPage.vue:1-24
- Flujo JWT frontend ya conectado (no se reescribió):
  src/composables/useAuth.js:64-97, 147-169, 175-183
  src/stores/auth.js:29-35
  src/router/index.js:307-335
- CRUD de inventario ya operativo desde UI + Pinia + Axios:
  src/vue/content/pages/admin/InventoryPage.vue:46-124
  src/stores/inventory.js:12-55
  src/services/api.js:5-15

PHASE 4 - SASS a tokens CSS

- Fuente leída:
  src/scss/_variables.scss:1-97
- Tokens creados con valores existentes:
  src/assets/styles/tokens.css:1-51
- Import único en arranque:
  src/main.js:2

PHASE 5 - Verificación de ejecución

- npm run build: OK (sin errores de compilación)
- npm run test -- --run: OK
  3 archivos de test, 8 tests en verde
- Resultado de tests actuales:
  tests/unit/components/InventoryCard.spec.js
  tests/unit/components/InventoryForm.spec.js
  tests/unit/stores/inventory.spec.js

Plan priorizado de finalización (3 semanas, orientado a evaluación PF1161)

Prioridad 1 (alta visibilidad evaluador) - 3 a 5 días
- Completar cobertura de tests de componentes críticos del demo:
  LoginForm, RegisterForm, RepairsPage, DashboardPage, InventoryPage, RepairDetailPage, AdminDashboard, SignaturePage, SchedulePage, NotFoundPage.
- Objetivo verificable:
  1 prueba mínima por componente crítico (mount + render + 1 interacción).
- Motivo:
  Es la brecha principal contra "al menos un test por componente".

Prioridad 2 (alta visibilidad evaluador) - 2 a 3 días
- Consolidar evidencia funcional de CRUD completo en demo guiado:
  alta, listado, edición y eliminación de inventario desde UI admin.
- Dejar guion de demo con rutas y acciones exactas.
- Motivo:
  Facilita evaluación de requisito fullstack en revisión en vivo.

Prioridad 3 (media/alta) - 2 a 4 días
- Reducir PARTIAL y LEGACY WRAPPER en componentes de navegación/layout:
  src/vue/components/layout/PageWrapper.vue
  src/vue/components/nav/navbar-wrappers/InPageNavbar.vue
  src/vue/components/nav/navbar-wrappers/RouteNavbar.vue
- Objetivo:
  eliminar wrappers legado o dejarlos estrictamente como adaptadores documentados.

Prioridad 4 (media) - 2 a 3 días
- Eliminar consumos Axios hardcodeados fuera de API_URL central:
  src/vue/components/ai/QuoteGenerator.vue:53
- Objetivo:
  usar src/services/api.js para todas las llamadas backend.

Prioridad 5 (media) - 1 a 2 días
- Afinar calidad de entrega:
  revisar warning de chunk grande en build y dividir carga crítica de páginas pesadas.
- Evidencia actual:
  warning en npm run build (bundle principal > 500 kB).

PHASE 6 - Checklist final para evaluador PF1161

MODULO 6 COMPLIANCE:
[x] Vue SFC (template+script+style) — ejemplos: src/vue/components/auth/LoginForm.vue, src/vue/components/admin/InventoryForm.vue, src/vue/content/pages/RepairsPage.vue, src/vue/content/pages/NotFoundPage.vue
[x] v-if, v-show, v-for, v-bind, v-model, v-on — v-if: src/vue/content/pages/admin/InventoryPage.vue:14; v-show: src/vue/components/generic/ImageView.vue:4; v-for: src/vue/components/admin/InventoryTable.vue:14; v-bind: src/vue/components/auth/LoginForm.vue:13; v-model: src/vue/components/auth/LoginForm.vue:8; v-on: src/vue/components/auth/LoginForm.vue:3
[x] Vue Router with dynamic routes — src/router/index.js:133, src/router/index.js:177, src/router/index.js:223
[x] 404 route — src/router/index.js:293, src/vue/content/pages/NotFoundPage.vue

MODULO 7 COMPLIANCE:
[x] Props and emit — src/vue/components/admin/InventoryForm.vue:61, src/vue/components/admin/InventoryForm.vue:68; src/vue/components/dashboard/RepairCard.vue:23, src/vue/components/dashboard/RepairCard.vue:27
[x] onMounted — src/vue/content/pages/admin/InventoryPage.vue:168, src/vue/content/pages/RepairsPage.vue:158
[x] Class binding — src/vue/content/pages/RepairsPage.vue:43
[x] Axios to FastAPI — src/services/api.js:1-7, uso en src/vue/content/pages/RepairsPage.vue:149 y src/stores/inventory.js:20
[x] Pinia store — src/main.js:5, src/main.js:15, src/stores/auth.js:14, src/stores/inventory.js:4
[ ] Unit tests por componente — hoy solo cobertura parcial en tests/unit/components/InventoryCard.spec.js, tests/unit/components/InventoryForm.spec.js, tests/unit/stores/inventory.spec.js

FULLSTACK COMPLIANCE:
[x] Frontend → Backend communication working — vía src/services/api.js y llamadas en páginas/store (ej: src/vue/content/pages/RepairsPage.vue:149, src/stores/inventory.js:20)
[x] JWT login flow working — src/composables/useAuth.js:69-90, src/services/api.js:10-13, guard en src/router/index.js:311-318
[x] Complete CRUD in UI — módulo Inventario (admin) con create/read/update/delete
[x] Real problem solved — gestión de taller de reparación de sintetizadores (módulos clientes, reparaciones, inventario, firmas)

REMAINING MANUAL STEPS (solo lo no automatizable seguro)

1) Ejecutar validación HTTP directa backend fuera del sandbox (curl /health, /docs) en máquina local sin restricción de socket.
   Tiempo estimado: 20-30 min
   Prioridad: Alta (evidencia de ejecución para evaluador)

2) Acordar con docente/evaluador alcance exacto de "1 test por componente" (todos los componentes vs componentes críticos de evaluación).
   Tiempo estimado: 15-30 min
   Prioridad: Alta (define esfuerzo final de testing)

3) Ejecutar demo end-to-end grabada (login, CRUD inventario, consulta estado reparación, ruta 404) con dataset final.
   Tiempo estimado: 2-4 h
   Prioridad: Alta (visibilidad evaluador)
