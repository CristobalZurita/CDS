# Permisos y Roles (Aditivo)

## Evidencia en backend
- Permisos granulares: `backend/app/services/permission_service.py`
- Dependencias: `backend/app/core/dependencies.py` (require_permission)
- Modelos: `backend/app/models/permission.py`

## Roles
- Admin, Technician, Client (legacy + granular).

## Uso recomendado
- Enrutar todos los endpoints por `require_permission` o `require_permissions`.
