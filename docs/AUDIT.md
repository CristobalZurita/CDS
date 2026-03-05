# Auditoria

Este archivo queda como punto de entrada corto.

Documentos activos para el trabajo incremental:

- `docs/AUDITORIA_VIVA.md`
- `docs/MATRIZ_AUTORIDAD.md`

Referencia puntual de auditoria backend:

- Modelo `AuditLog`: `backend/app/models/audit.py`
- Servicio de logging: `backend/app/services/logging_service.py`
- Hooks visibles en auth y reparaciones

Siguiente foco operativo:

- ampliar cobertura before/after en endpoints criticos
- seguir encauzando modulos que aun usan API directa teniendo store o composable disponible
