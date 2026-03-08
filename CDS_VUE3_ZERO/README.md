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
5. Calculadoras: **9/9** paginas en Vue real.
6. Token: **2/2** paginas en Vue real.

## 3) Cierre de desacople legacy
1. Wrappers `LegacyView` en `src/pages`: **0**.
2. Imports `@legacy` en `src`: **0**.
3. Alias activo de trabajo: `@new` y `@` apuntando a `src` local.

## 4) Trabajo aplicado en este ciclo (UI Home + Navbar)
1. Se elimino la segunda barra de navegacion en Home (`Navegacion rapida`).
2. Se rehizo la Home con estructura visual cercana al sitio viejo, pero con Vue + CSS local (sin SASS masivo).
3. Se dejaron solo acciones funcionales reales (rutas existentes y enlaces externos reales).
4. Se ajusto spec E2E de navegacion para reflejar rutas/redirecciones actuales.
5. Se rehizo `MasterLayout` para navbar mas cercano al viejo: logo real, menu completo y menu movil plegable.
6. Se agregaron assets reales de logo en `public/images/logo` dentro de `CDS_VUE3_ZERO`.
7. En landing (`/`) la navegacion de secciones ahora vive en el navbar principal (sin segundo bloque de navegacion en el cuerpo).

## 5) Evidencia de cambios (archivo:linea)
1. Home reconstruida:
   - `src/pages/public/HomePage.vue:1`
2. Datos/acciones de Home actualizados:
   - `src/composables/useHomePage.js:1`
3. Spec E2E ajustado al comportamiento actual:
   - `tests/e2e/navigation.spec.js:1`
4. Navbar reconstruido:
   - `src/layouts/MasterLayout.vue:1`
5. Logos incorporados:
   - `public/images/logo/logo_square_002.webp`
   - `public/images/logo/NUEVO_cirujano.webp`
   - `public/images/logo/logo_square_004.webp`
   - `public/images/logo/Logo Nuevo.webp`

## 6) Checks ejecutados en este ciclo
1. `npm run build`: **OK**.
2. Playwright E2E: **NO ejecutable en este entorno** por crash de Chromium (`sandbox_host_linux.cc:41`, `Operation not permitted`).

## 7) Riesgos reales abiertos
1. Aunque la Home ya no tiene doble navbar, queda revisar visual fino del resto de paginas publicas para mantener paridad estetica completa.
2. La auditoria E2E automatica depende de resolver ejecucion de Chromium en este entorno.

## 8) Nota de control
- README actualizado con estado real aplicado en codigo.
- No se hicieron commits en este ciclo.
