# Auditoria Viva CDS

## Proposito

Este documento convierte la auditoria inicial del proyecto en una auditoria viva y acumulativa.

No reemplaza la auditoria anterior.
La usa como linea base y cambia la forma de trabajo:

- no rehacer todo desde cero
- no repetir lecturas ya verificadas sin motivo
- no mezclar documentacion con codigo activo
- intervenir por delta real sobre una base conocida

## Regla de trabajo

Este repo se trabaja con criterio:

- aditivo
- no destructivo
- no sustractivo
- deconstructivo

Aplicacion practica:

- si existe una pieza activa, se reutiliza
- si existe una pieza parcial, se completa
- si existe una pieza duplicada, se clasifica antes de tocarla
- si no existe una pieza necesaria, se crea encima de la estructura actual

## Jerarquia de evidencia

Para auditar y decidir cambios, la autoridad baja en este orden:

1. codigo activo
2. configuracion activa
3. tests activos
4. documentacion tecnica
5. archivos historicos, wrappers, legacy y reportes viejos

La documentacion orienta.
El codigo activo manda.

## Taxonomia de lectura

Cada archivo o modulo debe quedar clasificado en una de estas categorias:

| Categoria | Significado operativo |
| --- | --- |
| `AUTORIDAD` | Pieza que gobierna realmente un flujo o modulo |
| `COMPATIBILIDAD` | Pieza mantenida para no romper consumidores previos |
| `DUPLICADO_UTIL` | Duplica, pero todavia resuelve compatibilidad real |
| `DUPLICADO_RUIDOSO` | Duplica y agrega ambiguedad o mantenimiento innecesario |
| `FLOTANTE` | Existe y funciona en parte, pero no esta bien encauzado |
| `LEGACY_INERTE` | Existe, pero no participa de la ruta activa del sistema |
| `PARCIAL` | Cubre solo una parte del flujo y requiere cierre aditivo |

## Metodo de re-auditoria

La re-auditoria ya no se hace por carpeta completa si no cambio nada.

Se hace por estas fases:

1. fijar una linea base real
2. identificar la autoridad actual del modulo
3. detectar bypass, ruido, duplicados y piezas flotantes
4. intervenir solo el borde necesario
5. validar con test, build o import de modulo
6. registrar el cambio en este documento

## Como leer un modulo

### Frontend

Orden de lectura:

1. `src/router/*`
2. vista en `src/vue/content/pages/*` o `src/views/*`
3. componentes usados por esa vista
4. composable
5. store
6. `src/services/*`
7. endpoint backend consumido

### Backend

Orden de lectura:

1. router
2. schema
3. servicio o capa de escritura/lectura
4. modelo
5. migracion o patch de esquema si aplica
6. consumidor frontend si existe

## Linea base operativa actual

Esta auditoria viva parte desde una base ya leida y verificada en el repo:

- arquitectura general del frontend y backend
- routers de Vue y FastAPI
- stores y composables activos
- routers backend de auth, inventory, repair, signature, quotation y cliente
- vistas principales de admin y cliente
- tests unitarios y de stores para los modulos intervenidos

## Hallazgos de autoridad ya verificados

### Frontend

| Modulo | Autoridad | Compatibilidad / ruido observado |
| --- | --- | --- |
| HTTP frontend | `src/services/api.ts` | `src/services/api.js` queda como compatibilidad |
| Auth frontend | `src/composables/useAuth.ts` + `src/stores/auth.js` / `src/stores/auth.ts` | `src/services/auth.ts` queda como fachada de compatibilidad |
| Router | `src/router/index.ts` | ya enruta panel cliente, admin y `admin/wizards` |
| Inventory admin | `src/stores/inventory.js` / `src/stores/inventory.ts` | antes habia bypass directo desde vistas; ya fue encauzado |
| Categories | `src/stores/categories.js` / `src/stores/categories.ts` | normalizado con alias `loading` / `isLoading` |
| Diagnostics | `src/stores/diagnostics.js` / `src/stores/diagnostics.ts` | composables normalizados con refs reales |
| Instruments | `src/stores/instruments.js` / `src/stores/instruments.ts` | composables normalizados con refs reales |
| Repairs | `src/stores/repairs.js` / `src/stores/repairs.ts` | admin y portal cliente ya comparten la misma autoridad de estado para lista y detalle cliente |

### Backend

| Modulo | Autoridad | Compatibilidad / ruido observado |
| --- | --- | --- |
| Repairs | `backend/app/routers/repair.py` | capa rica y activa |
| Client portal | `backend/app/routers/client.py` | expone dashboard, reparaciones, detalle y PDF cliente |
| Inventory | `backend/app/routers/inventory.py` | flujo activo y conectado a frontend |
| Auth | `backend/app/api/v1/endpoints/auth.py` | convive con otras capas historicas |
| Categorias | `backend/app/routers/category.py` + `backend/app/schemas/category.py` | borde ya tipado |
| Device | `backend/app/routers/device.py` + `backend/app/schemas/device.py` | borde ya tipado |
| Instrument | `backend/app/routers/instrument.py` + `backend/app/schemas/instrument.py` | borde ya tipado |
| Repair status | `backend/app/routers/repair_status.py` + `backend/app/schemas/repair_status.py` | borde ya tipado |

## Registro de intervenciones aplicadas

### Fase 1. Capa HTTP y auth frontend

Estado: aplicado y validado.

- `src/services/api.ts` se consolido como cliente HTTP autoridad
- `src/services/api.js` quedo como wrapper de compatibilidad
- `src/composables/useApi.js` dejo de sostener un cliente propio divergente
- `src/composables/useAuth.ts` se alineo con `/auth/*`
- `src/services/auth.ts` quedo como fachada compatible sobre el flujo real

### Fase 2. Router admin y wizards

Estado: aplicado y validado.

- `src/router/index.ts` incorpora `admin/wizards`
- `src/vue/components/admin/layout/AdminSidebar.vue` expone acceso
- `src/vue/content/pages/admin/WizardsPage.vue` ya tiene feedback operativo

### Fase 3. Borde backend tipado

Estado: aplicado y validado por import/compilacion.

- `backend/app/routers/category.py`
- `backend/app/routers/device.py`
- `backend/app/routers/instrument.py`
- `backend/app/routers/repair_status.py`

Apoyo de schemas:

- `backend/app/schemas/category.py`
- `backend/app/schemas/device.py`
- `backend/app/schemas/instrument.py`
- `backend/app/schemas/repair_status.py`

### Fase 4. Normalizacion de Pinia

Estado: aplicado y validado.

Se estandarizo el contrato de stores/composables activos:

- alias `loading` / `isLoading`
- `setError`
- uso consistente de refs en composables store-backed

Archivos principales:

- `src/stores/auth.js`
- `src/stores/categories.js`
- `src/stores/diagnostics.js`
- `src/stores/instruments.js`
- `src/stores/inventory.js`
- `src/stores/quotation.js`
- `src/stores/repairs.js`
- `src/stores/stockMovements.js`
- `src/stores/users.js`

### Fase 5. Inventory como modulo Pinia completo

Estado: aplicado y validado.

El modulo de inventario ya concentra:

- lista paginada
- create/update/delete
- estado de catalogo tienda
- sincronizacion de catalogo
- importacion
- fetch puntual por item

Archivos principales:

- `src/stores/inventory.js`
- `src/stores/inventory.ts`
- `src/composables/useInventory.js`
- `src/composables/useInventory.ts`
- `src/vue/content/pages/admin/InventoryPage.vue`
- `src/views/InventoryUnified.vue`

Validacion ya ejecutada en esta fase:

- `tests/stores/inventory.store.test.ts`
- `tests/composables/useComposables.test.ts`
- `tests/unit/admin/InventoryPage.test.ts`
- `npx vite build`

### Fase 6. Repairs cliente sobre la misma autoridad de store

Estado: aplicado y validado.

El portal cliente de reparaciones ya no carga lista, detalle ni PDF de cierre directo desde la vista.

La autoridad ahora queda en:

- `src/stores/repairs.js`
- `src/stores/repairs.ts`
- `src/composables/useRepairs.js`
- `src/composables/useRepairs.ts`

Vistas encauzadas:

- `src/vue/content/pages/RepairsPage.vue`
- `src/vue/content/pages/RepairDetailPage.vue`

Validacion ejecutada:

- `tests/stores/repairs.store.test.ts`
- `tests/unit/client/RepairsPage.test.ts`
- `tests/unit/client/RepairDetailPage.test.ts`
- `tests/composables/useComposables.test.ts`
- `npx vite build`

## Registro de ruido estructural vigente

Esto no se borra por defecto. Se clasifica y se ataca por modulo.

| Ruta | Clasificacion | Nota |
| --- | --- | --- |
| `src/services/api.js` | `COMPATIBILIDAD` | wrapper sobre la autoridad TS |
| `src/services/auth.ts` | `COMPATIBILIDAD` | fachada, no fuente primaria |
| `vitest.config.js` | `DUPLICADO_RUIDOSO` | coexiste con `vitest.config.ts` |
| `.eslintrc.json` | `DUPLICADO_RUIDOSO` | coexiste con `eslint.config.cjs` |
| `database/migrations/` | `LEGACY_INERTE` | Alembic activo vive en `backend/alembic/` |
| `src/config/app.ts` | `LEGACY_INERTE` | vacio |
| `src/config/index.ts` | `LEGACY_INERTE` | vacio |
| `src/config/security.ts` | `LEGACY_INERTE` | vacio |

## Cola progresiva de trabajo

Orden sugerido desde la linea base actual:

1. `quotation` y `schedule`: confirmar si el store ya cubre el flujo real o si hay bypass directo
2. `dashboard` cliente: encauzar lo que use API directa si ya existe capa compartida
3. `tickets` y `purchase requests`: revisar si conviene store o mantener vista directa segun cobertura real

## Regla de cierre por modulo

Un modulo se considera encauzado cuando:

- la vista ya no mantiene contratos de API que el store/composable puede absorber
- la fuente de verdad esta clara
- los aliases de compatibilidad siguen disponibles si hacen falta
- hay validacion minima por test o build

## Relacion con otras docs

Documentos complementarios:

- `docs/ARCHITECTURE.md`
- `docs/AUDIT.md`
- `docs/TESTING.md`
- `docs/PRODUCTION_MIGRATIONS.md`
- `docs/SECURITY.md`
