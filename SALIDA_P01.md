# Alcance y Fuente de Verdad

- Fuente de verdad: `SALIDA_P00.md`. Este documento `SALIDA_P01.md` se genera **únicamente** a partir de la información contenida en `SALIDA_P00.md`.
- Alcance del análisis: únicamente las secciones y archivos listados en `SALIDA_P00.md` (secciones: Resumen General, Archivos Clasificados, Archivos Vacíos o Inertes, Imports y Conexiones Sin Efecto, Flujos Detectados como Incompletos).

---

# Normalización Semántica Detectada

- Variante detectada: `diagnostic` (backend) vs `DiagnosticsList` (frontend).
  - Ubicación: ./backend/app/api/v1/endpoints/diagnostics.py, ./backend/app/models/diagnostic.py, ./backend/app/routers/diagnostic.py, ./backend/app/schemas/diagnostic.py , ./src/vue/components/admin/DiagnosticsList.vue
  - Forma CANÓNICA propuesta: `diagnostics` (plural para colecciones).
  - Alcance: backend / frontend

- Variante detectada: `repair` (modelo backend) vs `Repairs*` (UI).
  - Ubicación: ./backend/app/api/v1/endpoints/repairs.py, ./backend/app/crud/repair.py, ./backend/app/models/repair.py, ./backend/app/routers/repair.py, ./backend/app/schemas/repair.py , ./src/vue/components/admin/RepairsList.vue, ./src/vue/components/dashboard/RepairsList.vue, ./src/vue/content/pages/RepairsPage.vue
  - Forma CANÓNICA propuesta: `repair` (modelo) / `repairs` (colecciones).
  - Alcance: backend / frontend

- Variante detectada: `stock_movement` (backend) vs `stockMovements` (frontend).
  - Ubicación: ./backend/app/models/stock_movement.py, ./backend/app/routers/stock_movement.py , ./src/stores/stockMovements.js
  - Forma CANÓNICA propuesta: documentar patrón (backend snake_case, frontend camelCase).
  - Alcance: backend / frontend

- Variante detectada: uso mixto `AI` (backend) y `IA` (frontend `CotizadorIAPage`).
  - Ubicación: ./backend/app/api/v1/endpoints/ai.py , ./src/vue/content/pages/CotizadorIAPage.vue
  - Forma CANÓNICA propuesta: documentar uso consistente (ej. `AI`).
  - Alcance: frontend / backend

- Variante detectada: `quotation` vs `quotes`/`estimate` en rutas y componentes.
  - Ubicación: ./backend/app/routers/quotation.py , ./src/vue/components/quotation/QuotationResult.vue
  - Forma CANÓNICA propuesta: `quotation` (entidad) / `quotes` (colecciones/paths).
  - Alcance: backend / frontend


---

# Modelos de Dominio Existentes

- No se encontraron modelos explícitos en `backend/app/models` listados como ACTIVO en `SALIDA_P00.md`.

---

# Huecos Estructurales Reales

- Diagnostic / Quote calculation flows (ALTO)
  - Módulo afectado: `backend/app/routers/diagnostic.py` y rutas listadas bajo `/api/v1/*`.
  - Qué existe: frontend composables y `DiagnosticsList.vue`.
  - Qué NO existe: endpoints numerosos marcados como TODO o sin callers.

- AI pipeline declarado pero no ejecutado (ALTO)
  - Módulo afectado: `backend/app/api/v1/endpoints/ai.py` y `backend/app/services/ai_detector.py`.
  - Qué existe: UI components listados; qué NO existe: endpoints y servicios backend implementados.


---

# Rol de la Carpeta MODELOS

- Observación: `MODELOS` aparece en el repositorio, pero **no** está incluida como parte del análisis en `SALIDA_P00.md`.
- Conclusión: según `SALIDA_P00.md`, `MODELOS` es referencial y no una dependencia activa del proyecto CDS.

---

# Plan de Completado Técnico por Fases

Fase 1 — Normalización semántica y nomenclatura
- Objetivo técnico: Documentar convención de nombres según inconsistencias detectadas en `SALIDA_P00.md`.
- Archivos involucrados: los citados en la sección "Normalización Semántica Detectada" generada más arriba.
- Resultado esperado: documento de normalización (observable).

Fase 2 — Completar placeholders backend
- Objetivo técnico: Priorizar PLACEHOLDER críticos listados en `SALIDA_P00.md` (ej.: `auth.py`, `diagnostic.py`, `ai.py`, `imports.py`).
- Resultado esperado: reducción medible de entradas PLACEHOLDER en `SALIDA_P00.md`.

Fase 3 — Conexión frontend ↔ backend
- Objetivo técnico: Asegurar que vistas y stores consuman endpoints activos listados en `SALIDA_P00.md`.
- Resultado esperado: reducción de flujos incompletos listados.

Fase 4 — Servicios transversales
- Objetivo técnico: Activar servicios listados como PLACEHOLDER (`email_service.py`, `pdf_generator.py`, `quote_calculator.py`).
- Resultado esperado: servicios con actividad y pruebas mínimas.

Fase 5 — IA y procesamiento de imágenes
- Objetivo técnico: Conectar componentes `src/vue/components/ai/*` con endpoints/backend de IA si aparecen implementados; observar resultados.

Fase 6 — Verificación y actualización de inventario
- Objetivo técnico: Ejecutar pruebas y actualizar `SALIDA_P00.md` y `SALIDA_P01.md` con el estado real post-trabajo.
