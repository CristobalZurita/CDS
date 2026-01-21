# AUDITORIA_MAPEO_ENDPOINTS_DB_FRONT

## Alcance
- Mapeo de endpoints backend -> tablas DB -> pantallas frontend (cuando aplica).

## Backend -> DB (heuristico)
### router: `diagnostic.py`
- Tabla/modelo probable: `diagnostic`
- Endpoints:
  - GET /instruments/brands
  - GET /instruments/models/{brand_id}
  - GET /instruments/{instrument_id}
  - GET /faults
  - GET /faults/applicable/{instrument_id}
  - POST /calculate
  - GET /
  - GET /{diagnostic_id}
  - PUT /{diagnostic_id}
  - DELETE /{diagnostic_id}
  - ... y 2 mas

### router: `payments.py`
- Tabla/modelo probable: `payment`
- Endpoints:
  - POST /
  - GET /
  - GET /{payment_id}

### router: `repair_status.py`
- Tabla/modelo probable: `repair_statu`
- Endpoints:
  - GET /
  - POST /
  - PUT /{status_id}
  - DELETE /{status_id}

### router: `quotation.py`
- Tabla/modelo probable: `quotation`
- Endpoints:
  - POST /estimate

### router: `invoice.py`
- Tabla/modelo probable: `invoice`
- Endpoints:
  - POST /
  - POST /from-repair/{repair_id}
  - GET /
  - GET /summary
  - GET /overdue
  - GET /{invoice_id}
  - GET /by-number/{invoice_number}
  - POST /{invoice_id}/items
  - DELETE /{invoice_id}/items/{item_id}
  - POST /{invoice_id}/send
  - ... y 4 mas

### router: `clients.py`
- Tabla/modelo probable: `client`
- Endpoints:
  - GET /
  - GET /{client_id}
  - POST /
  - PUT /{client_id}
  - DELETE /{client_id}
  - GET /{client_id}/devices

### router: `inventory.py`
- Tabla/modelo probable: `inventory`
- Endpoints:
  - GET /
  - GET /{product_id}
  - GET /low-stock/alerts

### router: `appointment.py`
- Tabla/modelo probable: `appointment`
- Endpoints:
  - POST /
  - GET /{appointment_id}
  - GET /
  - GET /email/{email}
  - PATCH /{appointment_id}
  - DELETE /{appointment_id}
  - GET /status/pending
  - GET /status/confirmed

### router: `uploads.py`
- Tabla/modelo probable: `upload`
- Endpoints:
  - POST /images

### router: `stock_movement.py`
- Tabla/modelo probable: `stock_movement`
- Endpoints:
  - GET /
  - POST /

### router: `repair.py`
- Tabla/modelo probable: `repair`
- Endpoints:
  - GET /
  - POST /
  - PUT /{repair_id}
  - DELETE /{repair_id}
  - GET /{repair_id}/audit
  - POST /{repair_id}/components
  - GET /{repair_id}/components
  - DELETE /{repair_id}/components/{usage_id}
  - POST /{repair_id}/notes
  - GET /{repair_id}/notes
  - ... y 2 mas

### router: `instrument.py`
- Tabla/modelo probable: `instrument`
- Endpoints:
  - GET /
  - POST /
  - PUT /{instrument_id}
  - DELETE /{instrument_id}

### router: `newsletter.py`
- Tabla/modelo probable: `newsletter`
- Endpoints:
  - POST /subscribe
  - GET /subscriptions

### router: `category.py`
- Tabla/modelo probable: `category`
- Endpoints:
  - GET /
  - POST /
  - PUT /{category_id}
  - DELETE /{category_id}

### router: `user.py`
- Tabla/modelo probable: `user`
- Endpoints:
  - GET /
  - POST /
  - PUT /{user_id}
  - DELETE /{user_id}

### router: `warranty.py`
- Tabla/modelo probable: `warranty`
- Endpoints:
  - POST /
  - POST /auto-create/{repair_id}
  - GET /
  - GET /expiring-soon
  - GET /by-repair/{repair_id}
  - GET /check-coverage/{repair_id}
  - GET /{warranty_id}
  - POST /{warranty_id}/void
  - POST /{warranty_id}/claims
  - GET /claims
  - ... y 6 mas

### router: `client.py`
- Tabla/modelo probable: `client`
- Endpoints:
  - GET /dashboard
  - GET /repairs
  - GET /repairs/{repair_id}/timeline
  - GET /repairs/{repair_id}/details
  - GET /profile
  - PUT /profile

### router: `analytics.py`
- Tabla/modelo probable: `analytic`
- Endpoints:
  - GET /dashboard
  - GET /alerts
  - GET /repairs
  - GET /repairs/timeline
  - GET /repairs/export
  - GET /revenue
  - GET /revenue/timeline
  - GET /clients
  - GET /inventory
  - GET /technicians
  - ... y 2 mas

### router: `device.py`
- Tabla/modelo probable: `device`
- Endpoints:
  - GET /
  - GET /{device_id}
  - POST /
  - PUT /{device_id}
  - DELETE /{device_id}

### router: `contact.py`
- Tabla/modelo probable: `contact`
- Endpoints:
  - POST /
  - GET /messages
  - GET /messages/{message_id}

### router: `tools.py`
- Tabla/modelo probable: `tool`
- Endpoints:
  - GET /
  - GET /{tool_id}
  - POST /
  - PUT /{tool_id}
  - DELETE /{tool_id}
  - POST /{tool_id}/calibrate

## Frontend (rutas)
- src/router/index.js
- src/router/index.ts

## Observaciones
- Este mapeo es heuristico. Para precision total, revisar cada router y su modelo real.
- Relacion front/back debe verificarse por consumo real (API calls en componentes).

## Recomendaciones para ejecutar lo faltante
1) Validar consumo real de APIs en frontend
   - Buscar `fetch`/`axios`/`$http` en `src/` y mapear a endpoints reales.
2) Confirmar mapeo router -> modelo
   - Abrir cada router y verificar el modelo importado (ej: `from app.models...`).
3) Probar endpoints criticos con DB real
   - Ejecutar requests a endpoints clave y guardar respuestas JSON como evidencia.
4) Unificar documentacion
   - Mantener un solo reporte vigente y mover historicos a `DOCUMJENTOS_EXTRAS/`.
