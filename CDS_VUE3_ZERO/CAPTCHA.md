# CAPTCHA / TURNSTILE - GUIA OPERATIVA CDS_VUE3_ZERO

Este proyecto usa **Cloudflare Turnstile** (no reCAPTCHA) para login y formularios publicos.

Objetivo de esta guia:
- Modo desarrollo rapido (captcha desactivado con bypass)
- Modo real (captcha activo en produccion)
- Verificacion y troubleshooting
- Criterios de seguridad para no filtrar secretos

---

## 1) Estado actual del proyecto (importante)

Frontend (`CDS_VUE3_ZERO`) usa estas variables:
- `VITE_TURNSTILE_SITE_KEY`
- `VITE_TURNSTILE_DISABLE`
- `VITE_API_URL`

Backend (`backend`) usa estas variables:
- `TURNSTILE_SECRET_KEY`
- `TURNSTILE_DISABLE`
- `ENVIRONMENT`

Comportamiento clave:
- Si `VITE_TURNSTILE_DISABLE=true`, el frontend emite token de bypass para pruebas.
- Si `TURNSTILE_DISABLE=true`, backend acepta el captcha automaticamente.
- Si `ENVIRONMENT=development`, auth puede saltar verificacion de captcha.

---

## 2) Archivos y politica de secretos

No renombrar ni reemplazar:
- `.env.example` (plantilla versionada)

Usar para ejecucion real/local:
- `.env` (archivo local, con valores reales)

Archivos:
- Front plantilla: `CDS_VUE3_ZERO/.env.example`
- Front local: `CDS_VUE3_ZERO/.env`
- Back plantilla: `backend/.env.example`
- Back local: `backend/.env`

Git:
- `.env` debe estar ignorado por `.gitignore` (ya esta configurado).
- Nunca subir site key/secret key reales al repo.

---

## 3) Modo desarrollo (rapido) - captcha desactivado

### 3.1 Frontend: `CDS_VUE3_ZERO/.env`

```env
VITE_API_URL=http://localhost:8000/api/v1
VITE_TURNSTILE_DISABLE=true
VITE_TURNSTILE_SITE_KEY=REPLACE_WITH_TURNSTILE_SITE_KEY
```

> Con esto aparece el estado de pruebas y el boton de login se puede habilitar.

### 3.2 Backend: `backend/.env`

```env
ENVIRONMENT=development
TURNSTILE_DISABLE=true
TURNSTILE_SECRET_KEY=REPLACE_WITH_TURNSTILE_SECRET_KEY
```

### 3.3 Levantar servicios

Terminal A (front):
```bash
cd /mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/CDS_VUE3_ZERO
npm run dev
```

Terminal B (back):
```bash
cd /mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

---

## 4) Modo real (produccion o pre-produccion) - captcha activo

## 4.1 Obtener claves Turnstile

En Cloudflare Turnstile:
- Crear sitio
- Registrar dominios reales
- Copiar:
  - `site key` (frontend)
  - `secret key` (backend)

## 4.2 Configuracion frontend (`CDS_VUE3_ZERO/.env`)

```env
VITE_API_URL=https://TU_API_REAL/api/v1
VITE_TURNSTILE_DISABLE=false
VITE_TURNSTILE_SITE_KEY=TU_SITE_KEY_REAL
```

## 4.3 Configuracion backend (`backend/.env`)

```env
ENVIRONMENT=production
TURNSTILE_DISABLE=false
TURNSTILE_SECRET_KEY=TU_SECRET_KEY_REAL
```

## 4.4 Reiniciar servicios

Siempre reiniciar front y back al cambiar `.env`.

---

## 5) Checklist de validacion (modo real)

1. Abre login y verifica que **se renderiza el widget real** de Turnstile.
2. Completa captcha y credenciales.
3. El boton "Iniciar sesion" debe habilitarse.
4. Si captcha no se resuelve, backend debe responder `400` con `Captcha invalido`.
5. Si captcha OK y credenciales validas, login normal.

---

## 6) Troubleshooting rapido

### Error: boton "Iniciar sesion" bloqueado
Causas tipicas:
- `VITE_TURNSTILE_DISABLE=false` y no hay `VITE_TURNSTILE_SITE_KEY` valida.
- El script de Turnstile no carga (bloqueo de red/extensiones).
- Token expirado/no emitido.

Acciones:
1. Revisar `CDS_VUE3_ZERO/.env`
2. Reiniciar `npm run dev`
3. Revisar consola navegador (`[turnstile] Missing VITE_TURNSTILE_SITE_KEY`)

### Error vite proxy: `ECONNREFUSED 127.0.0.1:8000`
Significa que backend no esta corriendo.

Accion:
- Levantar backend desde carpeta `backend` con:
  `uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`

### Error backend: `ModuleNotFoundError: No module named 'app'`
Causa:
- Uvicorn lanzado desde carpeta incorrecta.

Accion:
- `cd .../cirujano-front_CLEAN/backend` antes de ejecutar uvicorn.

---

## 7) Seguridad y buenas practicas

1. No subir `.env` al repo.
2. No pegar keys reales en tickets, issues o chats.
3. Mantener `.env.example` con placeholders.
4. Rotar keys si hubo exposicion accidental.
5. Verificar antes de commit:

```bash
git status
git check-ignore -v CDS_VUE3_ZERO/.env backend/.env
```

---

## 8) Cambio de modo rapido (resumen)

Desarrollo (bypass):
- Front: `VITE_TURNSTILE_DISABLE=true`
- Back: `TURNSTILE_DISABLE=true`

Real:
- Front: `VITE_TURNSTILE_DISABLE=false` + `VITE_TURNSTILE_SITE_KEY` real
- Back: `TURNSTILE_DISABLE=false` + `TURNSTILE_SECRET_KEY` real

