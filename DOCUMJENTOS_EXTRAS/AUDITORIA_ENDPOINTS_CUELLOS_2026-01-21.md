# AUDITORIA ENDPOINTS Y CUELLOS DE BOTELLA
**Fecha:** 2026-01-21
**Alcance:** Frontend (consumo API) + Backend (routers + endpoints v1)
**Criterio:** Aditivo, no destructivo

---

## 1) Resumen ejecutivo
- **Cobertura API:** El backend expone endpoints completos, pero el frontend usa rutas inconsistentes (duplicadas o con prefijos distintos), lo que genera 404/307 y flujos rotos.
- **Cuellos de botella principales:** discrepancia de rutas (`/items` vs `/inventory`, `/stats` vs `/analytics`), uso de `fetch` fuera del cliente API y base URL duplicada/hardcodeada.
- **Impacto directo:** botones que “no hacen nada”, pantallas sin datos, operaciones CRUD que fallan al no coincidir el endpoint o el payload esperado.

---

## 2) Mapa backend (rutas reales)
**Routers (app/routers):** `/clients`, `/client`, `/repairs`, `/devices`, `/inventory`, `/categories`, `/appointments`, `/contact`, `/newsletter`, `/analytics`, `/payments`, `/invoices`, `/warranties`, `/stock-movements`, `/uploads`, `/tools`, `/diagnostic`, `/quotations`, `/repair-statuses`, `/users`, `/instruments`.

**API v1 endpoints (app/api/v1/endpoints):** `/auth/*`, `/stats/*`, `/items/*`, `/imports/*`, `/inventory/*`, `/brands/*`, `/diagnostics/*`, `/repairs/*`, `/users/*`.

**Nota:** Hay rutas duplicadas entre `app/api/v1/endpoints/*` y `app/routers/*` (por ejemplo, categorías e inventario).

---

## 3) Consumo frontend (rutas detectadas)
Rutas encontradas en `src/`:
- `/appointments/` (PageHeader, SchedulePage, Appointments admin)
- `/auth/forgot-password`, `/auth/reset-password`
- `/categories`
- `/client/dashboard`, `/client/profile`, `/client/repairs`
- `/clients`, `/clients/`
- `/contact`, `/contact/messages`
- `/devices/`
- `/diagnostic`, `/diagnostic/calculate`
- `/imports/run`
- `/instruments`
- `/inventory`, `/inventory/`
- `/newsletter/subscribe`, `/newsletter/subscriptions`
- `/quotations/estimate`
- `/repairs`, `/repairs/`
- `/stats`
- `/stock-movements`
- `/uploads/images`
- `/users`

Rutas con problemas detectados por implementación (no solo uso):
- `src/vue/components/admin/StockMovementsList.vue` usa `'/api/stock-movements'` (prefijo erróneo)
- `src/vue/components/modals/AppointmentModal.vue` usa `fetch('/api/v1/appointments/')` (no usa API base)
- `src/vue/content/pages/admin/InventoryPage.vue` hace `api.get('/items/:id')` (mezcla `/items` y `/inventory`)

---

## 4) Inconsistencias que generan fallos
### 4.1 Doble cliente HTTP (baseURL inconsistente)
- `src/services/api.js` usa `VITE_API_URL` y funciona con `.env`.
- `src/composables/useApi.js` **ignora `.env`** y usa `http://localhost:8000/api/v1` fijo.
- Resultado: en producción o dominios distintos, parte del frontend apunta a un host incorrecto.

### 4.2 Inventario duplicado
- **Backend**: `/items` (api/v1 endpoints) y `/inventory` (app/routers) coexisten.
- **Frontend**: mezcla ambos (`/inventory` en store, `/items/:id` en InventoryPage).
- Impacto: consultas parciales y estado inconsistente.

### 4.3 Estadísticas
- **Backend**: `/stats/*` (api/v1) y `/analytics/*` (router analytics).
- **Frontend**: usa `/stats`.
- Impacto: datos incompletos si solo se llena uno de los módulos; confusión de fuente.

### 4.4 AppointmentModal usa fetch local
- `fetch('/api/v1/appointments/')` se ejecuta contra **frontend (5173)** y no contra backend.
- Impacto: 404 o CORS según proxy; la cita no se crea aunque la UI muestre envío.

### 4.5 Prefijo incorrecto en stock movements
- `'/api/stock-movements'` debería ser `'/stock-movements'` usando el base URL.
- Impacto: 404 directo.

### 4.6 Imports de inventario
- `/imports/run` requiere admin y usa DB `backend/instance/cirujano.sqlite` + Excel externo.
- Si el Excel no está o el path no existe → `404 Excel master file not found`.
- Impacto: Inventario unificado muestra vacío o error.

---

## 5) Cuellos de botella (prioridad técnica)
1) **Base URL partida (api.js vs useApi.js)** → rompe parte del sistema al cambiar host.
2) **Inventario con dos APIs** (`/items` y `/inventory`) → mezcla de POC con DB real.
3) **Stats/Analytics duplicados** → Admin no muestra datos consistentes.
4) **Uso de fetch hardcoded** → bypass de auth y CORS.
5) **Endpoints que dependen de archivos externos** (Excel) → fallas silenciosas.

---

## 6) Recomendaciones aditivas (sin borrar nada)
1) Unificar consumo API:
   - Migrar `useApi.js` a usar `VITE_API_URL` como `api.js`.
2) Elegir un único módulo de inventario en frontend:
   - O todo vía `/inventory` (DB), o todo vía `/items` (Excel POC).
3) Normalizar stats:
   - Usar `/stats` como fuente primaria y documentar si `/analytics` queda para BI avanzado.
4) Eliminar fetch hardcoded:
   - AppointmentModal debe usar `api.post('/appointments/')` o `useApi().post`.
5) Confirmar imports:
   - Validar el Excel en `Inventario_Cirujanosintetizadores.xlsx` o documentar su ausencia.

---

## 7) Evidencia (archivos clave)
- `src/services/api.js`
- `src/composables/useApi.js`
- `src/views/InventoryUnified.vue`
- `src/vue/content/pages/admin/InventoryPage.vue`
- `src/vue/components/modals/AppointmentModal.vue`
- `backend/app/api/v1/endpoints/inventory.py`
- `backend/app/routers/inventory.py`
- `backend/app/api/v1/endpoints/stats.py`
- `backend/app/routers/analytics.py`

---

## 8) Próximo paso sugerido
- Decidir **una sola ruta oficial** para Inventario y Stats y ejecutar la normalización del frontend.
- Luego re‑auditar con pruebas rápidas (`curl`) para validar 200/401/403 por endpoint.
