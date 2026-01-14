# Cirujano - Arquitectura y Flujo

Resumen de la arquitectura, módulos, endpoints y flujo de usuario.

## Backend
- FastAPI, SQLAlchemy
- Carpetas principales: `backend/app/models`, `backend/app/api/v1/endpoints`
- Rutas expuestas (ejemplos):
  - `/api/v1/users`
  - `/api/v1/inventory`
  - `/api/v1/repairs`
  - `/api/v1/diagnostics`

## Frontend
- Vue 3 + Vite
- Stores: Pinia en `src/stores`
- Composables: `src/composables`
- Componentes principales en `src/vue/components`

## Flujo de usuario
- Registro / Login → Dashboard
- Desde dashboard se accede a Inventario, Reparaciones, Instrumentos, etc.

## Ejecutar localmente
Backend:
```bash
# Activar entorno y ejecutar (ejemplo)
cd backend
uvicorn backend.app.main:app --reload
```

Frontend:
```bash
cd cirujano-front
npm install
npm run dev
```
