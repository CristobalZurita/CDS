# CDS Vue 3 Zero

Proyecto Vue 3 autonomo en `CDS_VUE3_ZERO/`, con migracion deconstructiva y aditiva desde el CDS actual.

## 1) Contexto operativo (obligatorio)
- Repo: `cirujano-front_CLEAN`
- Rama: `CDS_ZERO`
- Carpeta de trabajo: `CDS_VUE3_ZERO/`
- Regla: no inventar rutas/contratos/endpoints/variables.
- Regla: no commit sin autorizacion explicita.

## 2) Estado real actualizado
1. Auth: **6/6** paginas en Vue real.
2. Public: **9/9** paginas en Vue real.
3. Client: **5/5** paginas en Vue real.
4. Admin: **17/17** paginas en Vue real.
   - Migradas en este ciclo (9 pendientes cerradas):
     - `ClientsPage`, `RepairsAdminPage`, `QuotesAdminPage`, `RepairDetailAdminPage`, `TicketsPage`, `PurchaseRequestsPage`, `ManualsPage`, `WizardsPage`, `ArchivePage`.
   - Composables nuevos asociados (9):
     - `useClientsPage`, `useRepairsAdminPage`, `useQuotesAdminPage`, `useRepairDetailAdminPage`, `useTicketsPage`, `usePurchaseRequestsPage`, `useManualsPage`, `useWizardsPage`, `useArchivePage`.

## 3) Pendiente (orden)
1. Calculadoras: **9/9** wrappers legacy.
2. Token: **2/2** wrappers legacy.
3. Desacople final de referencias legacy compartidas:
   - `src/layouts/AdminLayout.vue`
   - `src/components/business/index.js`

## 4) Checks ejecutados (este ciclo)
1. `npm install` en `CDS_VUE3_ZERO`: **OK**.
2. `npm run build` en `CDS_VUE3_ZERO`: **OK** (build completo generado en `dist/`).
3. Conteo wrappers en paginas:
   - `rg -n "<LegacyView" CDS_VUE3_ZERO/src/pages | wc -l` -> **11**.
4. Conteo imports `@legacy` en `src`:
   - `rg -n "@legacy" CDS_VUE3_ZERO/src | wc -l` -> **15**.

## 5) Evidencia de cambios (archivo:linea)
1. Paginas admin migradas:
   - `src/pages/admin/ClientsPage.vue:1`
   - `src/pages/admin/RepairsAdminPage.vue:1`
   - `src/pages/admin/QuotesAdminPage.vue:1`
   - `src/pages/admin/RepairDetailAdminPage.vue:1`
   - `src/pages/admin/TicketsPage.vue:1`
   - `src/pages/admin/PurchaseRequestsPage.vue:1`
   - `src/pages/admin/ManualsPage.vue:1`
   - `src/pages/admin/WizardsPage.vue:1`
   - `src/pages/admin/ArchivePage.vue:1`
2. Composables admin creados:
   - `src/composables/useClientsPage.js:1`
   - `src/composables/useRepairsAdminPage.js:1`
   - `src/composables/useQuotesAdminPage.js:1`
   - `src/composables/useRepairDetailAdminPage.js:1`
   - `src/composables/useTicketsPage.js:1`
   - `src/composables/usePurchaseRequestsPage.js:1`
   - `src/composables/useManualsPage.js:1`
   - `src/composables/useWizardsPage.js:1`
   - `src/composables/useArchivePage.js:1`

## 6) Riesgos reales abiertos
1. Aun quedan 11 paginas con `LegacyView` (Calculadoras + Token).
2. Aun quedan imports `@legacy` en layout/admin y exports de componentes business.
3. `vite.config.js` sigue manteniendo alias legacy para soportar los modulos no migrados.

## 7) Nota de control
- Este README documenta estado real de codigo aplicado en `CDS_VUE3_ZERO/`.
- No se hicieron commits en este ciclo.
