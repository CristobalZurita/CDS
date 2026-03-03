# Matriz de Autoridad

## Objetivo

Esta matriz identifica, por modulo, que pieza gobierna realmente el comportamiento del sistema.

No reemplaza modulos existentes.
Sirve para:

- saber donde intervenir
- saber que archivos son compatibilidad
- evitar duplicaciones nuevas
- encauzar piezas flotantes sin romper contratos activos

## Frontend

| Modulo | Router / entrada | Autoridad de estado | Autoridad de consumo | Compatibilidad o ruido |
| --- | --- | --- | --- | --- |
| Auth | `src/router/index.ts` | `src/stores/auth.js` y `src/stores/auth.ts` | `src/composables/useAuth.ts` | `src/services/auth.ts` |
| Inventory | `src/vue/content/pages/admin/InventoryPage.vue` | `src/stores/inventory.js` y `src/stores/inventory.ts` | `src/composables/useInventory.js` y `src/composables/useInventory.ts` | `src/views/InventoryUnified.vue` como superficie secundaria |
| Categories | `src/vue/content/pages/admin/CategoriesPage.vue` | `src/stores/categories.js` y `src/stores/categories.ts` | `src/composables/useCategories.js` y `src/composables/useCategories.ts` | sin conflicto fuerte actual |
| Diagnostics | `src/vue/content/pages/admin/QuotesAdminPage.vue` | `src/stores/diagnostics.js` y `src/stores/diagnostics.ts` | `src/composables/useDiagnostics.js` y `src/composables/useDiagnostics.ts` | sin conflicto fuerte actual |
| Instruments | `src/vue/components/admin/InstrumentList.vue` | `src/stores/instruments.js` y `src/stores/instruments.ts` | `src/composables/useInstruments.js` | TS y JS coexisten |
| Repairs | `src/vue/content/pages/admin/RepairsAdminPage.vue`, `src/vue/content/pages/RepairsPage.vue`, `src/vue/content/pages/RepairDetailPage.vue` | `src/stores/repairs.js` y `src/stores/repairs.ts` | `src/composables/useRepairs.js` y `src/composables/useRepairs.ts` | admin y portal cliente ya usan la misma autoridad para lista y detalle cliente |
| Router global | `src/router/index.ts` | no aplica | `src/main.js` | sin bypass relevante |
| HTTP cliente | no aplica | no aplica | `src/services/api.ts` | `src/services/api.js` es compatibilidad |

## Backend

| Modulo | Router autoridad | Capa de apoyo | Modelo / schema | Compatibilidad o ruido |
| --- | --- | --- | --- | --- |
| Client portal | `backend/app/routers/client.py` | helpers internos del mismo router | `backend/app/models/repair.py`, `backend/app/models/client.py` | payloads cliente especificos del portal |
| Repairs | `backend/app/routers/repair.py` | `backend/app/services/repair_read_service.py`, `backend/app/services/repair_write_service.py` | `backend/app/models/repair.py`, `backend/app/schemas/repair.py` | router rico y activo |
| Inventory | `backend/app/routers/inventory.py` | servicios y scripts de sync | `backend/app/models/inventory.py`, `backend/app/models/stock.py` | flujo tienda conectado |
| Auth | `backend/app/api/v1/endpoints/auth.py` | `backend/app/core/security.py` | `backend/app/models/user.py` | convive con capas historicas |
| Category | `backend/app/routers/category.py` | capa router directa | `backend/app/schemas/category.py`, `backend/app/models/category.py` | borde ya tipado |
| Device | `backend/app/routers/device.py` | capa router directa | `backend/app/schemas/device.py`, `backend/app/models/device.py` | borde ya tipado |
| Instrument | `backend/app/routers/instrument.py` | capa router directa | `backend/app/schemas/instrument.py`, `backend/app/models/instrument.py` | borde ya tipado |
| Repair status | `backend/app/routers/repair_status.py` | capa router directa | `backend/app/schemas/repair_status.py`, `backend/app/models/repair.py` | borde ya tipado |

## Reglas de uso

Cuando se trabaje un modulo:

1. tocar primero la autoridad
2. dejar wrappers de compatibilidad si todavia hay consumidores activos
3. no eliminar ruido sin confirmar que es inerte
4. validar antes de pasar al siguiente modulo
