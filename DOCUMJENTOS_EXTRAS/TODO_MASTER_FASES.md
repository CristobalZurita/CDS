# TODO Master (Programa + Web)

Regla base: trabajo **aditivo, no destructivo**. Antes de cambiar, verificar si ya existe archivo, variable o flujo reutilizable.

## Estado global
- Fecha base: 2026-02-19
- Objetivo: cumplimiento tecnico + cumplimiento academico (modulos 4 a 9)

## Fase 0 - Baseline unico
- [x] Definir orden de trabajo por fases cruzadas
- [x] Identificar brechas criticas (datos, CI, tests, backend DB, modulos 8/9)
- [ ] Consolidar reporte unico "antes/despues" en `docs/`

## Fase 1 - Datos de instrumentos (canonica + compatibilidad)
- [x] Mantener `src/data/instruments.json` como fuente canonica
- [x] Generar `src/assets/data/instruments.json` compatible y sincronizado desde el canonico
- [x] Preservar registros legacy fuera de la lista activa (`legacy_archived`) sin borrado destructivo
- [x] Agregar validacion automatica de consistencia (249 fotos / 214 instrumentos)
- [x] Integrar validacion en workflow `sync-instruments`
- [ ] Revisar consumidores para dejar una sola ruta funcional documentada (sin ambiguedad)

## Fase 2 - Consumidores front/back
- [ ] Alinear consumo de datasets en frontend (`useInstruments`, `useDiagnostic`, catalogos)
- [ ] Alinear consumo en backend (`diagnostic`, `brands`, `quotation`)
- [ ] Definir y documentar politica de instrumentos con `marca_habilitada=false`

## Fase 3 - CI y testing frontend
- [ ] Agregar script `lint` faltante en `package.json`
- [ ] Agregar script `test:integration` faltante en `package.json`
- [ ] Unificar configuracion de Vitest (evitar doble config activa)
- [ ] Unificar estrategia ESLint (flat config vs legacy)

## Fase 4 - Backend DB y tests
- [ ] Corregir desalineacion de schema en appointments (`client_id` y relacionados)
- [ ] Alinear migraciones para entorno de tests
- [ ] Dejar `pytest` sin fallas bloqueantes

## Fase 5 - UI, SASS y checklist funcional
- [ ] Revalidar checklist carrusel/fotos (20 puntos)
- [ ] Confirmar botones flotantes y scroll en vistas publicas
- [ ] Mantener gate de "sin CSS inline" en CI

## Fase 6 - TS incremental
- [ ] Plan por lotes para pares `.js/.ts` duplicados
- [ ] Normalizar imports para evitar ambiguedad de resolucion
- [ ] Agregar chequeo de typecheck en pipeline

## Fase 7 - Cierre academico modulos 8 y 9
- [ ] Evidencia formal de portafolio (hosting/demo/video)
- [ ] Evidencia formal de empleabilidad (CV, plan de busqueda, pitch)
- [ ] Matriz final "criterio del modulo -> evidencia"

## Fase 8 - Cierre 100% + 101%
- [ ] Auditoria automatica final (datos + estilos + tests + build)
- [ ] Corregir claims de documentacion segun evidencia real
- [ ] Reporte final trazable por modulo
