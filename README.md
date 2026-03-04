# Cirujano de Sintetizadores

Aplicacion web fullstack para operacion de taller, seguimiento de reparaciones, inventario tecnico, tienda/catalogo y herramientas publicas para clientes.

Este README esta pensado como documento de entrada tecnica del proyecto. Resume lo que existe hoy en el repo, como se conectan frontend y backend, que rutas estan activas y que informacion es razonable dejar publica sin exponer secretos.

## Estado actual

El sistema hoy tiene tres superficies principales:

- `portal publico`: landing, politicas, calculadoras, tienda, cotizador, rutas con token para firma y carga de fotos
- `portal cliente`: dashboard, reparaciones, pagos OT, perfil y seguimiento
- `portal administrador`: inventario, clientes, reparaciones, citas, tickets, compras, manuales, estadisticas y flujos internos

Tambien conviven dos capas tecnicas importantes:

- `frontend SPA` con Vue 3 + Vite + Pinia + Vue Router
- `backend API` con FastAPI + SQLAlchemy

La base local por defecto sigue siendo SQLite, con preparacion para PostgreSQL en despliegues mas formales.

## Stack principal

### Frontend

- Vue 3
- Vite
- Pinia
- Vue Router
- Sass como base visual del sistema
- migracion progresiva a `style scoped` en componentes Vue

### Backend

- FastAPI
- SQLAlchemy
- SQLite por defecto
- soporte para PostgreSQL via `DATABASE_URL`
- CORS, JWT, rate limiting y CSRF configurable

### Testing y calidad

- Vitest
- Playwright
- pytest
- ESLint

## Arquitectura actual

### Frontend

Piezas clave:

- `src/router/index.ts`: mapa de rutas y guards
- `src/stores/auth.ts`: sesion, login, logout, refresh y guardas por rol
- `src/services/api.ts`: cliente Axios con `VITE_API_URL`, cookies, CSRF y compatibilidad legacy con Bearer token
- `src/scss`: sistema Sass base
- `src/vue`: paginas, layouts y componentes principales
- `src/modules`: calculadoras publicas lazy-loaded

### Backend

Piezas clave:

- `backend/app/main.py`: app FastAPI, lifespan, middlewares, CORS, CSRF, health, static y uploads
- `backend/app/api/v1/router.py`: agregador de routers bajo `/api/v1`
- `backend/app/core/config.py`: carga de configuracion y flags de entorno
- `backend/app/core/database.py`: engine SQLAlchemy y compatibilidad SQLite/PostgreSQL
- `backend/app/models`: modelos ORM
- `backend/app/schemas`: contratos Pydantic
- `backend/app/routers` y `backend/app/api/v1/endpoints`: superficie HTTP

### Datos y almacenamiento

- DB local por defecto: `backend/cirujano.db`
- uploads locales: `backend/uploads`
- assets publicos del frontend: `public/`
- dataset tecnico de instrumentos: `src/data/instruments.json` y `src/assets/data/instruments.json`

## Rutas frontend

Referencia principal: `src/router/index.ts`

### Publicas

- `/`
- `/license`
- `/policy`
- `/terminos`
- `/privacidad`
- `/cotizador-ia`
- `/calculadoras`
- `/tienda`
- `/login`
- `/register`
- `/password-reset`
- `/signature/:token`
- `/photo-upload/:token`
- `/calc/555`
- `/calc/resistor-color`
- `/calc/smd-capacitor`
- `/calc/smd-resistor`
- `/calc/ohms-law`
- `/calc/temperature`
- `/calc/number-system`
- `/calc/length`
- `/calc/awg`

### Cliente autenticado

- `/dashboard`
- `/ot-payments`
- `/repairs`
- `/repairs/:id`
- `/profile`
- `/agendar`

### Administracion

- `/admin`
- `/admin/inventory`
- `/admin/inventory/unified`
- `/admin/clients`
- `/admin/repairs`
- `/admin/quotes`
- `/admin/repairs/:id`
- `/admin/categories`
- `/admin/contact`
- `/admin/newsletter`
- `/admin/appointments`
- `/admin/tickets`
- `/admin/purchase-requests`
- `/admin/manuals`
- `/admin/stats`
- `/admin/wizards`
- `/admin/archive`

### Como se protegen

El guard de router hace tres validaciones:

- `requiresAuth`: obliga sesion activa
- `requiresAdmin`: obliga rol admin
- `requiresGuest`: redirige fuera de login/register si ya hay sesion

La hidratacion de sesion pasa por `useAuthStore().checkAuth()` cuando una ruta necesita auth o guest-only.

## API y backend

La superficie HTTP no es una sola capa "pura REST". Hoy conviven:

- endpoints versionados bajo `/api/v1`
- routers de dominio incluidos dentro de `/api/v1`
- endpoints globales fuera de version (`/health`, `/api/health`, `/api/csrf-token`, `/api/logs`, `/uploads`, `/static`)

### Endpoints globales importantes

- `/`: metadatos basicos del servicio
- `/health`: health check principal
- `/api/health`: alias del health check
- `/docs`, `/redoc`, `/openapi.json`: solo si `ENABLE_API_DOCS=true`
- `/api/csrf-token`: bootstrap de CSRF
- `/api/logs`, `/api/metrics`: logging/observabilidad
- `/uploads`: expuesto en dev/test o si `ENABLE_PUBLIC_UPLOADS=true`
- `/static`: assets backend-rendered y email styles

### Grupos de API bajo `/api/v1`

La siguiente lista es un mapa operativo, no una enumeracion exhaustiva endpoint por endpoint:

| Prefijo | Dominio |
| --- | --- |
| `/auth` | login, registro, 2FA, refresh, logout, perfil actual, reset password |
| `/brands` | marcas y modelos por marca |
| `/instruments` | consulta de instrumentos y sus imagenes |
| `/items` | CRUD base de inventario tipo recurso |
| `/inventory` | inventario enriquecido usado por admin y tienda |
| `/categories` | categorias |
| `/users` | usuarios |
| `/repairs` | reparaciones, OTs, fotos, notas, auditoria, componentes |
| `/repair-statuses` | estados de reparacion |
| `/diagnostic` y `/diagnostics` | diagnostico |
| `/quotations` | cotizaciones |
| `/payments` | pagos |
| `/appointments` | citas |
| `/client` y `/clients` | panel y datos orientados a cliente |
| `/devices` | equipos/dispositivos |
| `/purchase-requests` | compras y flujo de pagos asociado |
| `/manuals` | manuales y archivos asociados |
| `/tickets` | tickets |
| `/invoices` | facturacion |
| `/warranties` | garantias |
| `/analytics` y `/stats` | metricas y tableros |
| `/imports` | ejecucion y seguimiento de importaciones |
| `/ai` | servicios de apoyo IA |
| `/search` | busqueda |
| `/uploads` y `/files` | subida/entrega de archivos |
| `/signatures` | flujo de firma por token |
| `/photo-requests` | solicitudes de fotos por token |
| `/newsletter` | newsletter |
| `/contact` | contacto |
| `/instruments-sync` | sync tecnico de instrumentos |

### Seguridad y transporte

Hoy el backend aplica estas capas:

- JWT para autenticacion
- CORS desde `settings.allowed_origins`
- CSRF para mutaciones cuando `ENFORCE_CSRF=true`
- excepcion CSRF para bootstrap auth (`/auth/login`, `/auth/register`, etc.)
- bypass de CSRF clasico cuando la peticion lleva `Authorization: Bearer ...`
- rate limiting con `slowapi`
- headers extra de seguridad en produccion

## Como se conectan frontend y backend

La ruta principal del frontend hacia la API es:

- `VITE_API_URL` -> `src/services/api.ts`

La comunicacion actual funciona asi:

1. `src/services/api.ts` crea una instancia Axios con `baseURL = VITE_API_URL`
2. esa instancia usa `withCredentials=true`
3. si existe meta tag CSRF, agrega `X-CSRF-Token`
4. si existe `access_token` legacy en `localStorage`, agrega `Authorization: Bearer ...`
5. `src/stores/auth.ts` consume `/auth/login`, `/auth/verify-2fa`, `/auth/refresh`, `/auth/me`, `/auth/logout`
6. `src/router/index.ts` protege rutas leyendo `isAuthenticated` e `isAdmin`
7. `backend/app/main.py` resuelve CORS, CSRF, JWT, health y static/uploads

Esto significa que el cliente hoy soporta un modo hibrido:

- compatible con cookies/CSRF
- compatible con token Bearer persistido en `localStorage`

Ese detalle es importante para cualquier cambio futuro en auth.

## Datos, archivos y sincronizaciones

### Inventario y tienda

El repo mantiene una relacion estrecha entre inventario tecnico, catalogo y tienda:

- el frontend admin trabaja sobre `/api/v1/inventory`
- el frontend publico de tienda consume datos de inventario/catalogo
- existen scripts para sincronizacion de catalogo desde imagenes y datasets

### Instrumentos

El sistema tecnico de instrumentos se apoya en:

- `public/images/instrumentos/`
- `src/data/instruments.json`
- `src/assets/data/instruments.json`
- `src/assets/data/brands.json`
- `scripts/sync_instruments.py`
- `scripts/auto_sync.py`
- workflow `.github/workflows/sync-instruments.yml`

Ademas, el backend puede ejecutar auto-sync en startup o por intervalo segun configuracion.

### Uploads y archivos

Rutas y almacenamiento relevantes:

- `backend/uploads`: archivos subidos
- `/uploads`: servido solo en entornos permitidos
- `backend/app/static`: assets estaticos del backend
- `/static`: exposicion de esos assets

## Estado del frontend visual

La base visual sigue apoyada en `src/scss`, pero el proyecto ya esta migrando componentes puntuales a `style scoped`.

Estado actual del corte de migracion ya aplicado:

- `src/scss/_global.scss`: expone custom properties CSS reutilizables
- `src/components/prototypes/InventoryCard.vue`: migrado a `script setup` + `style scoped`
- `src/views/InventoryUnified.vue`: migrado a `script setup` + `style scoped`

El criterio vigente es:

- estilos de sistema y layout general se quedan en Sass global
- estilos especificos de un componente deben migrar a `style scoped`
- no agregar Bootstrap/Tailwind inline en componentes nuevos

## Estructura del repo

Directorios principales:

- `src/`: frontend SPA
- `src/vue/`: paginas, layouts y componentes Vue
- `src/router/`: router frontend
- `src/stores/`: stores Pinia
- `src/services/`: cliente API y servicios frontend
- `src/scss/`: sistema visual base
- `src/modules/`: calculadoras y modulos publicos
- `public/`: assets publicos del frontend
- `backend/app/`: backend FastAPI
- `backend/app/models/`: modelos ORM
- `backend/app/schemas/`: schemas Pydantic
- `backend/app/routers/`: routers de dominio
- `backend/app/api/v1/endpoints/`: endpoints versionados
- `backend/tests/`: tests backend
- `tests/`: tests frontend
- `scripts/`: automatizaciones y sincronizaciones
- `docs/`: documentacion tecnica
- `.github/workflows/`: CI/CD y automatizaciones

## Desarrollo local

### Requisitos

- Node.js
- npm
- Python 3.11+ recomendado

### Frontend

```bash
npm install
npm run dev
```

Frontend local esperado:

- `http://localhost:5173`

### Backend

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
cd backend
uvicorn app.main:app --reload
```

Backend local esperado:

- `http://localhost:8000`

### Health y docs

Si el backend esta arriba:

- `http://localhost:8000/health`
- `http://localhost:8000/api/health`

Si `ENABLE_API_DOCS=true`:

- `http://localhost:8000/docs`
- `http://localhost:8000/redoc`

## Variables de entorno

No se documentan valores reales en este README. Para bootstrap usa solo archivos ejemplo:

- `.env.example`
- `.env.production.example`
- `.env.docker`

En desarrollo, la carga de config del backend prioriza:

1. `backend/.env`
2. `.env` en la raiz del repo

Variables importantes que si es razonable documentar publicamente por nombre:

### Backend

- `ENVIRONMENT`
- `DEBUG`
- `DATABASE_URL`
- `SECRET_KEY`
- `JWT_SECRET`
- `JWT_REFRESH_SECRET`
- `ALLOW_TOKEN_IN_RESPONSE`
- `ENABLE_API_DOCS`
- `ENABLE_PUBLIC_UPLOADS`
- `ENFORCE_CSRF`
- `ALLOWED_ORIGINS` o `CORS_ORIGINS`
- `PUBLIC_BASE_URL`
- `REDIS_URL`
- `TURNSTILE_SECRET_KEY`
- `TURNSTILE_DISABLE`
- `SMTP_*`
- `WHATSAPP_*`
- `ENABLE_INSTRUMENT_AUTO_SYNC`
- `INSTRUMENT_SYNC_ON_STARTUP`
- `INSTRUMENT_SYNC_INTERVAL_MINUTES`

### Frontend

- `VITE_API_URL`
- `VITE_APP_VERSION`
- `VITE_ENVIRONMENT`
- `VITE_TURNSTILE_SITE_KEY`
- `VITE_TURNSTILE_DISABLE`

## Scripts utiles

### Frontend

```bash
npm run dev
npm run build
npm run lint
npm run test
npm run test:coverage
npm run test:e2e
```

### Instrumentos

```bash
npm run sync:instruments
npm run sync:instruments:force
npm run sync:instruments:once
npm run sync:instruments:watch
npm run sync:instruments:auto
```

### Backend

```bash
python -m pytest backend/tests -q
```

## Que informacion se puede dejar "publica"

Esto si es razonable documentar o compartir:

- stack tecnologico
- arquitectura general
- mapa de rutas frontend
- prefijos de API/backend
- flujo general entre SPA, auth store y API
- comandos de desarrollo y build
- nombres de variables de entorno
- ubicacion de carpetas y docs tecnicas
- comportamiento funcional a nivel alto

## Que NO se debe publicar

Esto no debe copiarse a README publico, wiki abierta o material de distribucion:

- valores reales de `.env`, `backend/.env` o cualquier secreto operativo
- JWT secrets, API keys, tokens Turnstile, tokens WhatsApp, SMTP passwords
- dumps de DB o archivos `*.db` reales
- contenido real de `backend/uploads`, `backend/credentials`, backups o logs
- links tokenizados activos de firma o carga de fotos
- datos reales de clientes, reparaciones, pagos o metricas internas
- reportes de auditoria o logs exportados sin sanitizar

## Documentacion adicional recomendada

- `docs/ARCHITECTURE.md`
- `docs/API_DOCUMENTATION.md`
- `docs/DEPLOYMENT.md`
- `docs/SECURITY.md`
- `docs/TESTING.md`
- `docs/TESTING_COVERAGE_MATRIX.md`
- `docs/MODELOS_INVENTORY.md`
- `docs/SYNC_INSTRUMENTS_SYSTEM.md`
- `src/scss/README.md`

## Nota final

Este README busca ser util para onboarding tecnico y publicacion controlada. Si necesitas documentacion mas sensible o mas operativa, conviene separarla en dos capas:

- `README publico-tecnico`: arquitectura, rutas, setup, conceptos y ejemplos
- `runbook interno`: secretos, despliegue real, dominios, accesos, backups, usuarios semilla, credenciales y procedimientos de contingencia
