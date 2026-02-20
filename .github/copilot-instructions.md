# CDS Operative Instructions (Aditivo / No Destructivo)

## Scope
- Project: `Cirujano de Sintetizadores (CDS)`
- Stack: `Vue 3 + Vite | FastAPI + SQLAlchemy | SQLite -> PostgreSQL (gradual)`
- Architecture target: `modular monolith`

## Mandatory Rules
1. `Pre-check first`: before creating/moving/renaming, verify if it already exists (`rg`, `find`, `ls`).
2. `Additive only`: extend what exists; do not remove active flows without validated replacement.
3. `No mass rewrites`: migrate by module and by endpoint/component, one unit at a time.
4. `Compatibility`: keep current endpoints/routes working during migration.
5. `No unnecessary renames`: keep current domain names used by the repo (`Repair`, `OT`, etc.).
6. `Real data`: do not invent entities/fields/statuses not grounded in current models/docs.
7. `Backend layers`:
   - routers -> services -> repositories
   - routers must not own business rules
   - repositories must not own business rules
8. `Frontend layers`:
   - views/components -> store/composable -> api client
   - avoid direct HTTP calls from views/components when migrating a module
9. `DB migration`: SQLite -> PostgreSQL must be gradual and validated with Alembic and tests.
10. `Phase closure criteria`:
    - `npm run build` passes
    - backend starts and key tests pass
    - OT critical flow works end-to-end

## Current Priority Order
1. OT core flow reliability (admin + client + payments + closure PDF).
2. Style hygiene (`no inline CSS`, SCSS consistency).
3. Data consistency (logos/brands/instruments sync).
4. Progressive backend layering (service/repo extraction per module).
5. SQLite -> PostgreSQL transition with rollback path.

## Execution Pattern (per task)
1. Audit current implementation.
2. Reuse existing module/file/class when possible.
3. Implement minimal additive change.
4. Validate (`build`, tests, manual flow).
5. Document result and next pending item.

## References
- Operative plan: `docs/PLAN_OPERATIVO_CDS.md`
- Master TODO: `TODO_MASTER_FASES.md`
- Phase-0 audit script: `scripts/phase0_precheck.sh`
