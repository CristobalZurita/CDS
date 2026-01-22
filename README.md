# Cirujano de Sintetizadores

Plataforma integral para gestión de reparaciones de instrumentos, con portal público, panel de clientes y panel administrativo. Incluye cotización online, agendamiento, seguimiento de reparaciones e inventario del taller.

---

## Estado actual (resumen)
- Backend FastAPI + SQLite operativo con permisos granulares.
- Frontend Vue operativo (portal público, panel cliente y admin).
- CRUD básico funcional para clientes, instrumentos y reparaciones.
- Inventario con CRUD básico, falta integración por reparación.

---

## Módulos principales

### Portal público
- Información del taller, servicios y trabajos.
- Contacto con formulario (mensajes llegan a admin).
- Cotizador online con flujo de diagnóstico.
- Calculadoras electrónicas para estudiantes.

### Panel cliente
- Dashboard con estado de reparaciones.
- Historial de reparaciones + detalle.
- Perfil y datos personales.
- Agendamiento de citas.

### Panel admin
- Clientes (listado + detalle + ingreso completo).
- Reparaciones (listado + creación + detalle avanzado).
- Inventario (listado + creación + edición).
- Categorías, citas, contacto y newsletter.

---

## Flujo operativo recomendado (admin)
1) Crear cliente + instrumento + reparación en **Ingreso completo**.
2) Actualizar estado y registrar avances en la reparación.
3) Adjuntar fotos y notas técnicas.
4) Registrar consumo de inventario (pendiente de integración).
5) Cerrar reparación y emitir documento/boleta (pendiente).

---

## Tecnologías
- **Frontend:** Vue 3 + Vite
- **Backend:** FastAPI + SQLAlchemy
- **DB:** SQLite (local), preparado para Postgres

---

## Requisitos
- Node.js (para frontend)
- Python 3.x (para backend)

---

## Configuración

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000/api/v1
```

### Backend
- Base de datos local: `backend/cirujano.db`

---

## Ejecutar en local

### Backend
```
cd backend
uvicorn app.main:app --reload
```

### Frontend
```
npm install
npm run dev
```

Frontend: `http://localhost:5173`
Backend: `http://localhost:8000`

---

## Migraciones y permisos

### Migraciones
```
cd backend
alembic upgrade head
```

### Seed de permisos/roles
```
cd backend
source .venv/bin/activate
PYTHONPATH=. python scripts/seed_permissions.py
```

---

## Estado de integraciones pendientes
- Inventario asociado a reparaciones (consumo y descuento automático).
- Documentos automáticos (recepción/entrega) con email.
- Contabilidad/pagos y facturación.
- Sistema de tickets para consultas.
- Dashboard admin con KPIs reales (usar `/analytics`).

---

## Auditorías
- Auditoría actual: `AUDITORIA_CDS_2026-01-21.md`
- Auditoría MODELOS: `AUDITORIA_MODELOS_2026-01-21.md`

---

## Licencia
Uso interno del proyecto. Ajustar si se publica.
