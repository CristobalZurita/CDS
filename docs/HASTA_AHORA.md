# Hasta Ahora

## Uso

Este archivo es el checkpoint corto para retomar el trabajo sin depender del chat.

Antes de continuar, leer en este orden:

1. `docs/HASTA_AHORA.md`
2. `docs/AUDITORIA_VIVA.md`
3. `docs/MATRIZ_AUTORIDAD.md`
4. `docs/AUDIT.md`

## Regla vigente

Trabajar siempre:

- aditivo
- no destructivo
- no sustractivo
- deconstructivo

Aplicacion directa:

- si existe, se usa
- si existe parcial, se completa
- si duplica, primero se clasifica
- no inventar variables, rutas, modelos ni funciones fuera de la estructura real

## Base ya encauzada

### Documentacion viva

Quedo creada y actualizada:

- `docs/AUDITORIA_VIVA.md`
- `docs/MATRIZ_AUTORIDAD.md`
- `docs/AUDIT.md`

### Frontend ya normalizado

#### Capa HTTP y auth

- `src/services/api.ts` es la autoridad HTTP
- `src/services/api.js` queda como compatibilidad
- `src/composables/useAuth.ts` ya esta alineado con `/auth/*`
- `src/services/auth.ts` queda como fachada compatible

#### Router y wizards

- `src/router/index.ts` ya incluye `admin/wizards`
- `src/vue/components/admin/layout/AdminSidebar.vue` ya expone acceso
- `src/vue/content/pages/admin/WizardsPage.vue` ya esta conectado

#### Pinia normalizado

Se estandarizo la superficie publica de stores/composables activos:

- alias `loading` / `isLoading`
- `setError`
- refs consistentes en composables store-backed

#### Inventory encauzado en store

Autoridad actual:

- `src/stores/inventory.js`
- `src/stores/inventory.ts`
- `src/composables/useInventory.js`
- `src/composables/useInventory.ts`

Las vistas ya no resuelven por su cuenta:

- `src/vue/content/pages/admin/InventoryPage.vue`
- `src/views/InventoryUnified.vue`

#### Repairs cliente encauzado en store

Autoridad actual:

- `src/stores/repairs.js`
- `src/stores/repairs.ts`
- `src/composables/useRepairs.js`
- `src/composables/useRepairs.ts`

Las vistas cliente ya no hacen carga directa de lista, detalle ni PDF:

- `src/vue/content/pages/RepairsPage.vue`
- `src/vue/content/pages/RepairDetailPage.vue`

### Backend ya tipado en borde

Routers ya encauzados con schemas:

- `backend/app/routers/category.py`
- `backend/app/routers/device.py`
- `backend/app/routers/instrument.py`
- `backend/app/routers/repair_status.py`

Schemas de apoyo:

- `backend/app/schemas/category.py`
- `backend/app/schemas/device.py`
- `backend/app/schemas/instrument.py`
- `backend/app/schemas/repair_status.py`

## Validacion ya ejecutada

### Inventory

- `npx vitest run tests/stores/inventory.store.test.ts tests/composables/useComposables.test.ts tests/unit/admin/InventoryPage.test.ts --environment jsdom`
- `npx vite build`

### Repairs cliente

- `npx vitest run tests/stores/repairs.store.test.ts tests/composables/useComposables.test.ts tests/unit/client/RepairsPage.test.ts tests/unit/client/RepairDetailPage.test.ts --environment jsdom`
- `npx vite build`

## Siguiente corte logico

Siguiente modulo a trabajar:

1. `quotation`
2. `schedule`

Metodo para retomarlo:

1. leer router
2. leer vista
3. leer componentes usados
4. leer composable
5. leer store
6. leer `src/services/*`
7. leer router backend que consume
8. solo entonces decidir si hay bypass directo, pieza flotante o contrato duplicado

## Criterio al retomar

No abrir varios frentes a la vez.

Tomar un solo modulo y cerrarlo asi:

1. identificar autoridad real
2. mover bypass de vista al store/composable si ya existe esa capa
3. dejar compatibilidad si hay consumidores activos
4. validar con tests o build
5. registrar el cambio en `docs/AUDITORIA_VIVA.md`

## Nota corta

Si al retomar aparece una pieza duplicada, no borrarla por reflejo.
Primero clasificarla segun `docs/AUDITORIA_VIVA.md`:

- `AUTORIDAD`
- `COMPATIBILIDAD`
- `DUPLICADO_UTIL`
- `DUPLICADO_RUIDOSO`
- `FLOTANTE`
- `LEGACY_INERTE`
- `PARCIAL`
