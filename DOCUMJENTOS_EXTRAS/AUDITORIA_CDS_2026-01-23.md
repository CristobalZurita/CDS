# AUDITORIA CDS - ESTADO ACTUAL
**Fecha:** 2026-01-23
**Principio:** ADITIVO, NO DESTRUCTIVO

---

## 1) Backend (estado real)
- API v1 activa con routers legacy + routers nuevos (tickets, compras, manuales, firmas, photo-requests).
- Importador `/imports/run` activo con auditoria a SQLite local.
- Búsqueda global (`/search`) integrada a clientes, instrumentos, OT, inventario, tickets, manuales y compras.
- Servicio de reportes avanzado implementado en `/analytics/*`, pero no usado por UI.

## 2) Frontend (estado real)
- Admin: Wizards activos (Cliente/OT, Inventario, Materiales, Tickets, Compras, Manuales, Firmas).
- Admin: Menú con Tickets, Compras y Manuales (solo vistas de listado).
- Firma pública disponible en `/signature/:token`.
- Subida pública de fotos en `/photo-upload/:token`.

## 3) Integraciones activas
- Inventario -> OT (materiales usados con costos).
- OT -> firma de ingreso/retiro (link generado + captura de firma).
- Manuales -> instrumentos (asociación por modelo).
- Photo requests -> OT (token público + adjunto a OT).

## 4) Brechas confirmadas (funcionalidad)
- SSE/WS para firma en tiempo real: no existe canal de actualización (solo flujo manual por link).
- PDF final de OT con firmas y resumen: solo placeholder (`pdf_generator`).
- Vista detalle para tickets, compras y manuales: solo listados en UI.
- Carrito/e-commerce: router vacío (`backend/app/routers/cart`).
- Reportes avanzados: endpoints existen en `/analytics`, UI consume `/stats` básico.

## 5) Cuellos de botella probables
- Listados sin paginación en `/clients`, `/repairs`, `/inventory`, `/tickets`, `/purchase-requests`, `/manuals`, `/appointments` (riesgo de cargas grandes).
- Búsqueda global ejecuta varias consultas por request y limita por entidad, no por total.
- API tiene doble sistema de routers (legacy en `app/routers` + `api/v1/endpoints`), lo que complica mantenimiento.

## 6) Archivos sin conectar (detectados)
- `src/router/index.ts` no es usado por `src/main.js` (se usa `src/router/index.js`).
- `src/views/HomeView.vue` no está referenciado en el router principal.
- `backend/app/api/v1/endpoints/categories.py`, `diagnostics.py`, `repairs.py`, `users.py` existen pero no se incluyen en `api_router`.
- `backend/app/routers/cart`, `backend/app/routers/keyboards`, `backend/app/routers/repair_parts` están vacíos.
- `backend/app/routers/__pycache__/*.pyc` de módulos sin fuente (dashboard, history, legal, roles, notification, games, streaming, association, photo, payments_external).

## 7) Endpoints faltantes / incompletos
- OT PDF (descarga/preview): no hay endpoint funcional; solo placeholder en servicio.
- SSE/WS de firmas: no existe endpoint de suscripción o polling dedicado.
- Carrito/checkout: no hay endpoints implementados.
- Estadísticas avanzadas: endpoints existen, pero falta su integración UI.

## 8) Recomendación de validación
1) Migrar DB: `alembic upgrade head`.
2) Re-seed de permisos: `PYTHONPATH=. python scripts/seed_permissions.py`.
3) Probar endpoints clave en `/docs`:
   - `/signatures/requests`, `/signatures/submit`
   - `/tickets/`, `/purchase-requests/`, `/manuals/`
   - `/photo-requests/`
   - `/analytics/*` (si se va a integrar en UI)
4) Verificar UI admin:
   - `/admin/wizards`
   - `/admin/tickets`
   - `/admin/purchase-requests`
   - `/admin/manuals`

---

**Resultado:** el core operativo está activo, pero faltan cierres (PDF, SSE, ecommerce) y hay varios bloques sin conectar (routers legacy duplicados, archivos UI no usados, endpoints avanzados sin consumo).
