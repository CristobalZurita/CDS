# ESTADO

## Propósito

Documento de auditoría viva del repo para:

- mapear cómo se conecta `CDS_VUE3_ZERO` con `backend`,
- verificar si los endpoints usados por el frontend existen realmente,
- revisar componentes dinámicos y composables relevantes,
- revisar routers, servicios, modelos y scripts del backend,
- dejar constancia de hallazgos reales con base en lectura de archivos.

## Alcance de esta auditoría

Se audita el repo actual en:

- `CDS_VUE3_ZERO/`
- `backend/`
- scripts y workflows que afecten conexión front-back

Se excluye como fuente de verdad funcional:

- `RESTO/`
- histórico legado `L`

## Método

- lectura directa de archivos importantes completos,
- contraste entre rutas Vue, llamadas API y routers FastAPI,
- verificación local con build/tests/probes cuando sea viable,
- documentación incremental para liberar contexto durante la revisión.

## Estado de avance

- En curso.

## Observaciones iniciales

- El worktree no está limpio. Al momento de esta auditoría había cambios locales en:
  - `README.md`
  - `backend/app/routers/payment_gateway.py`
  - varios tests de backend
  - archivos nuevos sin trackear como `CDS_VUE3_ZERO/LECTURA.md`, `backend/smoke_flow.py`, `backend/tools/`
- Esta auditoría no toma esos cambios como verdad funcional por sí mismos; se usa el estado del repo leído en disco.

## Entry Points Reales

### Frontend ZERO

Fuente leída completa:

- `CDS_VUE3_ZERO/src/main.js`
- `CDS_VUE3_ZERO/src/router/index.js`
- `CDS_VUE3_ZERO/src/router/routes/public.js`
- `CDS_VUE3_ZERO/src/services/api.js`

Conclusión:

- El frontend `Z` arranca en `src/main.js`.
- Monta `Pinia`, `Vue Router` y `VueApexCharts`.
- El router usa `createWebHistory`.
- La hidratación de sesión ocurre en `beforeEach` sólo si la ruta depende de sesión.
- El cliente HTTP base es `src/services/api.js`.
- `VITE_API_URL` define el backend; si no existe, usa `'/api/v1'`.

### Backend

Fuente leída completa:

- `backend/app/main.py`
- `backend/app/api/v1/router.py`

Conclusión:

- El backend arranca en `backend/app/main.py`.
- La app FastAPI monta:
  - `api_router` bajo `/api/v1`
  - router CSRF fuera de `/api/v1`
  - router de logging fuera de `/api/v1`
  - `StaticFiles` para `/uploads` y `/static` según entorno
- El router agregador `backend/app/api/v1/router.py` es hoy la pieza central de integración.
- Ese agregador mezcla:
  - imports explícitos estables (`auth`, `brands`, `inventory`, `imports`, `stats`, `ai`, `users`)
  - imports defensivos/dinámicos con `try/except`
  - una segunda pasada de `importlib.import_module(...)`
- El patrón es funcional, pero la capa de registro no está del todo estabilizada.

## Estado Arquitectónico Inicial

- `Z` está organizado por rutas, layouts, páginas, composables, stores y servicios.
- El backend está organizado por `routers`, `services`, `models`, `schemas`, `crud`, `repositories`.
- La conexión principal es:

```text
CDS_VUE3_ZERO
  -> src/services/api.js
  -> /api/v1
  -> backend/app/api/v1/router.py
  -> routers FastAPI
  -> services/models/db
```

- El frontend público usa un `MasterLayout` único para home, páginas públicas, footer, navegación, carrito y acciones flotantes.
- El backend expone una gran superficie de routers bajo `/api/v1`, varios de ellos todavía con lógica de negocio adentro del propio router.

## Cruce Frontend -> Backend

### Método

- Se extrajeron llamadas `api.get/post/put/patch/delete(...)` desde `CDS_VUE3_ZERO/src`.
- Se enumeraron rutas realmente registradas por FastAPI importando `app.main`.
- Se normalizaron segmentos dinámicos (`${...}` / `{...}`) y barras finales para comparar.

### Resultado general

- Llamadas frontend con match de ruta registrada: `157`
- Mismatches literales detectados: `3`

### Mismatches literales reales

Todos están en `CDS_VUE3_ZERO/src/services/api.js`:

- `POST /auth/2fa/verify`
  - frontend usa: `/auth/2fa/verify`
  - backend expone: `/api/v1/auth/verify-2fa`
- `POST /auth/password-reset/request`
  - frontend usa: `/auth/password-reset/request`
  - backend expone: `/api/v1/auth/forgot-password`
- `POST /auth/password-reset/confirm`
  - frontend usa: `/auth/password-reset/confirm`
  - backend expone: `/api/v1/auth/reset-password`

### Lectura técnica de esos mismatches

Fuente leída completa:

- `backend/app/api/v1/endpoints/auth.py`
- `CDS_VUE3_ZERO/src/services/api.js`
- `CDS_VUE3_ZERO/src/stores/auth.js`

Conclusión:

- El store de auth del frontend está conectado a helpers de `services/api.js`.
- El login y `auth/me` sí coinciden con backend.
- Los flujos de 2FA y password reset no coinciden por nombre de endpoint.
- Eso significa que la autenticación base funciona mejor que los flujos secundarios.

## Contratos que requieren atención

### Contacto público

Fuente leída completa:

- `CDS_VUE3_ZERO/src/components/home/ContactSection.vue`
- `backend/app/routers/contact.py`

Hallazgo:

- El frontend envía:
  - `name`
  - `email`
  - `subject`
  - `message`
- El backend exige además `turnstile_token` válido.
- El formulario público de contacto no monta `TurnstileWidget` ni envía captcha.

Veredicto:

- El endpoint existe.
- La conexión existe.
- El contrato funcional no coincide.
- El formulario de contacto público puede fallar en runtime con `400 Captcha inválido` fuera de entornos donde se omita Turnstile.

### Leads públicos del cotizador

Fuente leída completa:

- `CDS_VUE3_ZERO/src/composables/useCotizadorIAPage.js`
- `backend/app/routers/leads.py`

Hallazgo:

- El frontend sí envía `turnstile_token`.
- El backend sí valida captcha y persiste el lead.
- El contrato de creación de leads está alineado.

Veredicto:

- Conexión correcta.

### Media bindings dinámicos

Fuente leída completa:

- `CDS_VUE3_ZERO/src/composables/useMediaBinding.js`
- `CDS_VUE3_ZERO/src/composables/useCloudinary.ts`
- `backend/app/routers/media.py`

Hallazgo:

- El frontend carga `/media/bindings` una sola vez a nivel de módulo.
- Si falla, hace fallback al mapping local de imágenes.
- El backend expone:
  - `GET /media/bindings`
  - `PUT /media/bindings/{slot}`
  - `DELETE /media/bindings/{slot}`
  - gestión de assets en `/media/assets`

Veredicto:

- El sistema dinámico de media sí existe y sí está conectado.
- Es un punto real de dinamismo del frontend, no un placeholder.
- El fallback local reduce riesgo de caída visual, pero también puede ocultar problemas de sincronización.

### Uploads

Fuente leída completa:

- `CDS_VUE3_ZERO/src/services/uploadService.js`
- `backend/app/routers/uploads.py` (pendiente lectura completa en detalle posterior)

Hallazgo inicial:

- El frontend intenta primero firma para Cloudinary (`/uploads/signature`) y luego upload directo a Cloudinary.
- Si falla, usa fallback a `/uploads/images`.

Veredicto inicial:

- La estrategia de upload es dual y coherente.
- Falta revisar completo el router backend para confirmar que el contrato exacto y los destinos sigan alineados tras la salida de `L`.

## Workflows y Scripts Operativos

### Estado real del repo en disco

Fuente leída completa:

- `CDS_VUE3_ZERO/package.json`
- `.github/workflows/ci.yml`
- `.github/workflows/tests.yml`
- `.github/workflows/deploy.yml`
- `.github/workflows/security.yml`
- `.github/workflows/secret-scan.yml`
- `.github/workflows/sync-instruments.yml`
- `scripts/run_tests.sh`
- `scripts/check_env.py`
- `scripts/security-check.sh`
- `scripts/e2e/start_backend.py`

Hallazgo base:

- En el estado actual del repo ya no existe `package.json` en raíz.
- El único `package.json` operativo del frontend está en `CDS_VUE3_ZERO/`.

### CI / tests

Hallazgos:

- `ci.yml` y `tests.yml` ya usan `working-directory: CDS_VUE3_ZERO` para el bloque frontend.
- Eso sí es coherente con el frontend `Z`.
- Pero ambos workflows siguen invocando scripts que `CDS_VUE3_ZERO/package.json` no declara:
  - `npm run lint`
  - `npm run test -- --run`
  - `npm run test:coverage`
  - `npm run test:integration`
- `CDS_VUE3_ZERO/package.json` solo declara:
  - `dev`
  - `build`
  - `preview`
  - `test:e2e`
  - `test:e2e:ui`
  - `test:e2e:headed`
  - `test:e2e:debug`
  - `test:report`

Veredicto:

- La intención de CI ya está migrada hacia `Z`.
- La definición de scripts npm todavía no coincide con lo que CI cree que existe.
- En el estado actual esos jobs frontend no son confiables tal como están escritos.

### Deploy / security

Hallazgos:

- `deploy.yml` sigue haciendo `npm ci` y `npm run build` en raíz.
- `security.yml` también hace `npm ci` en raíz.
- Eso ya no coincide con la estructura actual del repo.

Veredicto:

- `deploy.yml` y `security.yml` quedaron desalineados respecto al frontend `Z`.
- Son residuos operativos de una topología previa del repo.

### Sync de instrumentos

Hallazgos:

- `sync-instruments.yml` declara en comentarios que la estructura legacy fue movida a `RESTO`.
- Sin embargo el workflow sigue buscando:
  - `public/images/instrumentos`
  - `src/data/instruments.json`
  - `src/assets/data/instruments.json`
  - `src/assets/data/brands.json`
- `scripts/sync_instruments.py` y `scripts/validate_instruments_sync.py` siguen modelados sobre esa misma estructura legacy.
- `backend/app/services/instrument_sync_service.py` todavía apunta a:
  - `src/data/instruments.json`
  - `src/data/.sync_metadata.json`

Veredicto:

- El comentario del workflow dice una cosa, pero la implementación sigue acoplada al layout legacy.
- La sincronización de instrumentos no está emancipada del todo.

### Scripts locales

Hallazgos:

- `scripts/run_tests.sh` levanta backend local y luego ejecuta `npm run test:e2e` desde la raíz del repo.
- Como en raíz ya no existe `package.json`, ese script no corresponde al estado actual.
- `scripts/check_env.py` sí es coherente y autónomo; valida secretos productivos básicos.
- `scripts/security-check.sh` mezcla checks razonables con supuestos parciales:
  - audita `CDS_VUE3_ZERO` para npm,
  - pero sigue siendo un script manual más que una fuente de verdad del pipeline.
- `scripts/e2e/start_backend.py` sí está alineado con el repo actual:
  - prepara runtime aislado para backend,
  - usa DB `backend/tests/e2e_runtime/e2e_cirujano.db`,
  - y expone `ALLOWED_ORIGINS` para Playwright.

Veredicto:

- Hay una mezcla de scripts ya migrados a `Z/backend` y scripts todavía escritos como si existiera frontend raíz operativo.

## Flujos Frontend Admin y Portal Cliente

### Clientes / dispositivos / reparaciones rápidas

Fuente leída completa:

- `CDS_VUE3_ZERO/src/composables/useClientsPage.js`
- `CDS_VUE3_ZERO/src/composables/useClientManagement.js`
- `CDS_VUE3_ZERO/src/composables/useDeviceManagement.js`
- `CDS_VUE3_ZERO/src/composables/useRepairManagement.js`
- `backend/app/routers/clients.py`
- `backend/app/routers/device.py`
- `backend/app/routers/repair.py`
- `backend/app/services/repair_write_service.py`

Hallazgos:

- El flujo admin de clientes está realmente conectado a:
  - `GET/POST/PUT/DELETE /clients`
  - `GET /clients/{id}/devices`
  - `GET /clients/{id}/repairs`
  - `POST /devices/`
  - `POST /repairs/`
- `useClientsPage` no contiene la lógica; la delega en tres composables separados.
- `clients.py` sí expone `GET /clients/code/next`.
- `repair.py` sí expone `GET /repairs/next-code`, pero requiere `client_id`.

Matiz importante:

- `useIntakeWizard.js` llama `fetchNextOtCode()` sin `client_id` al inicializar.
- El backend exige `client_id`.
- El frontend captura el error y cae al placeholder `'OT-001'`.

Veredicto:

- El flujo CRUD base de clientes/dispositivos/reparaciones está conectado y es real.
- El “próximo código OT” no está realmente resuelto al cargar el wizard sin cliente seleccionado; la UI muestra fallback, no código backend real.

### Intake wizard

Fuente leída completa:

- `CDS_VUE3_ZERO/src/composables/useIntakeWizard.js`
- `backend/app/routers/repair.py`
- `backend/app/routers/device.py`
- `backend/app/routers/clients.py`
- `backend/app/routers/uploads.py`

Hallazgos:

- El wizard crea la cadena real:
  - cliente,
  - device,
  - repair,
  - intake sheet,
  - materiales,
  - fotos.
- Endpoints usados y existentes:
  - `POST /clients/`
  - `POST /devices/`
  - `POST /repairs/`
  - `POST /repairs/{id}/intake-sheet`
  - `POST /repairs/{id}/components`
  - `POST /repairs/{id}/photos`
  - `GET /inventory/`
- `repair_write_service.py` acepta payload libre y no rompe por campos extra como `warranty_days`; esos campos simplemente no participan en la escritura si el modelo no los usa.

Veredicto:

- El intake wizard no es un placeholder.
- La secuencia principal sí existe backend-side.
- El punto más débil ahí no es conectividad sino robustez de UX y algunos fallbacks.

### Reparación detalle admin

Fuente leída completa:

- `CDS_VUE3_ZERO/src/composables/useRepairDetailAdminPage.js`
- `CDS_VUE3_ZERO/src/pages/admin/RepairDetailAdminPage.vue`
- `backend/app/routers/repair.py`

Hallazgos:

- La pantalla usa endpoints reales y existentes para:
  - detalle de OT,
  - cambio de estado,
  - edición técnica,
  - notas,
  - fotos,
  - PDF de cierre,
  - archivado/reactivación,
  - notificación al cliente,
  - solicitud de firma,
  - solicitud de foto de cliente.
- `repair.py` sí implementa:
  - `GET /repairs/{id}`
  - `PUT /repairs/{id}`
  - `POST /repairs/{id}/archive`
  - `POST /repairs/{id}/reactivate`
  - `POST /repairs/{id}/notify`
  - `GET /repairs/{id}/closure-pdf`
  - `GET/POST /repairs/{id}/notes`
  - `GET/POST /repairs/{id}/photos`

Veredicto:

- La página de detalle admin está bien conectada con el backend y sus acciones principales son reales.

### Tickets

Fuente leída completa:

- `CDS_VUE3_ZERO/src/composables/useTicketsPage.js`
- `backend/app/routers/tickets.py`

Hallazgos:

- El frontend usa:
  - `GET /tickets/`
  - `POST /tickets/`
  - `PATCH /tickets/{id}?status=...`
  - `DELETE /tickets/{id}`
  - `POST /tickets/{id}/messages`
- El backend expone exactamente esas rutas.

Veredicto:

- El módulo de tickets sí está conectado y su contrato coincide.

### Solicitudes de compra y pagos OT cliente

Fuente leída completa:

- `CDS_VUE3_ZERO/src/composables/usePurchaseRequestsPage.js`
- `CDS_VUE3_ZERO/src/composables/useOtPaymentsPage.js`
- `backend/app/routers/purchase_requests.py`
- `backend/app/routers/client.py`
- `backend/app/routers/client_portal.py`
- `backend/app/routers/payments.py`
- `backend/app/routers/payment_gateway.py`
- `backend/app/services/payment_gateway_service.py`

Hallazgos:

- `purchase_requests.py` implementa realmente:
  - tablero `/purchase-requests/board`
  - creación `/purchase-requests/`
  - `request-payment`
  - `confirm-payment`
  - actualización de estado
  - borrado
- El backend además gestiona reserva/liberación/consumo de stock según estado de la solicitud.
- `client.py` y `client_portal.py` son idénticos por contenido.
- El portal cliente sí implementa:
  - `GET /client/purchase-requests`
  - `POST /client/store/purchase-requests`
  - `POST /client/purchase-requests/{id}/deposit-proof`
- `useOtPaymentsPage.js` está alineado con ese contrato.
- `payments.py` y `payment_gateway.py` existen y son reales.
- `payment_gateway_service.py` sí implementa integración real con Transbank/MercadoPago, condicionada a entorno.

Matiz importante:

- La seguridad del portal cliente depende de `require_permission("repairs", "read")`, no de una política específicamente separada para portal cliente.
- Es funcional, pero conceptualmente mezcla permisos de taller con permisos de cliente.

Veredicto:

- El flujo de solicitudes de compra y comprobante de depósito es real y está conectado.
- La capa de permisos del portal está menos refinada que el flujo funcional.

## Residuos y Duplicaciones Reales

### Routers duplicados

Hallazgos:

- `backend/app/routers/client.py` y `backend/app/routers/client_portal.py` son idénticos byte a byte.

Veredicto:

- No es herencia conceptual: es duplicación literal.
- Ahí hay deuda clara de consolidación.

### Endpoints v1 con rutas legacy

Fuente leída completa:

- `backend/app/api/v1/endpoints/instruments.py`
- `backend/app/api/v1/endpoints/brands.py`

Hallazgos:

- `instruments.py` sigue leyendo `src/data/instruments.json`.
- `brands.py` sigue leyendo `src/assets/data/*.json`.
- Ambas rutas apuntan a estructuras que ya no son fuente de verdad del repo actual `Z`.

Veredicto:

- Existen endpoints registrados que hoy dependen de layout legacy o de archivos que ya no son canónicos.
- Son candidatos claros a rotura silenciosa o a cleanup estructural.

### Media / Cloudinary / sync

Fuente leída completa:

- `backend/app/routers/uploads.py`
- `backend/app/services/cloudinary_service.py`
- `backend/app/services/instrument_sync_service.py`

Hallazgos:

- `uploads.py` ya trabaja sobre `uploads/images/...` y no sobre `public/images/...`.
- Eso sí está más alineado con el repo actual.
- Pero `cloudinary_service.py` todavía reconoce destinos legacy como:
  - `public/images/instrumentos`
  - `public/images/INVENTARIO`
- `instrument_sync_service.py` sigue dependiendo de `src/data/...`.

Veredicto:

- La capa de uploads mejoró.
- La capa de sincronización/media todavía arrastra dependencias de la estructura anterior.

## Observaciones Técnicas Adicionales

- `RepairRepository.list_active()` y `list_archived()` no aplican orden ni paginación.
- El frontend admin solicita a veces `/repairs/?limit=10&sort=-created_at`, pero `repair.py` no consume esos parámetros.
- Eso significa que ciertas vistas “recientes” del dashboard no están realmente gobernadas por los parámetros que envía el frontend; dependen del orden natural de la consulta backend.

## Módulos Públicos y Portal Cliente

### Dashboard / perfil / detalle OT cliente

Fuente leída completa:

- `CDS_VUE3_ZERO/src/composables/useDashboardPage.js`
- `CDS_VUE3_ZERO/src/composables/useRepairDetailPage.js`
- `CDS_VUE3_ZERO/src/composables/useProfilePage.js`
- `backend/app/routers/client.py`

Hallazgos:

- `DashboardPage` usa `GET /client/dashboard` y el backend sí lo implementa.
- `RepairDetailPage` usa:
  - `GET /client/repairs/{id}/details`
  - `GET /client/repairs/{id}/closure-pdf`
  y ambos existen.
- `ProfilePage` sí usa:
  - `GET /client/profile`
  - `PUT /client/profile`
  y ambos existen.

Pero:

- El propio composable `useProfilePage.js` marca explícitamente como pendientes de integración backend:
  - cambio de contraseña,
  - eliminación de cuenta.
- Esas acciones hoy muestran éxito local de UI, pero no ejecutan backend real.

Veredicto:

- Dashboard, perfil base y detalle de OT del cliente son flujos reales.
- Algunas acciones del perfil todavía son placeholders visibles, no integración terminada.

### Tienda / carrito

Fuente leída completa:

- `CDS_VUE3_ZERO/src/composables/useStorePage.js`
- `CDS_VUE3_ZERO/src/stores/shopCart.js`
- `backend/app/routers/inventory.py`
- `backend/app/routers/client.py`

Hallazgos:

- La tienda carga catálogo real desde backend:
  - con sesión: `GET /inventory/`
  - sin sesión: `GET /inventory/public/`
- Si backend falla, el front cae a caché local en `localStorage`.
- El checkout usa `POST /client/store/purchase-requests`.
- Ese endpoint existe y crea solicitud de compra real.
- `inventory.py` sí expone:
  - catálogo interno `/inventory/`
  - catálogo público `/inventory/public/`
  - alertas `/inventory/alerts/summary`
  - CRUD admin `/inventory/{id}`

Veredicto:

- La tienda pública no es demo estática.
- Usa catálogo real y tiene fallback local explícito.
- El fallback mejora resiliencia, pero también puede ocultar desalineaciones entre catálogo backend y vista pública.

## Cotizaciones y Diagnóstico

### Quotes admin

Fuente leída completa:

- `CDS_VUE3_ZERO/src/composables/useQuotesAdminPage.js`
- `backend/app/routers/diagnostic.py`
- `backend/app/services/quote_management.py`

Hallazgos:

- El frontend de cotizaciones usa:
  - `/diagnostic/quotes/board`
  - `/diagnostic/quotes`
  - `/diagnostic/quotes/{id}/send`
  - `/diagnostic/quotes/{id}/status`
  - `DELETE /diagnostic/quotes/{id}`
- El backend sí implementa esas rutas.
- `quote_management.py` concentra helpers reales para:
  - normalización de estado,
  - transición permitida,
  - ítems,
  - destinatarios,
  - cálculo de totales.
- Desde el panel de quotes se puede crear OT y el backend lo soporta vía `POST /repairs/`.

Veredicto:

- El módulo de cotizaciones admin sí es real y tiene capa de dominio mínima razonable.

### Diagnóstico / cotizador

Fuente leída completa:

- `CDS_VUE3_ZERO/src/composables/useCotizadorIAPage.js`
- `backend/app/routers/diagnostic.py`
- `backend/app/api/v1/endpoints/ai.py`
- `backend/app/services/ai_detector.py`
- `backend/app/services/image_analysis.py`

Hallazgos:

- El router `diagnostic.py` sí implementa lógica real para:
  - marcas,
  - modelos,
  - fallas aplicables,
  - cálculo de presupuesto basado en datos estáticos y multiplicadores.
- El endpoint de IA puro (`/ai/analyze`) es solo un placeholder.
- `ai_detector.py` delega a `image_analysis.py`.
- `image_analysis.py` devuelve:
  - `status: "pending"`
  - `summary: "no-analysis-performed"`
  - `detected: {}`

Veredicto:

- El cotizador no está “vacío”, pero su inteligencia actual no viene de IA.
- La parte real hoy es:
  - reglas,
  - datasets,
  - multiplicadores,
  - clasificación manual/estática.
- La parte `AI` del repo sigue siendo un punto de extensión, no una capacidad desplegada.

## Instrumentos y Manuales

Fuente leída completa:

- `CDS_VUE3_ZERO/src/composables/useManualsPage.js`
- `backend/app/routers/manuals.py`
- `backend/app/routers/instrument.py`
- `backend/app/api/v1/endpoints/instruments.py`

Hallazgos:

- `ManualsPage` usa:
  - `GET /instruments/`
  - `GET/POST/PATCH/DELETE /manuals`
- `manuals.py` sí expone ese CRUD y valida que el instrumento exista.
- `instrument.py` mezcla dos fuentes:
  - `GET /instruments/` lista desde la tabla DB `Instrument`
  - `GET /instruments/{instrument_id}` y `/image` leen JSON en `src/data/instruments.json`
- `api/v1/endpoints/instruments.py` repite esa misma dependencia a `src/data/instruments.json`.

Veredicto:

- El módulo de manuales funciona sobre instrumentos de DB.
- El módulo de instrumentos, en cambio, sigue híbrido:
  - lista desde DB,
  - detalle/imágenes desde JSON legacy.

## Estado de Conectividad Actual

### Cruce automático frontend -> backend

Verificación local actual:

- Se volvió a importar `app.main` y se compararon rutas registradas contra llamadas `api.*(...)` del frontend.
- Normalizando parámetros dinámicos, el resultado actual fue:
  - `114` rutas frontend únicas con match backend
  - `3` mismatches reales

Mismatches confirmados:

- `POST /auth/2fa/verify`
- `POST /auth/password-reset/request`
- `POST /auth/password-reset/confirm`

Veredicto:

- El acoplamiento general frontend-backend es alto.
- El desajuste literal actual sigue concentrado en auth secundaria (2FA y reset de password).

## Verificación Runtime en esta sesión

### Frontend

Comando validado:

- `npm run build` en `CDS_VUE3_ZERO`

Resultado:

- Build OK.
- Se cargó `image-mapping` con `449` imágenes.
- Vite advirtió chunks grandes:
  - `apexcharts...js` ~ `518 kB`
  - `index...js` ~ `697 kB`

Lectura:

- El frontend compila, pero el bundle principal sigue pesado.

### Backend

Comando validado:

- `../venv/bin/pytest tests/test_health.py tests/test_auth_client_flow.py tests/test_client_portal_router.py tests/test_purchase_request_stock_flow.py tests/test_uploads.py tests/test_payment_gateway.py -q`

Resultado:

- `20 passed`
- `2 skipped`
- warnings deprecadas por uso extendido de `datetime.utcnow()`

Cobertura factual de esa tanda:

- health
- auth base y flujo cliente
- portal cliente
- solicitudes de compra con stock
- uploads
- payment gateway

Veredicto:

- Los flujos críticos auditados sí tienen evidencia de ejecución local.
- El principal ruido runtime actual no son fallos funcionales en esos módulos, sino deuda técnica por `datetime.utcnow()` y deuda estructural en scripts/workflows.

### Segunda tanda de tests backend

Comando validado:

- `../venv/bin/pytest tests/test_appointments.py tests/test_categories_router.py tests/test_items_api.py tests/test_inventory_store_catalog_sync.py tests/test_api_router_dedupe.py -q`

Resultado:

- `30 passed`
- `1 skipped`

Cobertura factual adicional:

- appointments
- categories router
- items API
- sincronización catálogo tienda / inventario
- dedupe del router API

Veredicto:

- La evidencia de ejecución local cubre ya tanto flujos públicos/cliente como módulos administrativos y consistencia del router.

## CRUD Admin Medianos

Fuente leída completa:

- `CDS_VUE3_ZERO/src/composables/useAppointmentsPage.js`
- `CDS_VUE3_ZERO/src/composables/useLeadsAdminPage.js`
- `CDS_VUE3_ZERO/src/composables/useContactMessagesPage.js`
- `CDS_VUE3_ZERO/src/composables/useNewsletterSubscriptionsPage.js`
- `CDS_VUE3_ZERO/src/composables/useUsers.js`
- `backend/app/routers/appointment.py`
- `backend/app/routers/leads.py`
- `backend/app/routers/contact.py`
- `backend/app/routers/newsletter.py`
- `backend/app/api/v1/endpoints/users.py`

Hallazgos:

- Appointments:
  - frontend admin usa `GET/PATCH/DELETE /appointments`
  - backend sí los implementa
  - el endpoint público de creación sí exige Turnstile y además lanza mail + sync Google Calendar en background
- Leads admin:
  - frontend usa `GET /leads` y `PATCH /leads/{id}/status`
  - backend sí los implementa
- Contact messages admin:
  - frontend sólo lista `GET /contact/messages`
  - backend sí lo expone
- Newsletter admin:
  - frontend sólo lista `GET /newsletter/subscriptions`
  - backend sí lo expone
- Users:
  - frontend usa `GET/POST/PUT/DELETE /users`
  - backend `users.py` sí expone ese CRUD

Veredicto:

- Estos módulos medianos están funcionalmente conectados y no muestran gaps graves de contrato.
- La excepción relevante sigue siendo el formulario público de contacto, no el backoffice de mensajes.

## Diagnóstico Final

### Estado general

- `CDS_VUE3_ZERO` y `backend` están efectivamente conectados y la mayor parte de los flujos importantes son reales.
- No se observa un frontend “maquillado” sobre endpoints inexistentes.
- La base actual del sistema es operativa como monolito modular `Z + backend`.

### Dónde está la deuda principal

1. Auth secundaria:
   - 2FA y password reset tienen mismatch literal de rutas.
2. Contacto público:
   - el frontend no cumple el contrato Turnstile del backend.
3. Scripts / CI / deploy:
   - varias automatizaciones siguen escritas para una topología previa del repo.
4. Instrumentos / media:
   - persisten rutas y scripts híbridos o legacy (`src/data`, `src/assets/data`, sync antiguo).
5. Duplicación backend:
   - `client.py` y `client_portal.py` están duplicados literalmente.
6. Placeholders visibles:
   - AI real no desplegada,
   - acciones de perfil cliente aún simuladas en UI.

### Qué sí está sólido

- build del frontend `Z`
- CRUD admin principales
- portal cliente base
- solicitudes de compra y flujo de depósito
- catálogo/tienda con backend real
- uploads
- payment gateway base
- appointments
- analytics/reporting como capa real, no mock

### Prioridad de corrección sugerida

1. Corregir rutas auth del frontend.
2. Añadir Turnstile al formulario público de contacto.
3. Reescribir workflows/scripts para que asuman solo `CDS_VUE3_ZERO` como frontend.
4. Consolidar fuente de verdad de instrumentos/media y retirar dependencias legacy.
5. Unificar `client.py` y `client_portal.py`.
6. Convertir placeholders visibles restantes en flujos reales o marcarlos explícitamente como no disponibles.

### Conclusión

- El repo no está “roto por dentro”.
- Sí está en una etapa híbrida donde la aplicación principal ya es `Z`, pero la infraestructura auxiliar y algunos endpoints todavía arrastran supuestos del estado anterior.
- La deuda más importante hoy no es de inexistencia funcional; es de coherencia estructural, contratos secundarios y limpieza operativa.
