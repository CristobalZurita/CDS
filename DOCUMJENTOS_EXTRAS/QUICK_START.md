# 🚀 Quick Start - Sistema de Agendamiento de Citas

## 5 Minutos para Activar el Sistema

### ✅ Paso 1: Verificar que todo está instalado

```bash
# En la raíz del proyecto
cd backend
pip install -r requirements.txt
```

### ✅ Paso 2: Configurar Variables de Entorno

Crear/editar `.env` en la carpeta `backend/`:

```bash
# Copiar template
cp .env.example .env

# Editar con tu editor favorito
nano .env  # o vim, code, etc.
```

**Mínimas configuraciones necesarias:**
```dotenv
# Base de datos (SQLite para desarrollo)
DATABASE_URL=sqlite:///./cirujano.db

# Google Calendar (opcional para empezar)
GOOGLE_CALENDAR_ID=primary
GOOGLE_CALENDAR_CREDENTIALS_FILE=./credentials/google-calendar-credentials.json

# SendGrid (opcional para empezar)
SENDGRID_API_KEY=
SENDGRID_FROM_EMAIL=noreply@cirujanodesintetizadores.cl
```

### ✅ Paso 3: Crear Base de Datos

```bash
cd backend

# Ejecutar migraciones
alembic upgrade head

# Verificar tabla creada
ls -la cirujano.db
```

### ✅ Paso 4: Iniciar Backend

```bash
cd backend

# Iniciar servidor FastAPI
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

**Output esperado:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### ✅ Paso 5: Iniciar Frontend

En otra terminal:

```bash
cd /ruta/del/proyecto

# Instalar dependencias (primera vez)
npm install

# Iniciar dev server
npm run dev
```

**Output esperado:**
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
```

---

## 🧪 Probar el Sistema

### 1. Test en el Browser

1. Ir a `http://localhost:5173/`
2. Encontrar la sección de hero con botones
3. Clicker en "Agenda tu hora"
4. Llenar formulario:
   - Nombre: `Juan García` ✓
   - Email: `juan@test.com` ✓
   - Teléfono: `+56912345678` ✓
   - Fecha: Seleccionar fecha futura ✓
   - Mensaje: "Test appointment" (opcional) ✓
5. Click en "Agendar cita"
6. Debería aparecer "¡Mensaje Enviado!"

### 2. Test en Terminal (curl)

```bash
# Crear cita
curl -X POST http://localhost:8000/api/v1/appointments/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Test User",
    "email": "test@example.com",
    "telefono": "+56912345678",
    "fecha": "2024-12-25T14:30:00",
    "mensaje": "Test appointment"
  }'

# Listar citas
curl http://localhost:8000/api/v1/appointments/

# Obtener cita específica
curl http://localhost:8000/api/v1/appointments/1
```

### 3. Test en Postman/Insomnia

**POST** `http://localhost:8000/api/v1/appointments/`

Body (JSON):
```json
{
  "nombre": "Cristóbal Zurita",
  "email": "contact@cirujano.cl",
  "telefono": "+56912345678",
  "fecha": "2024-12-25T15:00:00",
  "mensaje": "Necesito reparar mi KORG Micro Korg"
}
```

---

## 🔧 Configuración Avanzada

### Activar Google Calendar Sync

1. **Obtener Credenciales:**
   - Ir a https://console.cloud.google.com/
   - Crear proyecto nuevo: "Cirujano Calendar"
   - Habilitar "Google Calendar API"
   - Crear "Service Account"
   - Descargar JSON key

2. **Instalar Credenciales:**
   ```bash
   # Mover archivo descargado
   mv ~/Downloads/your-key.json backend/credentials/google-calendar-credentials.json
   ```

3. **Configurar .env:**
   ```dotenv
   GOOGLE_CALENDAR_CREDENTIALS_FILE=./credentials/google-calendar-credentials.json
   GOOGLE_CALENDAR_ID=primary
   ```

4. **Compartir Calendario:**
   - Abrir Google Calendar
   - Settings de tu calendario personal
   - Agregar permisos a: email del service account (en el JSON)

5. **Reiniciar Backend:**
   ```bash
   # Ctrl+C para detener
   # Luego:
   uvicorn backend.app.main:app --reload --port 8000
   ```

### Activar Email Confirmación

1. **Crear Cuenta SendGrid:**
   - Ir a https://sendgrid.com/
   - Sign up gratis
   - Generar API key

2. **Configurar .env:**
   ```dotenv
   SENDGRID_API_KEY=SG.xxxxxxxxxxxxx
   SENDGRID_FROM_EMAIL=citas@cirujanodesintetizadores.cl
   ```

3. **Verificar Email Remitente:**
   - En SendGrid, verificar el email remitente

4. **Reiniciar Backend:**
   ```bash
   uvicorn backend.app.main:app --reload --port 8000
   ```

---

## 🐛 Troubleshooting Rápido

### Modal no aparece
```javascript
// En browser console
console.log('AppointmentModal importado')
// Si hay error, revisar PageHeader.vue import
```

### Error 422 al enviar formulario
```
Validación fallida. Revisar:
- Nombre: solo letras, espacios, acentos, Ñ
- Email: formato válido (a@b.com)
- Teléfono: comienza con +
- Fecha: debe ser futura
```

### Error 500 del backend
```bash
# Ver logs del backend
tail -f logs/cirujano.log

# O en la terminal donde corre uvicorn
# Revisar el error mostrado
```

### Base de datos no se crea
```bash
cd backend
alembic upgrade head
# Si falla, revisar permisos en carpeta backend/
```

### Google Calendar no sincroniza
```bash
# Verificar credenciales
python -c "
import json
with open('credentials/google-calendar-credentials.json') as f:
    data = json.load(f)
    print(f'✓ Credenciales válidas: {data[\"project_id\"]}')
"
```

---

## 📁 Archivos Clave

| Archivo | Función |
|---------|---------|
| `src/vue/components/modals/AppointmentModal.vue` | Formulario modal |
| `src/vue/components/layout/PageHeader.vue` | Botón que abre modal |
| `backend/app/models/appointment.py` | Modelo de BD |
| `backend/app/routers/appointment.py` | Endpoints API |
| `backend/app/services/google_calendar_service.py` | Sincronización Google |
| `alembic/versions/0005_add_appointments.py` | Migration de BD |
| `backend/.env` | Configuración (no commitear) |
| `APPOINTMENT_SYSTEM.md` | Documentación completa |

---

## 📊 Verificar Datos

### Ver citas en BD (SQLite)

```bash
# Instalar sqlite3 si no está
# MacOS: brew install sqlite3
# Ubuntu: sudo apt-get install sqlite3

# Abrir BD
sqlite3 backend/cirujano.db

# Ver citas
SELECT * FROM appointments;

# Contar citas
SELECT COUNT(*) FROM appointments;

# Salir
.quit
```

### Ver en Panel de Administración

```
Próximamente en: /admin/appointments
```

---

## 🚀 Desplegar a Producción

```bash
# 1. Cambiar variables de entorno
# Editar .env con valores de producción

# 2. Usar base de datos PostgreSQL
DATABASE_URL=postgresql://user:pass@host:5432/cirujano

# 3. Desactivar debug
DEBUG=false

# 4. Generar secrets nuevos
# Cambiar SECRET_KEY y JWT_SECRET

# 5. Ejecutar en servidor
# gunicorn -w 4 -b 0.0.0.0:8000 backend.app.main:app

# 6. Usar HTTPS
# Configurar SSL en nginx/Apache
```

---

## 📞 Soporte

- 📧 Email: contacto@cirujanodesintetizadores.cl
- 🌐 Web: https://cirujanodesintetizadores.cl
- 📖 Docs: Ver `APPOINTMENT_SYSTEM.md`

---

## ✨ Siguientes Pasos

1. ✅ Sistema funcionando
2. ⏭️ Personalizar colores (editar `/src/scss/_variables.scss`)
3. ⏭️ Agregar más campos si necesita
4. ⏭️ Conectar con calendar
5. ⏭️ Activar notificaciones email
6. ⏭️ Publicar a producción

---

**¡Sistema listo para usar!** 🎉
