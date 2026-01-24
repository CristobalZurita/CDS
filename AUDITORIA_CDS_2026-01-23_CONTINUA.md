# AUDITORIA CDS - CONTINUACION
**Fecha:** 2026-01-23
**Principio:** ADITIVO, NO DESTRUCTIVO

---

## 1) Mapa endpoints vs UI (cruce real)
**Resultado:** no se detectan endpoints consumidos por UI que no existan en backend.
**Nota:** el scanner detectó 1 falso positivo (`/imports/run`) por comillas simples en el router; el endpoint sí existe.

**Riesgo:** hay múltiples routers con prefijos cercanos (legacy `app/routers` y `api/v1/endpoints`).
- `api/v1/endpoints/*` y `app/routers/*` conviven. Esto crea duplicidad y confusión de permisos.
- Ejemplo: `/api/v1/items` (router POC de Excel) expuesto sin auth en lectura, mientras que `/api/v1/inventory` usa permisos.

---

## 2) Endpoints potencialmente rotos / inconsistentes
- **/api/v1/items**: endpoints POC de Excel (`backend/app/api/v1/endpoints/inventory.py`) quedan públicos y no son usados por UI. Riesgo de exposición innecesaria.
- **/api/v1/stats**: público con `get_optional_user`, devuelve contadores internos. Si no es deseado, restringir.
- **/api/v1/diagnostic** y **/api/v1/quotation**: expuestos sin rate limit (posible abuso o scraping).
- **/api/v1/contact**, **/api/v1/newsletter**, **/api/v1/appointments**, **/api/v1/photo-requests/submit**: públicos sin rate limit ni captcha.

---

## 3) Ciberseguridad (hallazgos)
**Exposición pública:**
- `backend/app/api/v1/endpoints/inventory.py` (prefijo `/items`) expone catálogo POC y lectura sin auth.
- `backend/app/api/v1/endpoints/stats.py` expone contadores públicos (users/clients/repairs/products).
- `backend/app/routers/uploads.py` permite upload público (con rate limit) sin auth.
- `backend/app/routers/diagnostic.py`, `backend/app/routers/quotation.py`, `backend/app/api/v1/endpoints/ai.py` son públicos sin rate limit.

**Riesgos de abuso:**
- No hay rate limit en formularios públicos: contacto, newsletter, appointments, photo-requests.
- No hay captcha/turnstile en backend (solo widget en frontend).

**Controles presentes:**
- JWT + permisos granulares (`require_permission`).
- Rate limit en login y upload imágenes.
- CORS restringido por env var.

**Recomendación inmediata:**
- Agregar rate limit a endpoints públicos.
- Revisar si `/stats` y `/items` deben ser públicos; de no serlo, exigir auth o permisos.

---

## 4) Archivos/routers sin conectar
- `src/router/index.ts` no está usado (el proyecto usa `src/router/index.js`).
- `src/views/HomeView.vue` no está referenciado por el router real.
- Routers vacíos: `backend/app/routers/cart`, `backend/app/routers/keyboards`, `backend/app/routers/repair_parts`.
- `backend/app/api/v1/endpoints/categories.py`, `diagnostics.py`, `repairs.py`, `users.py` existen pero no se incluyen en `api_router`.

---

## 5) Prioridad (roadmap impacto/esfuerzo)
**P0 - Seguridad / exposición**
1) Rate limits + captcha backend en endpoints públicos críticos.
2) Revisar exposición de `/stats` y `/items`.

**P1 - Cierres de flujo**
3) PDF de OT con firmas (servicio placeholder).
4) SSE/WS para firmas en tiempo real.

**P2 - UX / producto**
5) Vistas detalle para Tickets, Compras, Manuales.
6) Integración UI con `/analytics/*`.

**P3 - Limpieza técnica**
7) Unificar routers legacy vs api/v1/endpoints.
8) Depurar archivos y routers sin uso.

---

## 6) Acciones sugeridas (inicio de cierre)
- Añadir rate limit a: `/contact`, `/newsletter/subscribe`, `/appointments`, `/photo-requests/submit`, `/diagnostic/*`, `/quotation/estimate`, `/ai/analyze`.
- Definir si `/stats` público es aceptable.
- Definir si `/items` POC debe mantenerse expuesto (si no, esconder o proteger).

---

## 7) Cierres aplicados (2026-01-23)
- Rate limit agregado en endpoints públicos: contact, newsletter, appointments, photo-requests submit, diagnostic calculate, quotation estimate, ai analyze, signature submit.

---

**Resultado:** no hay endpoints rotos en UI, pero sí exposición pública y duplicidad de routers que genera riesgo y deuda técnica.
