# ESTADO REAL DEL PROYECTO (CONSOLIDADO)

## Fuentes consideradas
- ANALISIS_COMPARATIVO_PROYECTOS.md: OK
- APPOINTMENT_CHECKLIST.md: OK
- APPOINTMENT_SYSTEM.md: OK
- AUDIT_REPORT.md: OK
- AUDIT_TECHNICAL_STATUS.md: OK
- AUDITORIA_CDS_01.ms: OK
- AUDITORIA_CDS_FIX_02.md: OK
- AUDITORIA_CDS_FIX.md: OK
- AUDITORIA_CDS_PENDIENTES.md: OK
- AUDITORIA_CDS_RESUMEN.md: OK
- AUDITORIA_CDS.md: OK
- AUDITORIA_COMPLETA_2026-01-18.md: OK
- AUDITORIA_ENDPOINTS_CHECKLIST.md: OK
- AUDITORIA_ENDPOINTS_REAL.md: OK
- AUDITORIA_ENDPOINTS_RESUMEN.md: OK
- AUDITORIA_ENDPOINTS_TABLA.md: OK

## Estado actual (sí/no)
- Permisos granulares en backend: APLICADO (0 pendientes segun AUDITORIA_CDS_PENDIENTES.md)
- Frontend placeholders: - Vistas placeholder: 2
- TODO/FIXME/HACK: - TODO/FIXME/HACK: 3

## Pendientes confirmados (según la data)
- Basado en AUDITORIA_CDS_PENDIENTES.md
  - Endpoints con auth sin permiso granular: 0
  - Vistas placeholder: 2
  - Imports /src inexistentes: 0
  - TODO/FIXME/HACK: 3
  - Archivos vacíos: 0

## Inconsistencias detectadas entre reportes
- FIX_02 reporta 51 endpoints pendientes, pero PENDIENTES reporta 0. Confirmar en código actual.

## Lectura de estado por áreas
### Backend
- Permisos granulares: ver sección anterior.
- Migraciones: revisar cadena Alembic y confirmar `down_revision` real.
- Endpoints: contrastar con AUDITORIA_ENDPOINTS_* si están actualizados.

### Frontend
- Revisar vistas marcadas como placeholder y confirmar si son reales o falsos positivos.
- Revisar TODO/FIXME/HACK en UI crítica.

## Acciones recomendadas para fijar el estado real
1) Validar permisos granulares con búsqueda en `backend/app/routers` (require_permission).
2) Confirmar Alembic head chain (`alembic heads` y revisar `down_revision`).
3) Revisar TODOs listados y decidir si se eliminan, documentan o implementan.
4) Comparar endpoints con tablas AUDITORIA_ENDPOINTS_* para detectar endpoints inexistentes o faltantes.