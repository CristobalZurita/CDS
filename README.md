# Cirujano de Sintetizadores (CDS)
Plataforma integral para gestion de reparaciones de instrumentos, inventario de taller y comunicacion cliente-tecnico.
Incluye portal publico, panel cliente y panel administrador con magos de ingreso.

---

## Modulos principales
- Portal publico: servicios, trabajos, cotizador, contacto.
- Panel cliente: estado de reparaciones, historial, perfil.
- Panel admin: clientes, instrumentos, OT, inventario, categorias, citas, mensajes.
- Magos (admin): ingreso completo, inventario, materiales, tickets, compras, manuales, firmas.

---

## Flujo operativo recomendado (admin)
1) Crear cliente + instrumento + OT con el mago de ingreso.
2) Registrar diagnostico, materiales usados y avances.
3) Solicitar firma de ingreso y retiro (link publico).
4) Cerrar OT y emitir documento final (pendiente de PDF).

---

## Tecnologias
- Frontend: Vue 3 + Vite
- Backend: FastAPI + SQLAlchemy
- DB: SQLite (local), preparado para Postgres

---

## Configuracion
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

## Importacion de inventario (Excel)
1) Normalizar Excel -> JSON:
```
python scripts/ingest/normalize_excel.py
```
2) Importar a DB (tabla products):
```
python scripts/ingest/import_to_db.py
```

---

## Firma digital
- UI publica: `/signature/:token`
- Admin genera token desde mago o ficha de OT.
- Firma se guarda en `uploads/signatures/`.

---

## Auditoria y estado
- Auditoria actual: `AUDITORIA_CDS_2026-01-22.md`
- Todo-list operativo: `CDS_TODO_LIST_2026-01-22.md`

---

## Licencia
Uso interno del proyecto. Ajustar si se publica.
