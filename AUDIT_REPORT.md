# CDS Audit Report

## Critical

- Alembic multiple heads: Multiple migrations have down_revision = None: 78b5056b2086_initial_baseline_empty.py, 001_add_permission_invoice_warranty_models.py (/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/backend/alembic/versions)

## High

- Permissions not applied in routers: No router in /mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/backend/app/routers uses require_permission/require_any_permission/require_permissions. (/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/backend/app/routers)
- Missing permission/role seeding: Seed scripts exist but do not create Permission/Role data. (/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/backend/scripts)

## Medium

- Placeholder view: View still contains placeholder content. (src/modules/length/LengthView.vue)
- Placeholder view: View still contains placeholder content. (src/modules/temperature/TemperatureView.vue)
- Placeholder view: View still contains placeholder content. (src/modules/ohmsLaw/OhmsLawView.vue)
- Placeholder view: View still contains placeholder content. (src/modules/awg/AwgView.vue)
- Placeholder view: View still contains placeholder content. (src/modules/numberSystem/NumberSystemView.vue)

## Low

- None

## Info

- Routes inventory: Backend routes: 60, Frontend routes: 36
