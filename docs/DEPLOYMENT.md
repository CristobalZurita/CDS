# Deployment (Aditivo)

## Backend
- Variables de entorno requeridas: ver `backend/requirements.txt` y `backend/app/core/config.py`.
- Ejecutar migraciones: `alembic upgrade head`.
- Servir API con Uvicorn/Gunicorn según entorno.

## Frontend
- Build con Vite: `npm run build`.
- Servir `dist/` en hosting estático.

## Entorno
- Mantener secretos fuera del repo.
