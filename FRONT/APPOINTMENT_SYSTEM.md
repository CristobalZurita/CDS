# Sistema de Agendamiento de Citas - Cirujano de Sintetizadores

## Descripción General

Este sistema implementa un formulario modal para agendar citas en el sitio web de "Cirujano de Sintetizadores". Incluye:

- **Frontend**: Componente Vue 3 con validaciones en cliente
- **Backend**: API FastAPI con persistencia en BD y sincronización con Google Calendar
- **Email**: Notificaciones automáticas al cliente
- **Google Calendar**: Integración automática de citas

## Componentes del Frontend

### `AppointmentModal.vue`
Located at: `/src/vue/components/modals/AppointmentModal.vue`

**Características:**
- Modal responsive con overlay oscuro
- Formulario con 5 campos:
  - **Nombre**: Solo acepta letras, acentos y Ñ
  - **Email**: Validación de formato A@B.CD (mínimo 5 caracteres)
  - **Teléfono**: Comienza con + seguido de números
  - **Fecha**: Selector de fecha (debe ser en el futuro)
  - **Mensaje**: Campo opcional para consultas adicionales

**Validaciones:**
```javascript
// Nombre: /^[a-záéíóúñA-ZÁÉÍÓÚÑ\s]+$/
// Email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/
// Teléfono: /^\+\d+$/
// Fecha: debe ser mayor a fecha actual
```

**Estados:**
- Formulario activo: Permite editar y enviar
- Enviando: Muestra spinner y desactiva botón
- Éxito: Mensaje "¡Mensaje Enviado!" con botón Cerrar

### Integración en `PageHeader.vue`

El botón "Agenda tu hora" abre el modal:

```vue
<button class="btn-hero btn-primary" @click="openAppointmentModal">
    <i class="fa-solid fa-calendar"></i>
    <span>Agenda tu hora</span>
</button>

<AppointmentModal 
    v-if="showAppointmentModal" 
    @close="showAppointmentModal = false"
    @submit="handleAppointmentSubmit"
/>
```

## Componentes del Backend

### Modelo: `Appointment`
Located at: `/backend/app/models/appointment.py`

**Campos:**
```python
id: Integer (Primary Key)
nombre: String(255) - Nombre del cliente
email: String(255) - Email del cliente (indexed)
telefono: String(20) - Teléfono del cliente
fecha: DateTime - Fecha de la cita (indexed)
mensaje: Text - Mensaje opcional
estado: String(50) - Estado: "pendiente", "confirmado", "cancelado"
google_calendar_id: String(255) - ID del evento en Google Calendar
notificacion_enviada: Boolean - Confirmación de email enviado
created_at: DateTime - Timestamp de creación
updated_at: DateTime - Timestamp de última actualización
```

### Schema: `AppointmentCreate`
Located at: `/backend/app/schemas/appointment.py`

Validaciones Pydantic:
- **nombre**: Solo letras, acentos, Ñ y espacios (min 2, max 255)
- **email**: Email válido (validación Pydantic EmailStr)
- **telefono**: Comienza con + seguido de números (10-20 caracteres)
- **fecha**: DateTime debe ser en el futuro
- **mensaje**: Texto opcional (máx 1000 caracteres)

### CRUD Operations
Located at: `/backend/app/crud/appointment.py`

**Funciones disponibles:**
- `create_appointment()` - Crea una nueva cita
- `get_appointment()` - Obtiene cita por ID
- `get_appointments()` - Lista citas con filtrado
- `get_appointments_by_email()` - Citas por email del cliente
- `get_appointments_by_date_range()` - Citas en rango de fechas
- `update_appointment()` - Actualiza estado/calendario
- `delete_appointment()` - Elimina una cita
- `get_pending_appointments()` - Citas pendientes
- `get_confirmed_appointments()` - Citas confirmadas

### Router: Endpoints de API
Located at: `/backend/app/routers/appointment.py`

**Endpoints:**
```
POST   /api/v1/appointments/                  - Crear cita
GET    /api/v1/appointments/                  - Listar citas (con filtro estado)
GET    /api/v1/appointments/{id}              - Obtener cita específica
GET    /api/v1/appointments/email/{email}     - Citas por email
PATCH  /api/v1/appointments/{id}              - Actualizar cita
DELETE /api/v1/appointments/{id}              - Eliminar cita
GET    /api/v1/appointments/status/pending    - Citas pendientes
GET    /api/v1/appointments/status/confirmed  - Citas confirmadas
```

**Ejemplo de request POST:**
```json
{
    "nombre": "Juan García Pérez",
    "email": "juan@ejemplo.com",
    "telefono": "+56912345678",
    "fecha": "2024-12-20T14:30:00",
    "mensaje": "Necesito reparación de sintetizador KORG"
}
```

**Ejemplo de response:**
```json
{
    "id": 1,
    "nombre": "Juan García Pérez",
    "email": "juan@ejemplo.com",
    "telefono": "+56912345678",
    "fecha": "2024-12-20T14:30:00",
    "mensaje": "Necesito reparación de sintetizador KORG",
    "estado": "pendiente",
    "google_calendar_id": "abc123def456",
    "notificacion_enviada": true,
    "created_at": "2024-12-15T10:00:00",
    "updated_at": null
}
```

### Servicios

#### Email Service
Located at: `/backend/app/services/email_service.py`

**Función:**
```python
async def send_appointment_confirmation(
    email: str,
    nombre: str,
    fecha: datetime,
    appointment_id: int
) -> bool
```

Envía email HTML con:
- Confirmación de cita agendada
- Fecha y hora formateadas
- ID de cita para referencia
- Instrucciones para cambios

**Usa SendGrid** (requiere `SENDGRID_API_KEY`)

#### Google Calendar Service
Located at: `/backend/app/services/google_calendar_service.py`

**Clase:**
```python
class GoogleCalendarService:
    def create_event(calendar_id, title, description, start_time, end_time, attendee_email)
    def update_event(calendar_id, event_id, **kwargs)
    def delete_event(calendar_id, event_id)
```

**Función helper:**
```python
async def sync_to_google_calendar(appointment) -> Optional[str]
```

Sincroniza citas a Google Calendar automáticamente:
- Crea evento con título: "Cita: {nombre}"
- Descripción incluye mensaje de la cita
- Duración: 1 hora desde la fecha especificada
- Timezone: America/Santiago (Chile)
- Invita al cliente al evento

**Requiere:**
- `GOOGLE_CALENDAR_CREDENTIALS_FILE` - Archivo JSON de credenciales de Google
- `GOOGLE_CALENDAR_ID` - ID del calendario (default: "primary")

### Database Migration
Located at: `/alembic/versions/0005_add_appointments.py`

**Crear tabla:**
```bash
cd /path/to/backend
alembic upgrade head
```

**Rollback:**
```bash
alembic downgrade -1
```

## Configuración

### 1. Frontend (.env)
No requiere variables especiales - usa `/api/v1/appointments/` por defecto.

### 2. Backend (.env)

**Variables requeridas:**
```dotenv
# SendGrid (para emails)
SENDGRID_API_KEY=your-sendgrid-api-key
SENDGRID_FROM_EMAIL=noreply@cirujanodesintetizadores.cl

# Google Calendar (para sincronización)
GOOGLE_CALENDAR_CREDENTIALS_FILE=./credentials/google-calendar-credentials.json
GOOGLE_CALENDAR_ID=primary
```

### 3. Google Calendar Setup

**Pasos:**
1. Ir a [Google Cloud Console](https://console.cloud.google.com/)
2. Crear nuevo proyecto o usar uno existente
3. Habilitar Google Calendar API
4. Crear Service Account:
   - Type: Service Account
   - Role: Editor
   - Key format: JSON
5. Descargar JSON y guardar en: `backend/credentials/google-calendar-credentials.json`
6. Compartir calendario con email del service account
7. Copiar Calendar ID a `.env`

### 4. SendGrid Setup

**Pasos:**
1. Crear cuenta en [SendGrid](https://sendgrid.com/)
2. Generar API Key en Settings > API Keys
3. Copiar a `.env`

## Flujo de Funcionamiento

### 1. Cliente llena formulario
```
[AppointmentModal] → Validaciones cliente-side
                  → Envía POST /api/v1/appointments/
```

### 2. Backend recibe solicitud
```
[Router] → Validaciones Pydantic
       → Crea registro en BD
       → Envía email de confirmación
       → Sincroniza a Google Calendar
       → Retorna datos de cita
```

### 3. Frontend muestra éxito
```
[AppointmentModal] → Muestra "¡Mensaje Enviado!"
                  → Botón "Cerrar"
```

### 4. Automático (backend background)
```
[Google Calendar] ← Evento creado automáticamente
[Email Client] ← Recibe confirmación
```

## Testing

### Test Modal (Frontend)
```javascript
// En browser console
const modal = document.querySelector('[data-testid="appointment-modal"]')
// Llenar formulario y validar
```

### Test API (Backend)
```bash
# Crear cita
curl -X POST http://localhost:8000/api/v1/appointments/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Test User",
    "email": "test@example.com",
    "telefono": "+56912345678",
    "fecha": "2024-12-20T14:30:00",
    "mensaje": "Test appointment"
  }'

# Listar citas
curl http://localhost:8000/api/v1/appointments/

# Obtener cita
curl http://localhost:8000/api/v1/appointments/1
```

### Test con pytest
```bash
cd backend
pytest tests/test_appointments.py -v
```

## Troubleshooting

### Email no se envía
1. Verificar `SENDGRID_API_KEY` en `.env`
2. Verificar `SENDGRID_FROM_EMAIL` es email verificado en SendGrid
3. Revisar logs: `tail -f logs/cirujano.log`

### Google Calendar no sincroniza
1. Verificar archivo de credenciales existe
2. Verificar permisos del service account
3. Verificar `GOOGLE_CALENDAR_ID` es correcto
4. Revisar logs para errores

### Validación rechaza formato correcto
1. Nombre: Solo acepta `[a-záéíóúñA-ZÁÉÍÓÚÑ\s]`
2. Email: Requiere al menos `A@B.CD` (5 caracteres)
3. Teléfono: Debe ser `+` seguido de dígitos
4. Fecha: No aceptar fechas pasadas

### Modal no aparece
1. Verificar `showAppointmentModal.value = true`
2. Verificar import de `AppointmentModal` en PageHeader
3. Revisar console para errores de JavaScript

## Seguridad

### Frontend
- Validaciones en cliente-side (no confiar solo en esto)
- HTTPS recomendado en producción
- CORS configurado en backend

### Backend
- Validaciones doble en servidor (Pydantic)
- Sanitización de inputs
- Rate limiting en API (slowapi)
- JWT authentication (si es requerida)
- CORS whitelist configurado

## Performance

### Optimizaciones
- Índices en BD: email, fecha, estado
- Queries async con SQLAlchemy
- Email async con sendgrid
- Google Calendar async con googleapis
- Rate limiting para prevenir abuso

### Límites
- Máximo 1000 citas por request (paginación)
- Máximo 1000 caracteres en mensaje
- Máximo 1 archivo upload de 50MB

## Roadmap Futuro

- [ ] SMS confirmación (Twilio)
- [ ] Recordatorio automático (24h antes)
- [ ] Reschedule/Cancelar cita por email
- [ ] Admin dashboard para gestionar citas
- [ ] Integración con calendario del cliente (iCal)
- [ ] Múltiples calendarios según tipo de servicio
- [ ] Availability slots automáticos
- [ ] Zoom meeting auto-generation

## Contacto & Soporte

**Email:** contacto@cirujanodesintetizadores.cl
**Sitio:** https://www.cirujanodesintetizadores.cl
