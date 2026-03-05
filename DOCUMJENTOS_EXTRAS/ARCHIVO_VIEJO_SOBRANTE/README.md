# Archivo Viejo / Sobrante

Fecha: 2026-02-28

Este directorio concentra archivos que no forman parte del flujo operativo actual del proyecto, pero que se conservaron por referencia histórica.

## Se movió aquí

### DB legacy

- `db/cirujano.db.root_legacy`
  - Antes estaba en la raíz del repo como `cirujano.db`.
  - No es la DB activa del backend.
  - Está atrasada respecto de `backend/cirujano.db`.
  - Le faltan al menos estas tablas presentes en la DB operativa:
    - `instrument_photos`
    - `quote_items`
    - `quote_recipients`
    - `repair_intake_sheets`

- `db/cirujano.sqlite.instance_legacy`
  - Antes estaba en `backend/instance/cirujano.sqlite`.
  - No aparece como DB principal en la configuración actual.
  - Tiene un esquema muy incompleto y de otra etapa del proyecto.
  - Contenía tablas legacy como `inventory`, `items` e `import_runs`.

### Testing legacy

- `testing/playwright_test.legacy.js`
  - Antes estaba en la raíz como `playwright_test.js`.
  - No corresponde al sitio actual.
  - Usa `file://index.html` y selectores de otro proyecto/flujo.
  - Se conserva sólo como referencia histórica.

## Se mantiene en su lugar

- `backend/cirujano.db`
  - DB operativa actual del backend.
  - Referenciada por la configuración principal del proyecto.

- `backend/tests/test_cirujano.db`
  - DB usada por pruebas backend.
  - No se movió porque sí participa del flujo de test.

## Suite de pruebas vigente

Los tests activos del proyecto quedaron en:

- `tests/e2e/`
- `tests/stores/`
- `tests/composables/`
- `tests/integration/`

Comandos principales:

```bash
npm run test:e2e
npm run build
npm run test:coverage
```
