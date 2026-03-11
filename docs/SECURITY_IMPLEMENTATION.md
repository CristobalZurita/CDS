# 🔒 Implementación de Seguridad - CDS ZERO

**Fecha:** 2026-03-11  
**Estado:** Implementado y listo para usar

---

## ✅ Qué se implementó HOY

### 1. CSP Headers (Content Security Policy)

**Archivo:** `backend/app/main.py`

**Qué hace:**
- Bloquea inyección de scripts maliciosos
- Restringe de dónde puede cargar recursos el navegador
- Configuración dinámica según el entorno (dev vs prod)

**Headers agregados:**
```
Content-Security-Policy: default-src 'self'; 
  script-src 'self' 'unsafe-eval'; 
  style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; 
  img-src 'self' data: https://res.cloudinary.com; 
  connect-src 'self' http://localhost:8000;
X-XSS-Protection: 1; mode=block
Expect-CT: max-age=86400, enforce
```

**Para usar:** Nada, se aplica automáticamente en producción.

---

### 2. Sanitización de Inputs (Frontend)

**Archivos:**
- `CDS_VUE3_ZERO/src/utils/sanitize.js` - Utilidades
- `CDS_VUE3_ZERO/src/composables/useSecureForm.js` - Composable para forms

**Qué hace:**
- Elimina scripts y código malicioso de inputs de usuario
- Valida emails y teléfonos
- Protege contra XSS antes de enviar al backend

**Cómo usar:**

```javascript
// Opción A: Sanitizar input individual
import { sanitizeInput, sanitizeEmail, sanitizeHTML } from '@/utils/sanitize'

const userComment = sanitizeHTML('<p>Texto <script>alert("xss")</script></p>')
// Resultado: "<p>Texto </p>"

const userEmail = sanitizeEmail('  TEST@EMAIL.COM  ')
// Resultado: "test@email.com" (limpio y normalizado)

// Opción B: Composable para formularios completos
import { useSecureForm } from '@/composables/useSecureForm'

const { form, sanitizeForm } = useSecureForm({
  name: '',
  email: '',
  notes: ''
})

// Al enviar:
const cleanData = sanitizeForm({
  name: 'text',
  email: 'email',
  notes: 'html'  // Permite HTML seguro
})
await api.post('/clients', cleanData)

// Opción C: Helper rápido
import { sanitizeForAPI } from '@/composables/useSecureForm'

const data = { name: userInput, email: emailInput }
const clean = sanitizeForAPI(data, { name: 'text', email: 'email' })
```

---

### 3. Variables de Entorno Organizadas

**Archivos creados:**
- `CDS_VUE3_ZERO/.env.development` - Desarrollo local
- `CDS_VUE3_ZERO/.env.production` - Template para producción
- `backend/.env.development` - Backend en dev

**Estructura:**
```
.env.development    → Usa ahora (defaults seguros para dev)
.env.production     → Template (rellenar al deployar)
.env.local          → Git ignorado (tus valores reales)
```

**Para usar en desarrollo:**
```bash
# Frontend
cd CDS_VUE3_ZERO
cp .env.development .env.local  # Opcional: personalizar
npm run dev

# Backend
cd backend
cp .env.development .env        # Crea tu .env local
uvicorn app.main:app --reload
```

---

### 4. Script de Validación Pre-Deploy

**Archivo:** `scripts/security-check.sh`

**Qué verifica:**
1. ✅ No hay secrets hardcodeados en código
2. ✅ Archivos `.env` no están en git
3. ✅ Secrets tienen longitud mínima
4. ✅ JWT secrets son diferentes
5. ✅ Configuración de producción es segura
6. ✅ npm audit sin vulnerabilidades HIGH

**Cómo usar:**
```bash
# Antes de deployar
bash scripts/security-check.sh

# Resultado esperado:
# ✅ Todos los checks pasaron
```

---

## 📋 Checklist de Seguridad (Para el día del deploy)

### Variables de Entorno (Backend)
```bash
# Copiar y rellenar:
cp backend/.env.example backend/.env

# Generar secrets seguros:
openssl rand -hex 32  # Ejecutar 3 veces

# Valores a cambiar:
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=<64_chars_hex>
JWT_SECRET=<diferente_64_chars>
JWT_REFRESH_SECRET=<otro_64_chars_diferente>
ALLOWED_ORIGINS=https://tudominio.cl
ENFORCE_CSRF=true
ENABLE_API_DOCS=false
CLOUDINARY_URL=<cloudinary_url>
```

### Variables de Entorno (Frontend)
```bash
# Copiar y rellenar:
cd CDS_VUE3_ZERO
cp .env.production .env.local

# Valores a cambiar:
VITE_API_URL=/api/v1  # Si mismo dominio, o URL completa
VITE_TURNSTILE_SITE_KEY=<tu_key_real>
VITE_TURNSTILE_DISABLE=false
```

### Build y Deploy
```bash
# 1. Verificar seguridad
bash scripts/security-check.sh

# 2. Build frontend
cd CDS_VUE3_ZERO
npm run build
# → Genera dist/ listo para subir

# 3. Subir backend (con .env configurado)
# Subir carpeta backend/ sin __pycache__ ni .env.example

# 4. Subir frontend
# Subir CDS_VUE3_ZERO/dist/ a public_html/
```

---

## 🔍 Verificación Post-Deploy

### Test de Headers de Seguridad
```bash
curl -I https://tudominio.cl

# Debe mostrar:
Strict-Transport-Security: max-age=63072000
Content-Security-Policy: default-src 'self'; ...
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
```

### Test de Sanitización
1. Intentar crear cliente con nombre: `<script>alert(1)</script>`
2. Verificar que se guarda como texto plano o se limpia
3. Revisar que no hay alertas ni ejecución de scripts

### Test de CORS
```bash
curl -H "Origin: https://otro-dominio.com" \
  https://tudominio.cl/api/v1/health

# Debe retornar error CORS (403 o similar)
```

---

## 🛡️ Resumen de Protecciones Activas

| Amenaza | Protección | Archivo |
|---------|-----------|---------|
| XSS | CSP Headers + Sanitización | `main.py` + `sanitize.js` |
| SQL Injection | Validación de inputs + ORM | `validation.py` |
| CSRF | Tokens + middleware | `csrf.py` + `main.py` |
| Path Traversal | Validación de rutas | `uploads.py` |
| Rate Limiting | SlowAPI | `ratelimit.py` |
| Secrets expuestos | Secret scanning + env files | CI/CD + `.env` |
| CORS | Orígenes restringidos | `config.py` |
| Headers de seguridad | HSTS, X-Frame, etc | `main.py` |

---

## 📞 Qué hacer si algo falla

### CSP bloquea recursos legítimos
```python
# En backend/app/main.py, agregar al CSP:
connect-src 'self' https://api.tudominio.cl https://otro-servicio.com;
```

### Sanitización muy agresiva
```javascript
// Usar tipo 'html' para permitir etiquetas básicas
sanitizeForm({ description: 'html' })
```

### Script de security check falla
```bash
# Ver qué check falló:
bash scripts/security-check.sh
# Corregir el problema reportado
```

---

*Implementación completa. El código está listo para producción segura.*
