# Cirujano de Sintetizadores

Repositorio principal del sistema web y operativo de `CDS`.

Este repo concentra el frontend público y administrativo, el backend principal y las piezas de soporte que hoy sostienen la operación del taller, el portal cliente, la agenda, la tienda, inventario, media, cotizaciones y OT.

## Estado actual

Fecha base de este README: `2026-03-20`.

El proyecto ya no está en fase de armar estructura. Está en fase de:

- estabilización funcional,
- cierre operativo del taller,
- consolidación de contratos canónicos,
- salida progresiva de branding duro hacia capas configurables,
- preparación de `CDS` como vertical viva sobre un core reusable.

La guía operativa única del repo es [CDS_UNIFICADO.md](CDS_UNIFICADO.md). Este `README` resume el estado técnico y cómo entrar al proyecto; no reemplaza ese documento.

## Qué es este repo

La arquitectura vigente es un `monolito modular serio`:

- frontend principal en `Vue 3`,
- backend principal en `FastAPI`,
- utilidades y scripts de soporte,
- piezas temporales o satélite separadas del runtime canónico.

La regla de trabajo sigue siendo:

- cambios aditivos antes que destructivos,
- deconstrucción antes que reescritura completa,
- reutilizar capas reales antes de crear otras nuevas,
- no duplicar contratos ni lógica si el repo ya tiene una fuente válida.

## Estructura principal

```text
cirujano-front_CLEAN/
├── CDS_VUE3_ZERO/       frontend Vue 3 principal
├── backend/             API FastAPI y lógica de negocio principal
├── scripts/             utilidades y soporte operativo
├── coming-soon-vue/     landing temporal separada del frontend canónico
├── CDS_UNIFICADO.md     documento rector de trabajo
└── .github/             automatizaciones del repositorio
```

## Qué existe de verdad

Hoy están conectados de forma real:

- home pública,
- cotizador,
- panel administrativo,
- portal cliente,
- agenda pública y admin,
- OT y reparación,
- inventario,
- media,
- tienda,
- `purchase requests`,
- pagos manuales parciales,
- Google Calendar en backend,
- Google Places parcial en frontend.

## Arquitectura viva

### Frontend

`CDS_VUE3_ZERO/` es la aplicación principal.

La dirección actual del frontend es:

- seguir partiendo lógica grande en composables y servicios,
- sacar contenido de negocio desde componentes hacia capas canónicas,
- mantener `mobile first`,
- evitar dashboards paralelos y fachadas visuales sin backend real.

### Backend

`backend/` contiene la API principal y la mayor parte de la lógica operativa.

La dirección actual del backend es:

- consolidar contratos canónicos,
- sacar branding y copy repetido desde servicios hacia una capa única,
- mantener compatibilidad donde todavía exista consumo real,
- no abrir microservicios ni duplicar dominios.

## Estado de consolidación

### Ya asumido como base cerrada

- cotizador canónico bajo `quotation`,
- Cloudinary como contrato runtime real,
- agenda pública y admin conectadas,
- cliente portal base conectado,
- tienda pública conectada a catálogo y `purchase requests`,
- primer gran pase de modularización visual en `ZERO`,
- lifecycle base de Google Calendar.

#### Tronco B — Pago (B0 · B1 · B2 cerrados)

- `B0`: `unit_price` del navegador ya no manda; precio recalculado server-side al crear solicitud.
- `B1`: expiración real por `payment_due_date`, stock insuficiente rechaza con `409`, cliente no puede subir comprobante sin `Payment` solicitado.
- `B2`: `Payment` canonizado como contrato de intento de pago; checkout gateway congela snapshot, webhook sincroniza estado, rechazo no cierra falsamente la solicitud.

La tienda hoy opera como `purchase_request + reserva + comprobante manual`. El checkout online real (pasarela → webhook → conciliación) sigue pendiente en `B3`.

### Frentes todavía abiertos

- pasarela de pago online real (`B3`): Mercado Pago o Flow como primera opción,
- idempotencia fuerte de checkout y scheduler de expiración de reservas,
- cotizador mostrable sin disculpas,
- persistencia canónica de coordenadas,
- foundation real de mapas,
- Google Auth,
- GA4 o retiro de declaración falsa de privacidad (decisión pendiente),
- dashboard cliente como producto móvil fuerte,
- salida completa de hardcodes hacia capas configurables,
- separación clara entre `core reusable`, `domain pack` y `tenant CDS`.

## Auditorías completadas

### Visual / estilos (`2026-03-18`)

Pase de autoridad visual en `ZERO`:

- se cerró mezcla de `scoped shared + local` en componentes base, shells y páginas admin/cliente,
- se eliminaron redefiniciones de `--cds-*` fuera de capa hegemónica,
- métricas del corte: componentes mixtos `22 → 15`, archivos con `color-mix/gradientes` `45 → 25`.

Cuellos de botella residuales: calculadoras individuales (`Timer555`, `Temperature`, `OhmsLaw`) y componentes mixtos del frente público.

### Integraciones Google (`2026-03-20`)

Auditoría completa de Google Suite documentada en `GOOGLE.md`:

- `Google Calendar` integrado con Service Account, funcional, con 3 bugs documentados (duración fija, CALENDAR_ID fuera de settings, timezone duplicado).
- `Google Places / Maps` integrado parcialmente en admin, bloqueado por CSP en producción.
- `GA4` no implementado aunque la política de privacidad lo declara — decisión pendiente.
- `D0` listo para ejecutar: correcciones de Calendar, Maps CSP y Places DOM frágil.

### Componentes Vue huérfanos (`2026-03-20`)

Auditoría completa de 178 archivos `.vue`:

- 6 huérfanos directos: `AboutSection.vue` (no está en el barrel ni en el render), `ui/BaseButton.vue`, `ui/BaseInput.vue` (carpeta `ui/` vestigial), `BaseForm.vue`, `InventoryTable.vue`, `DataTable.vue`.
- 2 huérfanos secundarios: `BaseCard.vue` y `BaseTable.vue` (solo usados por `DataTable.vue`).
- El anchor `#about` del nav apunta a una sección que no se renderiza.
- El resto del árbol de componentes está vivo y conectado.

## Generalización en curso

La hipótesis activa del repo es esta:

`CDS` es la primera vertical viva sobre un `core` configurable.

Eso significa:

- lo reusable debe quedar en capas neutrales,
- lo específico del rubro debe quedar en el domain pack,
- lo propio del taller debe terminar como configuración o contenido del tenant.

### Fase 0 completada

Se cerró el primer bloque de desacople visible en backend email:

- los links públicos ya salen desde `PUBLIC_BASE_URL`,
- el remitente efectivo ya sale desde configuración existente,
- se eliminó el hardcode de `wa.me` fijo en esos templates,
- se agregaron tests dirigidos para blindar ese comportamiento.

### Fase 1 backend iniciada

Ya existe una capa canónica de identidad/copy backend en:

- [backend/app/core/business_config.py](backend/app/core/business_config.py)

Desde ahí ya se alimentan piezas visibles de runtime en:

- `config.py`,
- `main.py`,
- `appointment.py`,
- `google_calendar_service.py`,
- `pdf_generator.py`,
- `quote_management.py`,
- `email_service.py`,
- `repair_write_service.py`.

Esto no termina la generalización, pero sí deja de repartir branding duro en múltiples servicios backend.

## Prioridad vigente

El orden rector hoy es:

1. operación nuclear CDS,
2. pago seguro y confianza transaccional,
3. cotizador digno,
4. Google fundacional con base real,
5. definición de producto vendible.

Lo visual, growth, `NEO`, tipografía y SEO pueden correr en paralelo sólo si no rompen esa serie.

## Qué viene después

Los siguientes bloques correctos son:

- elegir pasarela y ejecutar `B3` (Mercado Pago como camino más rápido),
- correr en paralelo `D0` Google base (Calendar bugs + CSP Maps + Places DOM),
- resolver decisión `D2` sobre GA4 vs retiro de declaración de privacidad,
- cerrar `Fase 1` backend completa (G),
- abrir `Fase 1` frontend con capa canónica de negocio y contenido (G),
- sacar `footer`, `contact`, `home`, legal y copy comercial desde componentes inline,
- introducir feature flags reales para módulos opcionales,
- resolver `OT_PREFIX` como decisión de config más compatibilidad/migración,
- seguir separando `CDS tenant` de `core reusable` sin romper operación real.

## Desarrollo local

### Frontend

```bash
cd CDS_VUE3_ZERO
npm install
npm run dev
```

Build:

```bash
cd CDS_VUE3_ZERO
npm run build
```

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

## Variables de entorno

Las bases de configuración están en:

- [.env.example](.env.example)
- [backend/.env.example](backend/.env.example)

Puntos relevantes hoy:

- `PUBLIC_BASE_URL`
- `FROM_EMAIL`
- `SMTP_FROM_EMAIL`
- `SENDGRID_FROM_EMAIL`
- `GOOGLE_CALENDAR_CREDENTIALS_FILE`
- `GOOGLE_CALENDAR_ID`
- `WHATSAPP_*`
- `ENABLE_INSTRUMENT_AUTO_SYNC`
- `INSTRUMENT_SYNC_ON_STARTUP`
- `INSTRUMENT_SYNC_INTERVAL_MINUTES`
- `VITE_GOOGLE_MAPS_API_KEY`

## Validación

### Frontend

Validación mínima:

```bash
cd CDS_VUE3_ZERO
npm run build
```

### Backend

Base general:

```bash
cd backend
pytest tests/ --verbose
```

Cuando el corte es temático, se prefieren corridas focalizadas sobre lo realmente tocado.

Ejemplos reales usados en este repo:

```bash
pytest tests/test_email_service.py -q
pytest tests/test_business_config.py tests/test_quote_routes.py tests/test_health.py -q
```

## Documentación viva

### Documento rector

- [CDS_UNIFICADO.md](CDS_UNIFICADO.md)

### Documentos históricos

Se mantienen como contexto, no como backlog vivo principal:

- `NEGO_GANT.md`
- `NEGO_CHECKLIST.md`
- `CDS_GANT.md`
- `ESTADO.md`
- `NEO_DASH.md`
- `LETRAS.md`
- `COMPRAS.md`
- `gant.md`
- `dash.md`
- `APIREST.md`

## Seguridad

Este `README` no debe contener:

- credenciales,
- tokens,
- passwords,
- correos privados,
- rutas locales sensibles,
- configuraciones productivas sensibles,
- datos de clientes.

La configuración sensible debe resolverse por variables de entorno y canales internos controlados.
