# Cirujano de Sintetizadores

Repositorio principal del sistema web de Cirujano de Sintetizadores.

Este proyecto concentra la operación del sitio público, el panel administrativo, el portal de cliente y la API principal del sistema.

## Alcance

El sistema cubre, a nivel general:

- sitio público
- autenticación
- panel administrativo
- portal de cliente
- órdenes de trabajo
- cotizaciones
- inventario y tienda
- agenda
- pagos
- media y documentación técnica
- calculadoras electrónicas

## Estructura general

```text
cirujano-front_CLEAN/
├── CDS_VUE3_ZERO/   frontend Vue 3
├── backend/         backend FastAPI
├── scripts/         utilidades internas de soporte
└── .github/         workflows del repositorio
```

## Estado actual

- `CDS_VUE3_ZERO` es el frontend activo del proyecto.
- `backend/` contiene la API y la lógica principal del sistema.
- El repositorio está siendo ordenado como monolito modular.
- La evolución futura de arquitectura está separada de la entrega actual.

## Desarrollo local

### Frontend

```bash
cd CDS_VUE3_ZERO
npm install
npm run dev
```

Para generar build:

```bash
cd CDS_VUE3_ZERO
npm run build
```

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Configuración

La configuración sensible no se documenta en este README y no debe versionarse.

Usa los archivos de ejemplo incluidos en frontend y backend para preparar el entorno local sin exponer credenciales reales.

## Tests

### Backend

```bash
cd backend
pytest tests/ --verbose
```

### Frontend

```bash
cd CDS_VUE3_ZERO
npm run build
```

Si el entorno lo permite, también pueden ejecutarse las pruebas E2E del frontend.

## Seguridad

- No se incluyen credenciales reales en este repositorio.
- No se documentan secretos, tokens, rutas privadas ni detalles operativos sensibles en este archivo.
- La configuración de producción y despliegue debe mantenerse fuera del repositorio público o en canales internos controlados.

## Nota

Este README está intencionalmente reducido a información pública y operativa de alto nivel.
