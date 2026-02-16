# 🔗 MAPEO PARALELO: ENDPOINTS ↔️ BOTONES ↔️ ACCIONES
**Objetivo:** CADA BOTÓN del frontend DEBE tener su ENDPOINT en backend. CADA ACCIÓN se VALIDA.

---

## 📊 AUDITORÍA PARALELA - RESUMEN EJECUTIVO

| Aspecto | Cantidad | Estado |
|---------|----------|--------|
| **Endpoints Backend** | 165 | ✅ Identificados |
| **Routers** | 28 | ✅ Identificados |
| **Botones/Acciones Frontend** | ~300+ | 🔄 SIENDO AUDITADOS |
| **Checkpoints Necesarios** | ? | 🟡 A DEFINIR |

---

## 📍 ROUTER BACKEND - MAPA DE DOMINIOS

```
backend/app/routers/
├── analytics.py              → Tracking de eventos
├── appointment.py            → Citas/turnos
├── category.py               → Categorías
├── client.py / clients.py    → Clientes ⚠️ ¿Duplicado?
├── contact.py                → Formulario contacto
├── device.py                 → Dispositivos
├── diagnostic.py             → Diagnósticos
├── files.py                  → Manejo de archivos
├── instrument.py             → Instrumentos/herramientas
├── inventory.py              → Inventario
├── invoice.py                → Facturas
├── manuals.py                → Manuales
├── newsletter.py             → Newsletter
├── payments.py               → Pagos
├── photo_requests.py         → Solicitudes de fotos
├── purchase_requests.py      → Solicitudes de compra
├── quotation.py              → Cotizaciones
├── repair.py                 → Reparaciones
├── repair_status.py          → Estados de reparación
├── search.py                 → Búsqueda
├── signature.py              → Firmas digitales
├── stock_movement.py         → Movimientos de stock
├── tickets.py                → Tickets/soporte
├── tools.py                  → Herramientas
├── uploads.py                → Carga de archivos
├── user.py                   → Usuarios
└── warranty.py               → Garantía
```

**TOTAL: 28 routers = ~165 endpoints**

---

## 🎯 DOMINIOS PRINCIPALES - ENDPOINTS POR DOMINIO

### DOMINIO 1: AUTENTICACIÓN & USUARIOS
**Router:** `user.py`

```
Backend Endpoints:
❓ POST   /users/register        → Crear usuario
❓ POST   /users/login           → Login
❓ POST   /users/logout          → Logout
❓ POST   /users/refresh-token   → Refrescar token
❓ GET    /users/me              → Obtener usuario actual
❓ PUT    /users/{id}            → Actualizar perfil
❓ DELETE /users/{id}            → Eliminar cuenta
❓ POST   /users/password-reset  → Solicitar reset
❓ POST   /users/confirm-reset   → Confirmar reset
❓ POST   /users/2fa-setup       → Setup 2FA
```

**Frontend Buttons/Actions:**
```
src/vue/components/auth/LoginForm.vue:
  ✅ Button: "Login" → @submit.prevent="handleLogin"
  ✅ Link: "Register" → router-link to="/register"
  ✅ Link: "Forgot password?" → router-link to="/password-reset"

src/vue/components/auth/RegisterForm.vue:
  ✅ Button: "Register" → @submit.prevent="handleRegister"
  ✅ Toggle Password: @click="showPassword = !showPassword"

src/vue/components/auth/PasswordReset.vue:
  ✅ Button: "Request Reset" → @click="mode = 'request'"
  ✅ Button: "Reset Password" → @click="mode = 'reset'"
  ✅ Form Submit: @submit.prevent="requestReset"
  ✅ Form Submit: @submit.prevent="confirmReset"

src/vue/components/auth/AccountDelete.vue:
  ✅ Button: "Delete Account" → @click="$emit('confirm')"
```

**Validaciones Necesarias:**
- [ ] Login endpoint retorna JWT token
- [ ] JWT se guarda de forma SEGURA (no en localStorage)
- [ ] Refresh token funciona
- [ ] Logout limpia estado
- [ ] Password reset tiene expiración
- [ ] Delete account requiere confirmación
- [ ] 2FA opcional pero implementado

---

### DOMINIO 2: COTIZACIONES/DIAGNÓSTICOS
**Router:** `quotation.py`, `diagnostic.py`

```
Backend Endpoints:
❓ POST   /diagnostics/calculate         → Calcular diagnóstico
❓ GET    /diagnostics/                  → Listar diagnósticos
❓ GET    /diagnostics/{id}              → Obtener diagnóstico
❓ PUT    /diagnostics/{id}              → Actualizar diagnóstico
❓ DELETE /diagnostics/{id}              → Eliminar diagnóstico
❓ GET    /diagnostics/instruments/brands  → Obtener marcas
❓ GET    /diagnostics/instruments/models/{brand_id}  → Obtener modelos
❓ GET    /diagnostics/instruments/{id}  → Obtener instrumento
❓ GET    /diagnostics/faults            → Obtener fallos
❓ GET    /diagnostics/faults/applicable/{instrument_id}  → Fallos aplicables
❓ POST   /quotation/estimate            → Generar cotización
```

**Frontend Actions:**
```
src/vue/components/quotation/InstrumentSelector.vue:
  ✅ Click: selectBrand(brand) → @click="selectBrand(brand)"
  ✅ Click: selectInstrument(instrument) → @click="selectInstrument(instrument)"
  ✅ Button: "Proceed" → @click="proceed"

src/vue/components/quotation/InteractiveInstrumentDiagnostic.vue:
  ✅ Click: selectInstrument(inst) → @click="selectInstrument(inst)"
  ✅ Click: Upload photo → @click="$refs.fileInput.click()"
  ✅ Click: Remove photo → @click="removePhoto(idx)"
  ✅ Click: Next step → @click="nextStep"
  ✅ Click: Previous step → @click="previousStep"
  ✅ Click: Select fault type → @click="selectedFaultType = fault.id"
  ✅ Click: Clear markers → @click="clearMarkers"
  ✅ Click: Undo marker → @click="undoLastMarker"
  ✅ Click: Edit marker → @click="editMarker(marker, idx)"
  ✅ Click: Remove marker → @click.stop="removeMarker(idx)"
  ✅ Click: Submit diagnostic → @click="submitDiagnostic"
  ✅ Button: "Download report" → @click="downloadReport"

src/vue/components/quotation/QuotationResult.vue:
  ✅ Button: "Try again" → @click="$emit('new-quote')"
  ✅ Button: "Schedule" → @click="$emit('schedule')"
```

**Validaciones Necesarias:**
- [ ] GET /diagnostics/instruments/brands retorna datos completos
- [ ] GET /diagnostics/instruments/models/{brand_id} filtra correctamente
- [ ] POST /diagnostics/calculate valida inputs
- [ ] POST /quotation/estimate retorna cotización con desglose
- [ ] Upload de fotos funciona
- [ ] Markers en fotos se guardan
- [ ] Download report genera PDF correcto
- [ ] Workflow paso a paso es fluido

---

### DOMINIO 3: REPARACIONES
**Router:** `repair.py`, `repair_status.py`

```
Backend Endpoints:
❓ POST   /repairs/              → Crear reparación
❓ GET    /repairs/              → Listar reparaciones
❓ GET    /repairs/{id}          → Obtener reparación
❓ PUT    /repairs/{id}          → Actualizar reparación
❓ DELETE /repairs/{id}          → Eliminar reparación
❓ POST   /repairs/{id}/status   → Cambiar estado
❓ GET    /repair-status/        → Listar estados disponibles
❓ POST   /repair-status/        → Crear estado
```

**Frontend Actions:**
```
src/vue/components/dashboard/RepairCard.vue:
  ✅ Button: "View" → @click="$emit('open', repair)"
```

**Validaciones Necesarias:**
- [ ] Estados de reparación son válidos
- [ ] Transiciones de estado permitidas
- [ ] Notificaciones cuando cambia estado
- [ ] Historial de cambios guardado

---

### DOMINIO 4: INVENTARIO
**Router:** `inventory.py`, `stock_movement.py`

```
Backend Endpoints:
❓ GET    /inventory/            → Listar inventario
❓ POST   /inventory/            → Crear item
❓ PUT    /inventory/{id}        → Actualizar item
❓ DELETE /inventory/{id}        → Eliminar item
❓ POST   /stock-movements/      → Registrar movimiento
❓ GET    /stock-movements/      → Listar movimientos
```

**Validaciones Necesarias:**
- [ ] Stock nunca va negativo
- [ ] Movimientos crean audit trail
- [ ] Reportes de inventario son precisos
- [ ] Alertas de bajo stock funcionan

---

### DOMINIO 5: FACTURAS & PAGOS
**Router:** `invoice.py`, `payments.py`

```
Backend Endpoints:
❓ POST   /invoice/              → Crear factura
❓ POST   /invoice/from-repair/{repair_id}  → Generar de reparación
❓ GET    /invoice/              → Listar facturas
❓ GET    /invoice/summary       → Resumen de facturas
❓ GET    /invoice/overdue       → Facturas vencidas
❓ GET    /invoice/{id}          → Obtener factura
❓ GET    /invoice/by-number/{number}  → Buscar por número
❓ POST   /invoice/{id}/items    → Añadir items
❓ DELETE /invoice/{id}/items/{item_id}  → Eliminar item
❓ POST   /invoice/{id}/send     → Enviar factura
❓ POST   /invoice/{id}/mark-viewed  → Marcar como vista
❓ POST   /invoice/{id}/void     → Anular factura
❓ POST   /invoice/{id}/payments → Registrar pago
❓ POST   /invoice/maintenance/mark-overdue  → Marcar vencidas
❓ POST   /payments/             → Crear pago
❓ GET    /payments/             → Listar pagos
❓ GET    /payments/{id}         → Obtener pago
```

**Validaciones Necesarias:**
- [ ] Facturas tienen número secuencial
- [ ] Envío de factura notifica cliente
- [ ] Pagos se aplican correctamente
- [ ] Facturas vencidas se detectan
- [ ] Anulación crea nota de crédito

---

### DOMINIO 6: CITAS/TURNOS
**Router:** `appointment.py`

```
Backend Endpoints:
❓ POST   /appointments/        → Crear cita
❓ GET    /appointments/        → Listar citas
❓ GET    /appointments/{id}    → Obtener cita
❓ PUT    /appointments/{id}    → Actualizar cita
❓ DELETE /appointments/{id}    → Cancelar cita
❓ POST   /appointments/{id}/confirm  → Confirmar cita
```

**Frontend Actions:**
```
src/vue/components/layout/PageHeader.vue:
  ✅ Button: "Open Appointment Modal" → @click="openAppointmentModal"
```

**Validaciones Necesarias:**
- [ ] No se pueden solapar citas
- [ ] Horarios disponibles se muestran correctamente
- [ ] Confirmación enviada a cliente
- [ ] Recordatorios funcionan

---

### DOMINIO 7: CONTACTO & NEWSLETTERS
**Router:** `contact.py`, `newsletter.py`

```
Backend Endpoints:
❓ POST   /contact/              → Enviar mensaje contacto
❓ POST   /newsletter/subscribe  → Suscribir a newsletter
❓ POST   /newsletter/unsubscribe  → Desuscribirse
```

**Validaciones Necesarias:**
- [ ] Emails se envían
- [ ] Campos requeridos se validan
- [ ] Newsletter respeta privacidad

---

### DOMINIO 8: TICKETS/SOPORTE
**Router:** `tickets.py`

```
Backend Endpoints:
❓ POST   /tickets/              → Crear ticket
❓ GET    /tickets/              → Listar tickets
❓ GET    /tickets/{id}          → Obtener ticket
❓ POST   /tickets/{id}/messages → Añadir mensaje
❓ PATCH  /tickets/{id}          → Actualizar ticket (cerrar, etc.)
```

**Validaciones Necesarias:**
- [ ] Tickets se asignan a soporte
- [ ] Notificaciones por mensaje nuevo
- [ ] Historial se mantiene

---

### DOMINIO 9: CARGA DE ARCHIVOS
**Router:** `uploads.py`, `files.py`

```
Backend Endpoints:
❓ POST   /uploads/              → Subir archivo
❓ GET    /files/{file_id}       → Descargar archivo
❓ DELETE /files/{file_id}       → Eliminar archivo
❓ POST   /manuals/upload/{instrument_id}  → Subir manual
```

**Validaciones Necesarias:**
- [ ] Solo tipos de archivo permitidos
- [ ] Límite de tamaño funcionando
- [ ] Virus scan en upload
- [ ] Almacenamiento seguro
- [ ] Limpieza de archivos huérfanos

---

### DOMINIO 10: BÚSQUEDA & ANALYTICS
**Router:** `search.py`, `analytics.py`

```
Backend Endpoints:
❓ GET    /search/?q=...         → Búsqueda global
❓ GET    /analytics/events      → Obtener eventos
❓ POST   /analytics/track       → Registrar evento
```

**Validaciones Necesarias:**
- [ ] Búsqueda es rápida
- [ ] Analytics no ralentiza app
- [ ] Privacidad de datos respetada

---

## ⚠️ PROBLEMAS IDENTIFICADOS

### 🔴 CRÍTICOS

**1. ROUTER DUPLICADO: client.py vs clients.py**
```
Encontrado:
  - /backend/app/routers/client.py
  - /backend/app/routers/clients.py

Pregunta: ¿Cuál es el correcto? ¿Endpoint diferente?
```

**2. FALTA VALIDACIÓN CENTRALIZADA**
```
Problema: Cada endpoint probablemente valida inputs de forma inconsistente
Necesario: Schema de validación común
```

**3. FALTA MANEJO DE ERRORES CONSISTENTE**
```
Problema: ¿Qué pasa si API falla?
Necesario: Error codes estándar, mensajes consistentes
```

**4. SEGURIDAD: JWT EN FRONTEND**
```
Problema: ¿Token se guarda en localStorage?
Necesario: HttpOnly cookies o mejor
```

### 🟡 IMPORTANTES

**5. DOCUMENTACIÓN DE API**
```
Problema: 165 endpoints, ¿hay documentación?
Necesario: Swagger/OpenAPI
```

**6. TESTING DE ENDPOINTS**
```
Problema: ¿Hay tests de API?
Necesario: Integration tests para cada endpoint
```

**7. RATE LIMITING**
```
Problema: ¿Endpoints están protegidos de fuerza bruta?
Necesario: Rate limit por usuario/IP
```

---

## 🔗 MAPEO BOTÓN → ENDPOINT

### TEMPLATE PARA CADA ACCIÓN

```markdown
### [NOMBRE DE ACCIÓN]

**Frontend Component:**
- File: src/vue/components/XXX.vue
- Button: "[Texto del botón]"
- Event: @click="functionName()"

**Función Frontend (composable/store):**
- File: src/composables/useXXX.js
- Function: functionName()
- HTTP Method: POST/GET/PUT/DELETE
- Endpoint Called: /api/path

**Backend Endpoint:**
- File: backend/app/routers/XXX.py
- Route: @router.METHOD("/path")
- Function: handler_function()
- Database Models: Model1, Model2
- Validations: validation1, validation2

**Security Check:**
- [ ] Requiere autenticación?
- [ ] Requiere permiso específico?
- [ ] Input validation?
- [ ] Rate limited?

**Validation Points:**
- [ ] Frontend valida inputs
- [ ] Backend valida inputs
- [ ] Respuesta HTTP correcta
- [ ] Estado actualizado en frontend
```

---

## 📋 PRÓXIMOS PASOS - AUDITORÍA COMPLETA

**PARALELO 1: Mapear TODOS los botones**
```
Comando: grep -r "@click\|@submit" src/vue/components --include="*.vue" > botones.txt
Tarea: Crear entrada para CADA botón con su endpoint
```

**PARALELO 2: Verificar TODOS los endpoints**
```
Comando: grep -r "@router\." backend/app/routers --include="*.py" > endpoints.txt
Tarea: Crear entrada para CADA endpoint con su botón correspondiente
```

**PARALELO 3: Definir CHECKPOINTS**
```
¿Cuándo sincronizan los devs?
- Después de cada componente?
- Después de cada router?
- Después de cada fase?
```

**PARALELO 4: Tests de integración**
```
Para CADA acción:
- Test: botón dispara función
- Test: función llama endpoint correcto
- Test: endpoint retorna respuesta correcta
- Test: frontend actualiza estado
```

---

## ✅ CHECKLIST - ANTES DE EMPEZAR TRABAJO PARALELO

- [ ] ¿Todos los botones están mapeados a endpoints?
- [ ] ¿Todos los endpoints tienen botón correspondiente?
- [ ] ¿Qué botones NO TIENEN endpoint? (nueva funcionalidad)
- [ ] ¿Qué endpoints NO TIENEN botón? (dead code?)
- [ ] ¿Validación es consistente?
- [ ] ¿Errores se manejan igual?
- [ ] ¿Autenticación funciona?
- [ ] ¿Permisos están correctos?
- [ ] ¿Tests de integración pasan?

---

## 🎯 DECISIÓN AHORA

**Necesito entender el alcance de la auditoría:**

1. ¿Auditar TODOS los 300+ botones? (⏱️ ~4 horas)
2. ¿O solo los 10 DOMINIOS principales? (⏱️ ~2 horas)
3. ¿O crear TEMPLATE y que lo rellenes tú? (⏱️ ~30 min)

**¿Cuál prefieres?**
