# AUDITORIA CDS DOMINGO

## 1. Executive Summary
- Alcance: repositorio local `cirujano-front_CLEAN` (frontend + backend). Revisiones realizadas sobre archivos actuales y configuraciones detectadas en el repo.
- Estado general: sin secretos activos en archivos `.env` versionados; existen riesgos de seguridad en scripts de admin/seed, fallback JWT en ausencia de dependencia, y exposicion de uploads/doc endpoints en produccion.
- Nota de herramientas: no se ejecuto SAST externo (SonarQube/Semgrep/CodeQL), ni DAST (ZAP/Burp). Se incluyen comandos recomendados para ejecucion controlada.

## 2. Auditoria de Seguridad del Codigo

### 2.1 Analisis Estatico (SAST)
No ejecutado en esta iteracion. Comandos sugeridos:
```bash
# Semgrep
semgrep --config p/owasp-top-ten --error --metrics=off

# CodeQL (si se integra via GitHub Actions)
# SonarQube (si existe servidor y token)
```

### 2.1.b Informacion extra (hallazgos fuera de SAST)
- Falsos positivos por secretos en dependencias dentro de `venv/` y `backend/.venv/`. No son del codigo del proyecto; provienen de tests de librerias. Requiere excluir en `ggshield` y mantener esas carpetas fuera de Git.
- Documentacion interna con ejemplos de variables sensibles en `DOCUMJENTOS_EXTRAS/` (no son secretos reales, pero pueden disparar alertas y no deben considerarse codigo productivo).

### 2.2 Revision Manual de Codigo (resultados)

#### Hallazgos Criticos
1) Fallback JWT que emite token fijo si falta `python-jose`.
- Archivo: `backend/app/core/security.py`
- Impacto: autenticacion potencialmente inutil/forgable si la dependencia falta en runtime.
- Recomendacion: fallar en startup en produccion cuando `python-jose` no este disponible.

2) Creacion de admin guarda password en texto plano si falla hashing.
- Archivo: `backend/scripts/create_admin.py`
- Impacto: almacenamiento de credenciales en claro si falla bcrypt/passlib.
- Recomendacion: abortar con error si falla el hash. No persistir en claro.

3) Seed con usuarios y passwords fijos (admin12/test12).
- Archivo: `backend/scripts/init_db_and_seed.py`
- Impacto: cuentas previsibles si el script se ejecuta fuera de entorno dev.
- Recomendacion: exigir flag explicito `--dev` o lectura interactiva.

#### Hallazgos Altos
4) Exposicion de tokens en URL para firma/foto.
- Archivo: `src/router/index.js`
- Rutas: `/signature/:token`, `/photo-upload/:token`
- Impacto: si los tokens no expiran/rotan o se filtran, permiten acceso directo.
- Recomendacion: expiracion corta y validacion server-side estricta.

5) Servir uploads de forma publica.
- Archivo: `backend/app/main.py`
- Impacto: archivos subidos accesibles sin autenticacion.
- Recomendacion: proteger ruta o mover a storage privado con URLs firmadas.

#### Hallazgos Medios
6) `JWT_REFRESH_SECRET` no obligatorio en produccion.
- Archivo: `backend/app/core/config.py`
- Impacto: refresh tokens pueden fallar o quedar con secreto nulo.
- Recomendacion: exigir en el mismo bloque de validacion que `JWT_SECRET`.

7) Respuesta incluye `reset_token` fuera de produccion.
- Archivo: `backend/app/api/v1/endpoints/auth.py`
- Impacto: si `ENVIRONMENT` esta mal configurado, expone tokens.
- Recomendacion: validar que produccion nunca devuelva tokens en respuesta.

8) Docs/OpenAPI habilitados en produccion.
- Archivo: `backend/app/main.py`
- Impacto: expone superficie API y schemas.
- Recomendacion: deshabilitar o proteger en prod.

#### Hallazgos Bajos
9) Tokens almacenados en localStorage.
- Archivo: `src/composables/useAuth.js`
- Impacto: riesgo de exfiltracion por XSS.
- Recomendacion: usar cookies httpOnly si es viable.

#### Informacion extra (sin severidad asignada)
- Rutas publicas basadas en token: `/signature/:token` y `/photo-upload/:token` en `src/router/index.js`. Requiere revision de expiracion y validacion server-side.
- Credenciales de EmailJS en frontend: `src/composables/emails.js` (publicas por diseño). Revisar restricciones del proveedor.

### 2.3 Analisis de Dependencias
No ejecutado en esta iteracion. Comandos sugeridos:
```bash
npm audit
python -m pip install --user pip-audit
pip-audit
```

## 3. Auditoria de Infraestructura y Configuracion

### 3.1 Configuracion de Servidores
- Headers de seguridad: solo aplicados si `ENVIRONMENT=production`.
- HTTPS redirect: aplicado en prod.
- CORS: permite localhost en dev; validar `ALLOWED_ORIGINS` en prod.

### 3.2 Base de Datos
- No se evaluo cifrado en reposo ni backups (fuera del repo).

### 3.3 Variables de Entorno y Secrets
- `.env` y `backend/.env` eliminados del historial del repo.
- `.env.example` versionados sin secretos.
- Se recomienda gestor de secretos en prod.

## 4. Auditoria de Autenticacion y Autorizacion
- JWT con access + refresh tokens.
- Rate limit en login (en `auth.py`).
- RBAC/permiso granular presente en `backend/app/core/dependencies.py` y routers.
- Riesgo: fallback JWT y seed con passwords fijas (ver criticos).

## 5. Auditoria de APIs
- Rate limit aplicado solo en login.
- Validacion de inputs depende de esquemas Pydantic.
- Metodos HTTP permitidos no restringidos globalmente.

## 6. Respuesta y Remediacion de Incidentes de Secretos en Git

### 6.1 Deteccion
Comandos recomendados (no ejecutados en este informe):
```bash
# Historial
git log --all --full-history --source --find-renames --diff-filter=D --pretty=format: --name-only | sort -u

# Escaneo local actual
ggshield secret scan path . --recursive
```

### 6.2 Saneamiento de Historial
Se utilizo `git filter-repo` para eliminar `.env` y `backend/.env` del historial.
Comando aplicado:
```bash
git filter-repo --path .env --path backend/.env --invert-paths
```

### 6.3 Verificacion
```bash
git log --all --name-only --pretty=format: -- .env backend/.env
```

### 6.4 Force Push
```bash
git push --force --all
git push --force --tags
```

### 6.5 Rotacion de Credenciales
- SMTP, Turnstile, WhatsApp Token, JWT secrets: rotados fuera del repo.

### 6.6 Hardening del Repo
- `.gitignore` incluye `.env`, `.env.local`, `backend/.env`, `backend/.env.local`.
- Recomendado: pre-commit con detect-secrets/gitleaks.

### 6.7 Informacion extra (estado de escaneo)
- GitGuardian: incidentes historicos pueden seguir visibles hasta cierre manual, aunque el re-scan indique 0 incidentes nuevos.
- ggshield: escaneo local detecto secretos en `venv/` (falsos positivos). Se requiere `.ggshield-ignore` con exclusion de `venv/`, `.venv/`, `backend/.venv/`, `node_modules/`, `dist/`, `uploads/`, `reports/`, `DOCUMJENTOS_EXTRAS/`.

## 7. Plan de Remediacion (priorizado)

### 7.1 Critica (24-48h)
- Eliminar fallback JWT en prod. `backend/app/core/security.py`
- Evitar password en claro en create_admin. `backend/scripts/create_admin.py`
- Proteger seed de credenciales fijas. `backend/scripts/init_db_and_seed.py`

### 7.2 Alta (1 semana)
- Proteger `/uploads` o mover a storage privado. `backend/app/main.py`
- Agregar expiracion/rotacion para tokens publicos. `src/router/index.js`

### 7.3 Media (2 semanas)
- Exigir `JWT_REFRESH_SECRET` en prod. `backend/app/core/config.py`
- Deshabilitar `/docs` y `/openapi.json` en prod. `backend/app/main.py`

### 7.4 Baja (1 mes)
- Revisar migracion de tokens desde localStorage a cookies httpOnly.

## 8. Checklist Post-Remediacion
- [ ] Historial Git limpio (sin `.env`, `.venv`, `uploads`, `reports`, `*.db`).
- [ ] Credenciales rotadas y vigentes.
- [ ] Pre-commit hooks activos.
- [ ] CI con escaneo de secretos.
- [ ] Re-scan GitGuardian sin incidentes activos.
- [ ] Verificacion de prod con `ENVIRONMENT=production`.

## 9. Evidencias y Referencias
- Archivos sensibles revisados:
  - `backend/app/core/security.py`
  - `backend/scripts/create_admin.py`
  - `backend/scripts/init_db_and_seed.py`
  - `backend/app/main.py`
  - `backend/app/core/config.py`
  - `backend/app/api/v1/endpoints/auth.py`
  - `src/composables/useAuth.js`
  - `src/router/index.js`
  - `src/composables/emails.js`
  - `DOCUMJENTOS_EXTRAS/`
  - `venv/` y `backend/.venv/`
