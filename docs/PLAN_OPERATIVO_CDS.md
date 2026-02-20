# Plan Operativo CDS (Aditivo / No Destructivo)

## Regla central
Trabajo aditivo y adaptativo: no destruir ni sustraer. Antes de crear/cambiar, verificar existencia y extender desde lo que ya funciona.

## Fase 0 - Auditoria base (obligatoria antes de cambios grandes)
Objetivo: confirmar estado real del repo y usar nombres de dominio existentes.

Checklist:
- [ ] Modelos SQLAlchemy mapeados.
- [ ] Endpoints activos mapeados.
- [ ] Accesos DB directos en routers detectados.
- [ ] Llamadas HTTP directas en frontend detectadas.
- [ ] Estado Alembic registrado.

Comando sugerido:
```bash
bash scripts/phase0_precheck.sh
```

## Fase 1 - Repositorios (backend)
Objetivo: crear/usar capa `repositories/` sin romper routers actuales.

Checklist:
- [ ] `base_repository.py` disponible (crear si no existe).
- [ ] Repo del dominio OT (`Repair`) implementado de forma aditiva.
- [ ] Sin cambios destructivos en rutas activas.

## Fase 2 - Servicios (backend)
Objetivo: extraer reglas de negocio a `services/` por endpoint, uno a la vez.

Checklist:
- [ ] Primer endpoint OT migrado `router -> service -> repo`.
- [ ] Status code y payload se mantienen compatibles.
- [ ] Flujo OT sigue funcional.

## Fase 3 - SQLite -> PostgreSQL (gradual)
Objetivo: migracion segura, reversible y validada.

Checklist:
- [ ] Alembic al dia en SQLite.
- [ ] Postgres local con `alembic upgrade head`.
- [ ] Tests ejecutados contra Postgres.
- [ ] Backup SQLite retenido durante transicion.

## Fase 4 - Frontend API layer (gradual)
Objetivo: extraer llamadas HTTP directas por modulo, sin reescritura masiva.

Checklist:
- [ ] API client por dominio usado por OT.
- [ ] Vistas OT sin llamadas HTTP directas nuevas.
- [ ] Build sin regresiones.

## Fase 5 - Cierre y despliegue
Objetivo: cierre estable y reproducible.

Checklist:
- [ ] Build frontend OK.
- [ ] Backend arranca sin errores.
- [ ] Flujo manual OT completo OK (crear -> diagnosticar -> materiales -> firmas -> cierre PDF).
- [ ] Documentar evidencia final en `TODO_MASTER_FASES.md`.
