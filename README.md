# Cirujano de Sintetizadores

Plataforma web para operación de taller, seguimiento de reparaciones, inventario técnico y catálogo público de repuestos.

El sistema hoy está compuesto por una sola base operativa y tres superficies principales:
- portal público
- portal cliente
- portal administrador

## Estado actual

La base del proyecto ya está integrada de extremo a extremo en estas capas:
- `frontend SPA` con Vue 3, Vite, Pinia y Vue Router
- `backend API` con FastAPI y SQLAlchemy
- `base de datos` SQLite local por defecto en [backend/cirujano.db](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/backend/cirujano.db)
- `testing` con Vitest para front y Playwright para E2E

Capas funcionales activas:
- `público`: landing, contacto, agenda, calculadoras, cotizador/diagnóstico, tienda
- `cliente`: dashboard, reparaciones, perfil, pagos OT, documentos
- `admin`: clientes, usuarios, reparaciones, inventario, categorías, citas, tickets, compras, manuales, estadísticas

## Arquitectura resumida

### Frontend
- Vue 3
- Vite
- Pinia
- Vue Router
- Sass centralizado en [src/scss](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/scss)

### Backend
- FastAPI
- SQLAlchemy
- SQLite por defecto

### Testing
- Vitest
- Playwright
- pytest para backend

## Flujos importantes del sistema

### Inventario y tienda

El inventario y la tienda comparten la misma fuente de verdad.

Regla operativa:
- un solo `product`
- un solo stock real
- mismo ítem para taller y tienda
- separación por uso, no por duplicación

La tienda pública lee desde el backend de inventario:
- [backend/app/routers/inventory.py](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/backend/app/routers/inventory.py)
- [src/vue/content/pages/StorePage.vue](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/vue/content/pages/StorePage.vue)

El dashboard admin opera el inventario desde:
- [src/vue/content/pages/admin/InventoryPage.vue](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/vue/content/pages/admin/InventoryPage.vue)
- [src/vue/components/admin/InventoryForm.vue](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/vue/components/admin/InventoryForm.vue)
- [src/vue/components/admin/InventoryStockSheet.vue](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/vue/components/admin/InventoryStockSheet.vue)
- [src/vue/components/admin/InventoryStockStates.vue](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/vue/components/admin/InventoryStockStates.vue)

### Sincronización de imágenes de inventario

Flujo vigente:
1. dejar imágenes en [public/images/INVENTARIO](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/public/images/INVENTARIO)
2. usar `Sincronizar tienda` desde `/admin/inventory`
3. el backend actualiza `products.image_url`, publicación y catálogo

Script reutilizado por ese flujo:
- [scripts/sync_store_catalog_from_inventory_images.py](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/scripts/sync_store_catalog_from_inventory_images.py)

Ese flujo es aditivo:
- no borra productos por defecto
- no borra imágenes fuente
- reutiliza filas existentes cuando encuentra match por nombre/SKU
- crea filas sólo cuando no existe producto razonable

### OT y taller

Las OTs y reparaciones viven separadas del catálogo de venta, pero conectadas al mismo ecosistema:
- `cliente + equipo`
- `OT / reparación`
- `consumo de materiales`
- `stock interno`

Referencias:
- [backend/app/models/repair.py](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/backend/app/models/repair.py)
- [backend/app/routers/repair.py](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/backend/app/routers/repair.py)
- [src/vue/components/admin/repair/RepairComponentsManager.vue](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/vue/components/admin/repair/RepairComponentsManager.vue)

### Cotizador inteligente

El cotizador está orientado a diagnóstico referencial, no a precio final real.

Base actual:
- flujo guiado
- ramas bloqueantes
- observaciones libres del cliente
- resultado referencial, no vinculante

Referencias:
- [src/vue/content/pages/CotizadorIAPage.vue](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/vue/content/pages/CotizadorIAPage.vue)
- [src/vue/components/quotation/InteractiveInstrumentDiagnostic.vue](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/vue/components/quotation/InteractiveInstrumentDiagnostic.vue)
- [backend/app/routers/quotation.py](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/backend/app/routers/quotation.py)

## Estructura relevante

- Frontend: [src](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src)
- Backend: [backend/app](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/backend/app)
- Tests frontend: [tests](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/tests)
- Tests backend: [backend/tests](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/backend/tests)
- Documentación activa: [docs](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/docs)
- Documentación adicional/archivo: [DOCUMJENTOS_EXTRAS](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/DOCUMJENTOS_EXTRAS)

## Ejecución local

### Frontend
```bash
npm install
npm run dev
```

### Backend
```bash
cd backend
uvicorn app.main:app --reload
```

Puertos habituales:
- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`

## Variables importantes

### Frontend
```bash
VITE_API_URL=http://localhost:8000/api/v1
```

### Backend
Por defecto:
- `ENVIRONMENT=development`
- `DATABASE_URL=sqlite:///./cirujano.db`

La configuración efectiva sale de:
- [backend/.env](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/backend/.env)
- [backend/app/core/config.py](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/backend/app/core/config.py)

## Scripts útiles

### Desarrollo
```bash
npm run dev
npm run build
```

### Testing
```bash
npm run test
npm run test:coverage
npm run test:e2e
backend/.venv/bin/python -m pytest backend/tests -q
```

### Sincronización de instrumentos/catálogo técnico
```bash
npm run sync:instruments
npm run sync:instruments:force
npm run sync:instruments:once
```

## Validación reciente

Verificado en esta etapa:
- `npx vitest run tests/unit/admin/InventoryStockSheet.test.ts tests/unit/admin/InventoryPage.test.ts` -> OK
- `npm run build` -> OK
- `npm run test:e2e -- tests/e2e/store.spec.ts tests/e2e/routes.spec.ts` -> OK
- `backend/.venv/bin/python -m pytest backend/tests/test_inventory_store_catalog_sync.py -q` -> OK

Estado local del catálogo de tienda sobre la DB operativa al momento de esta actualización:
- `101` archivos detectados en `public/images/INVENTARIO`
- `111` productos vinculados y publicados
- `111` con stock bruto
- `111` vendibles ahora
- `0` pendientes
- `0` huérfanos

## Sass

La capa visual del runtime útil está centralizada en Sass y no en estilos embebidos de componentes.

Referencias:
- [src/scss](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/scss)
- [src/scss/README.md](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/scss/README.md)

## Documentación recomendada

- [docs/ARCHITECTURE.md](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/docs/ARCHITECTURE.md)
- [docs/DEPLOYMENT.md](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/docs/DEPLOYMENT.md)
- [docs/TESTING.md](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/docs/TESTING.md)
- [docs/TESTING_COVERAGE_MATRIX.md](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/docs/TESTING_COVERAGE_MATRIX.md)
- [docs/MODELOS_INVENTORY.md](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/docs/MODELOS_INVENTORY.md)
- [docs/KICAD_CATALOG_WORKFLOW.md](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/docs/KICAD_CATALOG_WORKFLOW.md)

## Criterio de trabajo del repo

Regla práctica vigente sobre este proyecto:
- trabajar sobre la estructura existente
- preferir mejora aditiva
- deconstruir antes de duplicar
- reutilizar archivos, stores, rutas, modelos y flujos ya presentes
- no inventar capas paralelas si el sistema actual ya tiene dónde integrarse

## Uso interno

Proyecto de uso interno. Revisar datos, secretos y documentación antes de publicar o redistribuir.
