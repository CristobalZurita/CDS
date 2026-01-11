# Google Calendar Credentials Setup

## Overview
Este directorio contiene las credenciales necesarias para que el backend sincronice citas con Google Calendar.

## Estructura

```
credentials/
├── .gitignore                              # Git ignore para credentials
├── google-calendar-credentials.example.json # Ejemplo de formato
└── google-calendar-credentials.json        # REAL CREDENTIALS (no commitear)
```

## Cómo Obtener Credenciales

### Paso 1: Crear Proyecto en Google Cloud Console

1. Ir a [Google Cloud Console](https://console.cloud.google.com/)
2. Click en el dropdown de proyecto en la parte superior
3. Click en "NEW PROJECT"
4. Nombre: "Cirujano de Sintetizadores"
5. Click en "CREATE"
6. Esperar a que se cree el proyecto

### Paso 2: Habilitar Google Calendar API

1. En la barra de búsqueda, buscar "Google Calendar API"
2. Click en "Google Calendar API"
3. Click en "ENABLE"

### Paso 3: Crear Service Account

1. Click en "Credenciales" en el sidebar izquierdo
2. Click en "CREATE CREDENTIALS" 
3. Seleccionar "Service Account"
4. Rellenar:
   - Service account name: "cirujano-calendar"
   - Description: "Service account for appointment calendar sync"
5. Click "CREATE AND CONTINUE"
6. Saltar pasos 2 y 3 (opcional)
7. Click "DONE"

### Paso 4: Generar JSON Key

1. En la tabla de Service Accounts, click en el email del service account creado
2. Click en la pestaña "KEYS"
3. Click en "ADD KEY" > "Create new key"
4. Seleccionar "JSON"
5. Click "CREATE"
6. El archivo JSON se descargará automáticamente

### Paso 5: Copiar Credenciales

1. Renombrar el archivo descargado a `google-calendar-credentials.json`
2. Copiar el archivo a este directorio: `backend/credentials/`
3. **⚠️ IMPORTANTE**: NO commitear este archivo a Git

```bash
# Desde la raíz del proyecto
cp ~/Downloads/your-project-*.json backend/credentials/google-calendar-credentials.json
```

### Paso 6: Compartir Calendario

1. Ir a [Google Calendar](https://calendar.google.com)
2. Click derecho en tu calendario personal
3. Click en "Settings and sharing"
4. Scroll hasta "Share with specific people"
5. Click en "Add people"
6. Copiar el email del service account (del JSON: `client_email`)
7. Pegar y seleccionar permisos: "Make changes to events"
8. Click "Send"

### Paso 7: Obtener Calendar ID

1. En Google Calendar, click en tu calendario personal
2. Click en los tres puntos > "Settings"
3. En la pestaña "Integrate calendar", copiar "Calendar ID"
4. Guardar en `.env`:
   ```
   GOOGLE_CALENDAR_ID=abc123xyz789@group.calendar.google.com
   ```
   O dejar como `primary` para usar el calendario por defecto

## Variables de Entorno

Agregar al archivo `.env`:

```dotenv
# Google Calendar Integration
GOOGLE_CALENDAR_CREDENTIALS_FILE=./credentials/google-calendar-credentials.json
GOOGLE_CALENDAR_ID=primary
# O con Calendar ID específico:
# GOOGLE_CALENDAR_ID=abc123xyz789@group.calendar.google.com
```

## Verificación

Para verificar que funciona:

```bash
cd backend
python -c "
from backend.app.services.google_calendar_service import get_calendar_service
service = get_calendar_service()
if service.service:
    print('✓ Google Calendar service initialized successfully')
else:
    print('✗ Error initializing Google Calendar service')
"
```

## Troubleshooting

### Error: "File not found"
- Verificar que el archivo existe en `backend/credentials/google-calendar-credentials.json`
- Verificar que la variable `GOOGLE_CALENDAR_CREDENTIALS_FILE` es correcta en `.env`

### Error: "Invalid credentials"
- Verificar que el JSON descargado es válido
- Verificar que el service account tiene permisos en Google Calendar API

### Error: "Permission denied"
- Verificar que se compartió el calendario con el email del service account
- Verificar que el service account tiene rol "Editor"

### Eventos no se sincronizan
- Verificar logs: `tail -f logs/cirujano.log`
- Revisar que `GOOGLE_CALENDAR_ID` es correcto
- Verificar respuesta de API en endpoint test

## Security Best Practices

✓ Archivo `.gitignore` previene commit accidental
✓ Archivo de ejemplo muestra estructura segura
✓ Credenciales no se exportan en código fuente
✓ Usar service account en lugar de OAuth para backend
✓ Rotar credentials regularmente en producción

## Referencia

- [Google Cloud Console](https://console.cloud.google.com/)
- [Google Calendar API Docs](https://developers.google.com/calendar/api/guides/overview)
- [Service Account Setup](https://cloud.google.com/docs/authentication/getting-started)
- [Python Client Library](https://github.com/googleapis/google-api-python-client)
