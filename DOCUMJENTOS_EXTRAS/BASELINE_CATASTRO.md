# BASELINE CATASTRO (Estado Base)

Fecha: 2026-01-18
Alcance: Inventario base para trabajo aditivo (sin eliminar ni romper).

## Runtime actual (lo que corre hoy)
- Frontend activo (Vite): `src/`, entry `src/main.js`, rutas `src/router/index.js`.
- Backend activo (FastAPI): `backend/app/main.py`, router `backend/app/api/v1/router.py`.
- Base de datos activa: `backend/cirujano.db`.

## Frontend (estructura base)
- Paginas reales: `src/vue/content/pages/*` (18 archivos .vue).
- Componentes: `src/vue/components/*`.
- Servicios/composables: `src/services/api.js`, `src/composables/useAuth.js`.
- Rutas registradas: `src/router/index.js`.

## Backend (estructura base)
- Routers reales: `backend/app/routers/*`.
- Endpoints v1 (algunos vacios): `backend/app/api/v1/endpoints/*`.
- Modelos: `backend/app/models/*`.
- Esquemas: `backend/app/schemas/*` y `backend/app/schemas.py` (coexisten).
- Migraciones: `backend/alembic/*`, config `backend/alembic.ini`.

## Assets y builds
- Build estatico: `dist/`.
- Public assets: `public/`.

## Datos y generacion
- Seeds/SQL: `database/*` y `DE_PYTHON_NUEVO/*` (insumos, no runtime).
- MODELOS: `MODELOS/*` (proyectos de referencia, no runtime).

## Archivos en blanco (0 bytes)

Backend:
- `backend/app/__init__.py`
- `backend/app/api/__init__.py`
- `backend/app/api/v1/__init__.py`
- `backend/app/api/v1/endpoints/ai.py`
- `backend/app/api/v1/endpoints/categories.py`
- `backend/app/api/v1/endpoints/diagnostics.py`
- `backend/app/api/v1/endpoints/repairs.py`
- `backend/app/api/v1/endpoints/stats.py`
- `backend/app/api/v1/endpoints/users.py`
- `backend/app/core/__init__.py`
- `backend/app/crud/__init__.py`
- `backend/app/crud/category.py`
- `backend/app/crud/inventory.py`
- `backend/app/crud/repair.py`
- `backend/app/crud/user.py`
- `backend/app/routers/__init__.py`
- `backend/app/schemas/category.py`
- `backend/app/schemas/diagnostic.py`
- `backend/app/schemas/repair.py`
- `backend/app/services/ai_detector.py`
- `backend/app/services/pdf_generator.py`
- `backend/app/services/quote_calculator.py`
- `backend/tests/__init__.py`

Frontend:
- `src/composables/useInventory.js`
- `src/domain/awg/model.ts`
- `src/domain/length/model.ts`
- `src/domain/numberSystem/model.ts`
- `src/domain/resistorColor/model.ts`
- `src/domain/smdCapacitor/model.ts`
- `src/domain/smdResistor/model.ts`
- `src/views/HomeView.vue`
- `src/vue/components/admin/CategoryManager.vue`
- `src/vue/components/admin/ClientDetail.vue`
- `src/vue/components/admin/ClientList.vue`
- `src/vue/components/admin/InventoryAlerts.vue`
- `src/vue/components/admin/RepairManager.vue`
- `src/vue/components/admin/RepairStatusEditor.vue`
- `src/vue/components/admin/StatsCards.vue`
- `src/vue/components/admin/StockMovements.vue`
- `src/vue/components/ai/AIAnalysisResult.vue`
- `src/vue/components/ai/FaultDetector.vue`
- `src/vue/components/ai/FaultMarker.vue`
- `src/vue/components/ai/ImageUploader.vue`
- `src/vue/components/auth/AccountDelete.vue`
- `src/vue/components/auth/PasswordReset.vue`
- `src/vue/components/auth/RegisterForm.vue`
- `src/vue/components/dashboard/QuickStats.vue`
- `src/vue/components/dashboard/RepairCard.vue`
- `src/vue/components/dashboard/RepairTimeline.vue`
- `src/vue/components/dashboard/RepairsList.vue`
- `src/vue/components/dashboard/StatusBadge.vue`
- `src/vue/components/dashboard/UserProfile.vue`

Seeds (vacios):
- `database/seeds/001_categories.sql`
- `database/seeds/002_brands.sql`
- `database/seeds/003_instruments.sql`
- `database/seeds/004_faults.sql`
- `database/seeds/005_admin_user.sql`

Otros:
- `$base.ttf,`

