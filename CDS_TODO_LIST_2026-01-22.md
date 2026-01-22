# CDS - TODO LIST COMPLETO (A-F)
**Fecha:** 2026-01-22
**Principio:** ADITIVO, NO DESTRUCTIVO

---

## A) Inventario / SKU (recatalogo)
**Objetivo:** Normalizar SKU visibles y consistentes, mantener ID interno auto.

**Estado actual:**
- Script de normalizacion Excel: `scripts/ingest/normalize_excel.py`.
- Script de importacion a DB: `scripts/ingest/import_to_db.py` (tabla `products`).

**Pendiente / tareas:**
1) Definir reglas finales de SKU por categoria (CAP, RES, DIO, IC, Q, LED, TOOL, INS).
2) Ejecutar normalizacion e importacion:
   - `python scripts/ingest/normalize_excel.py`
   - `python scripts/ingest/import_to_db.py`
3) Validar resultados en UI Inventario.
4) Ajustar orden visual por SKU (mostrar ordenado por `sku`, no por `id`).

---

## B) Clientes + Instrumentos + OT (codigos correlativos)
**Objetivo:** Mantener codigo fijo de cliente y OT correlativa por cliente.

**Decision final (confirmada):**
- Cliente: `CDS-001`
- OT base: `CDS-001-OT-001`
- Multiples instrumentos en la misma OT: `CDS-001-OT-001-01`, `...-02`, `...-NN`
- Nuevo ciclo para mismo cliente: `CDS-001-OT-002`, etc.

**Estado actual:**
- Codigo cliente calculado en backend.
- Codigo OT generado en backend.
- Agrupacion OT soportada en UI (marca base y genera -01, -02...).

**Pendiente / tareas:**
1) Ajustar flujo UI para agrupar OT al crear el primer instrumento del dia.
2) Forzar consistencia al crear la primera OT agrupada (que el primer instrumento quede -01).
3) Mostrar codigos OT/Cliente en listados y fichas.

---

## C) Reparaciones + Consumo de inventario
**Objetivo:** Registrar consumo por OT y descontar stock con trazabilidad.

**Estado actual:**
- Existe `RepairComponentUsage` (materiales usados).
- UI permite agregar materiales y costos.

**Pendiente / tareas:**
1) Definir si descuento es inmediato o al cerrar OT.
2) Agregar validacion de stock y registro en `stock_movements`.
3) Registrar detalle de materiales usados en PDF de cierre.

---

## D) Tickets internos (consultas)
**Objetivo:** Gestion de consultas internas por cliente/OT.

**Estado actual:**
- Backend: modelos `tickets` y `ticket_messages`.
- Backend: router `/api/v1/tickets`.
- UI: pagina Admin `Tickets` + Mago de tickets.

**Pendiente / tareas:**
1) Agregar vista detalle de ticket (thread completo).
2) Permitir cierre/reapertura desde UI.
3) Notificacion interna (opcional).

---

## E) Carrito interno (compras sugeridas)
**Objetivo:** Crear solicitudes de compra asociadas a OT/cliente.

**Estado actual:**
- Backend: `purchase_requests` + `purchase_request_items`.
- UI: pagina Admin `Compras` + Mago de compras.

**Pendiente / tareas:**
1) Agregar estados avanzados: aprobado, comprado, recibido.
2) Agregar enlaces externos por item (tiendas/proveedores).
3) Notificacion al cliente (email).

---

## F) Firmas + Manuales (documentacion tecnica)
**Objetivo:** Firma de ingreso/retiro + manuales asociados a modelo.

**Estado actual:**
- Backend: `signature_requests` + columnas en `repairs`.
- UI: pagina firma publica `/signature/:token`.
- UI: mago para crear firmas.
- Backend: `manual_documents` + router `/manuals`.
- UI: pagina Admin `Manuales` + mago para subir manual.

**Pendiente / tareas:**
1) Agregar SSE/WS en frontend para refrescar firma en tiempo real.
2) Incluir firmas en PDF final de OT.
3) Mostrar manual disponible en ficha de instrumento.

---

## Bloque final: validacion integral
1) Revisar endpoints nuevos en Swagger (`/docs`).
2) Ejecutar migracion `alembic upgrade head`.
3) Re-seed de permisos para nuevos recursos:
   - `PYTHONPATH=. python scripts/seed_permissions.py`
4) Probar flujo completo:
   - Cliente -> Instrumento -> OT -> Firma -> Materiales -> Cierre.

---

**Nota:** Todo es aditivo, sin eliminar nada existente.
