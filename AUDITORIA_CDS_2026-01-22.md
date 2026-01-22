# AUDITORIA CDS - ESTADO ACTUAL
**Fecha:** 2026-01-22
**Principio:** ADITIVO, NO DESTRUCTIVO

---

## 1) Backend (estado real)
- Permisos granulares operativos (`require_permission`).
- Nuevos recursos agregados: tickets, purchase_requests, manuals, signatures.
- Nuevas tablas: `tickets`, `ticket_messages`, `purchase_requests`, `purchase_request_items`, `manual_documents`, `signature_requests`.
- Reparaciones ahora tienen campos de firmas (ingreso/retiro).
- Router de busqueda global incluye tickets/manuals/compra.

## 2) Frontend (estado real)
- Admin: Magos activos (Cliente/OT, Inventario, Materiales, Tickets, Compras, Manuales, Firmas).
- Admin: Nuevas paginas en menu (Tickets, Compras, Manuales).
- Firma digital publica: `/signature/:token`.

## 3) Integraciones activas
- Inventario -> OT (materiales usados con costos).
- OT -> firma de ingreso/retiro (link generado).
- Manuales -> instrumentos (asociacion por modelo).

## 4) Brechas confirmadas
- SSE/WS para firma en tiempo real (pendiente, hoy se usa enlace manual).
- PDF final de OT con firmas y resumen (pendiente).
- Vista detalle de tickets (pendiente).
- Carrito externo/e-commerce (pendiente).
- Reportes avanzados en estadisticas (pendiente).

## 5) Recomendacion de validacion
1) Migrar DB: `alembic upgrade head`.
2) Re-seed de permisos: `PYTHONPATH=. python scripts/seed_permissions.py`.
3) Probar endpoints nuevos en `/docs`:
   - `/signatures/requests`
   - `/tickets/`
   - `/purchase-requests/`
   - `/manuals/`
4) Verificar UI admin:
   - `/admin/wizards`
   - `/admin/tickets`
   - `/admin/purchase-requests`
   - `/admin/manuals`

---

**Resultado:** avance funcional con nuevos flujos, faltan cierres (PDF, SSE, ecommerce).
