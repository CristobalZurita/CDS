# CDS Vue 3 Zero

Proyecto Vue 3 autónomo en construcción dentro de `CDS_VUE3_ZERO/`, con paridad funcional respecto al CDS actual.

## 1) Contexto operativo (obligatorio)
- Repo válido: `cirujano-front_CLEAN`
- Rama válida: `CDS_ZERO`
- Carpeta de trabajo: `CDS_VUE3_ZERO/`
- Enfoque: aditivo/deconstructivo, sin inventar rutas, contratos, endpoints, variables ni nombres.
- No commit sin autorización explícita.

## 2) Estado real verificado (hoy)
1. Desacople de alias legacy en Vite:
   - `vite.config.js` usa solo alias locales (`@new`, `@`, `/src/`), sin `@legacy`.
2. Wiring local implementado para auth/API:
   - `src/services/api.js` ahora implementa cliente Axios + helpers de sesión + endpoints auth.
   - `src/stores/auth.js` ahora implementa store Pinia real (login/register/2FA/reset/logout/checkAuth).
   - `src/composables/useAuth.js` usa el store local (sin puente legacy).
3. Layout base local:
   - `src/layouts/MasterLayout.vue` migrado a implementación Vue real (header/nav/footer + `router-view`), sin `@legacy`.
4. Fase Auth cerrada en Vue real:
   - páginas auth + formularios auth + `TurnstileWidget` local.
5. Fase Public cerrada en Vue real:
   - páginas public migradas: `Home`, `Terms`, `Privacy`, `License`, `Policy`, `Calculators`, `Schedule`, `CotizadorIA`, `Store`.
   - composables públicos locales activos.
6. Fase Client cerrada en Vue real:
   - páginas client migradas: `Dashboard`, `Repairs`, `RepairDetail`, `Profile`, `OtPayments`.
   - composables client locales activos (`useDashboardPage`, `useRepairsPage`, `useRepairDetailPage`, `useProfilePage`, `useOtPaymentsPage`).
   - util local de estados de reparación creado: `src/utils/repairStatus.js`.
7. Fase Admin iniciada en Vue real (8/17):
   - páginas admin migradas: `AdminDashboard`, `Stats`, `Categories`, `NewsletterSubscriptions`, `ContactMessages`, `Appointments`.
   - páginas admin adicionales migradas: `Inventory`, `InventoryUnified`.
   - composables admin locales activos para esas páginas.

## 3) Pendiente (orden de ejecución)
1. **Admin** (9 páginas pendientes): `Clients`, `RepairsAdmin`, `QuotesAdmin`, `RepairDetailAdmin`, `Tickets`, `PurchaseRequests`, `Manuals`, `Wizards`, `Archive`.
2. **Calculadoras** (9 páginas): reemplazar wrappers manteniendo lógica matemática.
3. **Token** (2 páginas): `Signature`, `PhotoUpload`.
4. **QA paridad completa**: rutas, guards, navegación, formularios y contratos API.

## 4) Checks ejecutados y resultado
1. `npm install` en `CDS_VUE3_ZERO`: OK.
2. `npm run build` en `CDS_VUE3_ZERO`: **FALLA** por wrappers legacy activos.
   - error actual: `@legacy/modules/timer555/Timer555View.vue`
   - archivo que bloquea build: `src/pages/calculators/Timer555Page.vue`
3. Conteo actual de referencias `@legacy`:
   - `rg -n "@legacy" src | wc -l` → `24`
4. Conteo actual de wrappers `LegacyView` en páginas:
   - `rg -n "<LegacyView" src/pages | wc -l` → `20`
5. `npm run lint`:
   - no existe script `lint` en `package.json` actual (solo `dev`, `build`, `preview`).

## 5) Riesgos abiertos
1. Build no cerrará mientras existan imports `@legacy` en módulos pendientes.
2. Validación runtime de auth/store requiere backend real y variables de entorno válidas.
3. Si se migra fuera de fase, aumenta riesgo de romper paridad de rutas y contratos.

## 6) Evidencia (archivo:línea)
1. Alias local sin `@legacy`:
   - `vite.config.js:11`
   - `vite.config.js:12`
2. API local real:
   - `src/services/api.js:7`
   - `src/services/api.js:105`
3. Store auth local real:
   - `src/stores/auth.js:34`
   - `src/stores/auth.js:72`
4. Composable auth local:
   - `src/composables/useAuth.js:4`
   - `src/composables/useAuth.js:21`
5. Layout local:
   - `src/layouts/MasterLayout.vue:1`
   - `src/layouts/MasterLayout.vue:63`
6. Public migrado:
   - `src/pages/public/HomePage.vue:1`
   - `src/pages/public/SchedulePage.vue:1`
   - `src/pages/public/StorePage.vue:1`
   - `src/composables/useHomePage.js:3`
   - `src/composables/useSchedulePage.js:15`
   - `src/composables/useStorePage.js:15`
7. Client migrado:
   - `src/pages/client/DashboardPage.vue:1`
   - `src/pages/client/RepairsPage.vue:1`
   - `src/pages/client/RepairDetailPage.vue:1`
   - `src/pages/client/ProfilePage.vue:1`
   - `src/pages/client/OtPaymentsPage.vue:1`
   - `src/composables/useDashboardPage.js:1`
   - `src/composables/useRepairsPage.js:1`
   - `src/composables/useRepairDetailPage.js:1`
   - `src/composables/useProfilePage.js:1`
   - `src/composables/useOtPaymentsPage.js:1`
   - `src/utils/repairStatus.js:1`
8. Admin (bloque inicial) migrado:
   - `src/pages/admin/AdminDashboard.vue:1`
   - `src/pages/admin/StatsPage.vue:1`
   - `src/pages/admin/CategoriesPage.vue:1`
   - `src/pages/admin/NewsletterSubscriptionsPage.vue:1`
   - `src/pages/admin/ContactMessagesPage.vue:1`
   - `src/pages/admin/AppointmentsPage.vue:1`
   - `src/composables/useAdminDashboardPage.js:1`
   - `src/composables/useStatsPage.js:1`
   - `src/composables/useCategoriesPage.js:1`
   - `src/composables/useNewsletterSubscriptionsPage.js:1`
   - `src/composables/useContactMessagesPage.js:1`
   - `src/composables/useAppointmentsPage.js:1`
9. Admin (inventario) migrado:
   - `src/pages/admin/InventoryPage.vue:1`
   - `src/pages/admin/InventoryUnifiedPage.vue:1`
   - `src/composables/useInventoryPage.js:1`
   - `src/composables/useInventoryUnifiedPage.js:1`

## 7) Nota de control
- Este README refleja solo estado real de `CDS_VUE3_ZERO/`.
- Este ciclo no modifica ni depende de `LISTA_DE_TAREAS.md`.
