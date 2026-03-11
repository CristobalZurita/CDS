# 🔒 AUDITORÍA DE SEGURIDAD - CDS ZERO

**Fecha**: 2026-03-11  
**Alcance**: CDS_VUE3_ZERO (Frontend) + Backend FastAPI  
**Tipo**: Mapeo exhaustivo (no implementación)  

---

## 📋 RESUMEN EJECUTIVO

| Categoría | Estado | Items |
|-----------|--------|-------|
| ✅ **Fuerte** | 12 | JWT con refresh tokens, bcrypt, rate limiting, validación de inputs, Cloudinary, HTTPS en prod, HSTS, XSS protection, SQL injection filters, path traversal protection, audit logging, CSRF opcional |
| ⚠️ **Mejorable** | 5 | CSP headers, cookies seguras, dependency updates, CORS restrictivo en dev, headers de seguridad faltantes |
| ❌ **Faltante** | 3 | Content Security Policy completo, SameSite cookies, Subresource Integrity (SRI) |

---

## 1. AUTENTICACIÓN Y AUTORIZACIÓN

### 1.1 JWT (backend/app/core/security.py) ✅

**Lo que HAY:**
```python
# Doble secreto: access + refresh
jwt_secret: Optional[str] = os.getenv("JWT_SECRET")
jwt_refresh_secret: Optional[str] = os.getenv("JWT_REFRESH_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
```

**Validaciones en producción:**
- ✅ Requiere SECRET_KEY, JWT_SECRET, JWT_REFRESH_SECRET
- ✅ Prohíbe que refresh == secret
- ✅ Mínimo 64 caracteres para secrets

**Lo que FALTA:**
- ❌ No hay blacklist de tokens revocados (logout solo borra del cliente)
- ❌ No hay rotación automática de refresh tokens
- ⚠️ Los tokens se almacenan en localStorage (vulnerable a XSS)

**Cómo se soluciona:**
```python
# Opción A: Redis blacklist
redis.setex(f"blacklist:{token_jti}", ttl, "revoked")

# Opción B: Cookies httpOnly (recomendado)
response.set_cookie(
    "access_token",
    token,
    httponly=True,
    secure=True,
    samesite="Strict",
    max_age=1800
)
```

### 1.2 Password Hashing ✅

**Lo que HAY:**
```python
# bcrypt directo (recomendado) con fallback pbkdf2
bcrypt.hashpw(pw_bytes[:72], bcrypt.gensalt())
```

**Verificación:**
```python
# Detecta bcrypt por prefijo $2
if hashed_password.startswith("$"):
    return bcrypt.checkpw(password_bytes, hash_bytes)
```

**Estado**: ✅ Implementación correcta

### 1.3 2FA (Two-Factor Authentication) ✅

**Lo que HAY:**
- Endpoint `/auth/2fa/verify` implementado
- Challenge ID + código numérico
- Store frontend soporta `requires_2fa`

**Falta verificar**:
- ⚠️ Si usa TOTP (Google Authenticator) o solo email/SMS
- ⚠️ Backup codes para recuperación

---

## 2. MANEJO DE SESIONES

### 2.1 Almacenamiento de Tokens ⚠️

**Frontend (CDS_VUE3_ZERO/src/services/api.js):**
```javascript
const AUTH_TOKEN_KEY = 'cds_auth_token'
const AUTH_USER_KEY = 'cds_auth_user'
// Almacenado en localStorage
storage.setItem(AUTH_TOKEN_KEY, token)
```

**Riesgo**: XSS puede robar tokens

**Solución:**
```javascript
// Opción A: Cookies httpOnly (backend debe soportar)
// Opción B: Memory storage (pierde sesión al recargar)
// Opción C: Service Worker con proxy
```

### 2.2 Refresh Token Flow ✅

**Backend:**
```python
# create_refresh_token usa secret diferente
jwt.encode(to_encode, settings.jwt_refresh_secret, algorithm=ALGORITHM)
```

**Falta:**
- ❌ Endpoint `/auth/refresh` no encontrado en análisis
- ❌ Rotación de refresh tokens

---

## 3. PROTECCIÓN CONTRA ATAQUES COMUNES

### 3.1 SQL Injection ✅

**Middleware (backend/app/middleware/validation.py):**
```python
SQL_INJECTION_PATTERNS = [
    r"(\bUNION\b.*\bSELECT\b)",
    r"(\bOR\b\s*['\"]?\d+['\"]?\s*=)",
    r"(--\s*$)",
    r"(/\*.*?\*/)",
    r"(;\s*DROP)",
    r"(;\s*DELETE)",
    r"(xp_cmdshell)",
]
```

**Implementación:**
- ✅ Middleware valida POST/PUT/PATCH
- ✅ Reglas por endpoint en ENDPOINT_VALIDATION_RULES
- ✅ Usa ORM SQLAlchemy (parametrizado por defecto)

**Estado**: ✅ Bien protegido

### 3.2 XSS (Cross-Site Scripting) ✅/⚠️

**Backend - Detección:**
```python
XSS_PATTERNS = [
    r"<script[^>]*>",
    r"<iframe[^>]*>",
    r"<embed[^>]*>",
    r"<object[^>]*>",
    r"javascript:",
    r"on\w+\s*=",
]
```

**Frontend:**
- ⚠️ No se detectó sanitización explícita en inputs
- ⚠️ Vue escapa por defecto {{ }}, pero v-html es riesgoso

**Solución:**
```javascript
// Composable useSanitizer.js
import DOMPurify from 'dompurify'
export function sanitizeHTML(dirty) {
  return DOMPurify.sanitize(dirty)
}
```

### 3.3 CSRF (Cross-Site Request Forgery) ⚠️

**Backend:**
```python
# Middleware condicional
enforce_csrf: bool = os.getenv("ENFORCE_CSRF", "true" if _IS_PROD_ENV else "false")

# Excepciones para auth
csrf_exempt_paths = {
    "/api/v1/auth/login",
    "/api/v1/auth/register",
    "/api/v1/auth/forgot-password",
    "/api/v1/auth/reset-password",
    "/api/v1/auth/confirm-email",
    "/api/csrf-token",
}
```

**Problema:**
- ⚠️ Bearer tokens no requieren CSRF (bien)
- ⚠️ CSRF solo activo en producción por defecto
- ❌ No hay doble cookie pattern implementado

### 3.4 Path Traversal ✅

**Uploads (backend/app/utils/uploads.py):**
```python
def resolve_upload_path(path_value: str, uploads_root: str = "uploads") -> Path:
    candidate = Path(path_value)
    if not candidate.is_absolute():
        candidate = Path(uploads_root) / candidate
    resolved = candidate.resolve()
    root = Path(uploads_root).resolve()
    if root not in resolved.parents and resolved != root:
        raise ValueError("Invalid uploads path")
    return resolved
```

**Estado**: ✅ Protegido

### 3.5 Rate Limiting ✅

**Configuración:**
```python
# backend/app/core/ratelimit.py
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address, storage_uri=RATE_LIMIT_STORAGE)
```

**Uso en endpoints:**
```python
@router.post("/images")
@limiter.limit("20/minute")  # Uploads limitados
```

**Estado**: ✅ Implementado

---

## 4. HEADERS DE SEGURIDAD HTTP

### 4.1 Implementados en Producción ✅

**backend/app/main.py:**
```python
if settings.environment in ("production", "prod"):
    response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer-when-downgrade"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=()"
```

### 4.2 FALTANTES ❌

| Header | Estado | Riesgo |
|--------|--------|--------|
| Content-Security-Policy | ❌ No implementado | XSS, data injection |
| X-XSS-Protection | ❌ No implementado | XSS legacy browsers |
| Expect-CT | ❌ No implementado | Certificate transparency |
| Feature-Policy (legacy) | ✅ Permissions-Policy | OK |

**Solución CSP:**
```python
response.headers["Content-Security-Policy"] = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
    "style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data: https://res.cloudinary.com; "
    "font-src 'self'; "
    "connect-src 'self' https://api.cirujanodesintetizadores.cl; "
    "frame-ancestors 'none'; "
    "base-uri 'self'; "
    "form-action 'self';"
)
```

---

## 5. CORS (Cross-Origin Resource Sharing)

### 5.1 Configuración Actual ⚠️

**backend/app/core/config.py:**
```python
allowed_origins: list = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
]
```

**backend/app/main.py:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 5.2 Problemas

- ⚠️ `allow_methods=["*"]` permite todos los métodos
- ⚠️ `allow_headers=["*"]` permite todos los headers
- ⚠️ En dev, añade orígenes dinámicamente (bien), pero en prod debería ser restrictivo

### 5.3 Solución

```python
# Producción
allow_origins=["https://cirujanodesintetizadores.cl"],
allow_methods=["GET", "POST", "PUT", "DELETE"],
allow_headers=["Authorization", "Content-Type", "X-CSRF-Token"],
```

---

## 6. MANEJO DE ARCHIVOS Y UPLOADS

### 6.1 Validación de Imágenes ✅

**backend/app/utils/uploads.py:**
```python
MAX_IMAGE_SIZE = int(os.getenv("IMAGE_MAX_SIZE", str(5 * 1024 * 1024)))  # 5MB
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp"}

# Validación de firma de archivo
def _matches_image_signature(filename: str, content: bytes) -> bool:
    sig = content[:12]
    # PNG, JPEG, GIF, WEBP signatures
```

**Verificación:**
- ✅ Extensión validada
- ✅ Tamaño limitado
- ✅ Firma de archivo verificada (magic bytes)
- ✅ Pillow verification como capa adicional

### 6.2 Cloudinary ✅

**backend/app/services/cloudinary_service.py:**
- ✅ 518 imágenes en CDN (no local)
- ✅ URLs firmadas disponibles
- ✅ Transformaciones seguras

### 6.3 Control de Acceso ✅

**backend/app/routers/uploads.py:**
```python
async def require_upload_access(user: Optional[dict] = Depends(get_optional_user)):
    if user is not None:
        return user
    if settings.enable_public_uploads:
        return None
    raise HTTPException(status_code=403, detail="Not authenticated")
```

**Restricciones:**
- ✅ Solo admin puede subir a "instrumentos" e "inventario"
- ✅ Rate limiting 20/minuto
- ✅ Audit logging de uploads

---

## 7. DEPENDENCIAS Y VULNERABILIDADES

### 7.1 Frontend ZERO

```json
{
  "axios": "^1.13.2",
  "pinia": "^3.0.4",
  "vue": "^3.2.47",
  "vue-router": "^4.2.4"
}
```

**Análisis:**
- ✅ Versiones recientes
- ⚠️ Sin `dompurify` en ZERO (está en LEGACY)
- ⚠️ Sin librería de CSP

### 7.2 Backend

**Críticas:**
```
fastapi==0.104.1        # OK
python-jose==3.5.0      # OK
passlib==1.7.4          # OK
bcrypt                  # OK
slowapi==0.1.5          # OK
cloudinary==1.38.0      # OK
```

**Potencialmente problemáticas:**
```
pandas==2.3.3           # Solo para Excel, no expuesto a red
Pillow==12.1.1          # Historial de vulns, mantener actualizado
redis==3.5.3            # Outdated, latest es 5.x
google-auth==2.25.2     # Revisar periodicamente
```

### 7.3 Solución

```bash
# Script de auditoría semanal
pip install safety bandit
safety check
bandit -r backend/app/
```

---

## 8. CI/CD SEGURIDAD

### 8.1 Workflows Activos ✅

| Workflow | Función |
|----------|---------|
| `secret-scan.yml` | detect-secrets + baseline |
| `security.yml` | Bandit, Safety, NPM Audit, TruffleHog, Trivy |
| `tests.yml` | Tests funcionales |

### 8.2 Estado

- ✅ Secret scanning en cada push
- ✅ `.secrets.baseline` configurado
- ✅ Bandit (Python security linter)
- ✅ Safety (dependency vulnerabilities)
- ⚠️ `continue-on-error: true` en algunos pasos (no bloquea)

---

## 9. CONFIGURACIÓN DE ENTORNO

### 9.1 Variables Críticas (backend/.env.example)

```bash
# ✅ Requieren valores seguros en producción
SECRET_KEY=REPLACE_WITH_RANDOM_64_HEX
JWT_SECRET=REPLACE_WITH_RANDOM_64_HEX
JWT_REFRESH_SECRET=REPLACE_WITH_RANDOM_64_HEX

# ✅ Defaults seguros
ALLOW_TOKEN_IN_RESPONSE=false
ENABLE_API_DOCS=false
ENABLE_PUBLIC_UPLOADS=false
ENFORCE_CSRF=false  # Solo true en prod
```

### 9.2 Frontend (CDS_VUE3_ZERO/.env)

```bash
VITE_API_URL=http://localhost:8000/api/v1
VITE_TURNSTILE_DISABLE=true  # ⚠️ Debe ser false en prod
```

### 9.3 Riesgos

- ⚠️ `ENFORCE_CSRF=false` por defecto (solo debe serlo en dev)
- ⚠️ `VITE_TURNSTILE_DISABLE=true` puede olvidarse en prod

---

## 10. AUDIT LOGGING ✅

**backend/app/services/audit_service.py:**
```python
# Audit logging service inicializado en main.py
app.state.audit_service = audit_service
```

**Eventos auditados:**
- ✅ Upload de imágenes
- ✅ Login/logout
- ✅ Cambios en reparaciones

---

## 11. HTTPS Y TRANSPORTE SEGURO

### 11.1 En Producción ✅

```python
if settings.environment in ("production", "prod"):
    # Redirect HTTP to HTTPS
    app.add_middleware(HTTPSRedirectMiddleware)
```

### 11.2 En Desarrollo ⚠️

**CDS_VUE3_ZERO/vite.config.js:**
```javascript
proxy: {
  '/api': {
    target: 'http://127.0.0.1:8000',  // HTTP, no HTTPS
    changeOrigin: true,
    secure: false,  // ⚠️ No verifica certificado
  },
}
```

**Riesgo**: Solo afecta desarrollo local, pero documentar.

---

## 12. MAPEO DE GAPS Y SOLUCIONES

### 🔴 CRÍTICO (Arreglar ASAP)

| Gap | Ubicación | Solución |
|-----|-----------|----------|
| Tokens en localStorage | `src/services/api.js:6-7` | Migrar a cookies httpOnly o implementar refresh token rotation |
| CSP faltante | `backend/app/main.py:191-195` | Agregar Content-Security-Policy header |
| Redis desactualizado | `requirements.txt` | Actualizar a redis>=5.0.0 |

### 🟡 MEDIO (Mejorar)

| Gap | Ubicación | Solución |
|-----|-----------|----------|
| CORS permisivo | `backend/app/main.py:170-171` | Restringir métodos y headers en prod |
| DOMPurify faltante | ZERO package.json | Agregar para sanitización de inputs |
| No hay blacklist JWT | `backend/app/core/security.py` | Implementar Redis blacklist para logout |
| X-XSS-Protection | `backend/app/main.py` | Agregar header legacy |

### 🟢 BAJO (Opcional)

| Gap | Ubicación | Solución |
|-----|-----------|----------|
| SRI (Subresource Integrity) | index.html | Agregar integrity hashes a CDN |
| Expect-CT | `backend/app/main.py` | Certificate transparency |
| Feature-Policy legacy | - | Ya tiene Permissions-Policy |

---

## 13. CHECKLIST DE SEGURIDAD PRE-DEPLOY

```markdown
- [ ] JWT_SECRET y JWT_REFRESH_SECRET son diferentes y >= 64 chars
- [ ] ENFORCE_CSRF=true en producción
- [ ] ENABLE_API_DOCS=false en producción
- [ ] ENABLE_PUBLIC_UPLOADS=false en producción
- [ ] CORS_ORIGINS restringido a dominios válidos
- [ ] HTTPSRedirectMiddleware activo
- [ ] CSP header configurado
- [ ] Cookies httpOnly implementadas (o al menos plan de migración)
- [ ] Rate limiting activo en Redis (no memory)
- [ ] AUDIT logging funcionando
- [ ] Secret scanning pasando en CI/CD
- [ ] Dependency audit sin vulnerabilidades HIGH/CRITICAL
```

---

## 14. REFERENCIAS RÁPIDAS

### Archivos clave de seguridad:
- `backend/app/core/security.py` - JWT y hashing
- `backend/app/core/config.py` - Configuración de seguridad
- `backend/app/middleware/validation.py` - SQL/XSS filters
- `backend/app/core/ratelimit.py` - Rate limiting
- `backend/app/routers/csrf.py` - CSRF tokens
- `CDS_VUE3_ZERO/src/services/api.js` - Cliente HTTP y tokens
- `CDS_VUE3_ZERO/src/stores/auth.js` - Gestión de sesión

### Variables de entorno críticas:
- `SECRET_KEY`
- `JWT_SECRET`
- `JWT_REFRESH_SECRET`
- `ENFORCE_CSRF`
- `ALLOWED_ORIGINS`
- `RATE_LIMIT_STORAGE_URI`

---

*Documento generado para mapeo de seguridad. No contiene credenciales reales.*
