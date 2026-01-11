# 🔧 AUDITORÍA TÉCNICA COMPLETA

## Cirujano de Sintetizadores

### Sistema de Gestión para Taller de Reparación de Instrumentos Electrónicos

**Fecha:** Enero 2026
**Dominio:** www.cirujanodesintetizadores.cl
**Versión del Proyecto:** 2.0.1

---

# ÍNDICE

1. [Resumen Ejecutivo](#1-resumen-ejecutivo)
2. [Estado Actual del Proyecto](#2-estado-actual-del-proyecto)
3. [Análisis de Arquitectura](#3-análisis-de-arquitectura)
4. [Auditoría de Seguridad](#4-auditoría-de-seguridad)
5. [Funcionalidades Implementadas vs Requeridas](#5-funcionalidades-implementadas-vs-requeridas)
   - 5.1 Sistema de Cotización Inteligente
   - 5.2 Sistema de Gestión de Reparaciones
   - 5.3 Sistema de Carrito, Tracking y Pagos
   - 5.4 Sistema de Tracking de Reparaciones (Timeline)
   - 5.5 Políticas y Términos
   - 5.6 Sistema de Tickets y Atención Automatizada
   - 5.7 Detección Automática de Instrumentos (IA)
   - 5.8 Resumen de Integraciones API
   - 5.9 STREAMING EN VIVO (Diferenciador ÚNICO)
   - 5.10 Portfolio AUTOMÁTICO
   - 5.11 Flujo de Trabajo del Técnico
   - 5.12 Sistema de Cotización JUSTA
   - 5.13 Políticas y Términos
6. [Plan de Implementación](#6-plan-de-implementación)
7. [Integración con Hosting cPanel](#7-integración-con-hosting-cpanel)
8. [SEO, Analytics y Marketing](#8-seo-analytics-y-marketing)
9. [Presupuesto de Desarrollo](#9-presupuesto-de-desarrollo)
10. [Roadmap de Implementación](#10-roadmap-de-implementación)

---

# 1. RESUMEN EJECUTIVO

## Tu Visión (Lo que quieres)

Un sistema integral donde:

1. **Cliente sin cuenta** puede cotizar en línea seleccionando marca → modelo → fallas específicas
2. **Sistema de diagnóstico visual** donde el cliente marca en una imagen interactiva qué está malo
3. **Cuestionario inteligente "aguas abajo"** - si marca "no prende", se desactivan opciones posteriores
4. **Cotización aproximada** con disclaimer visible (PRECIOS SON APROXIMADOS)
5. **Creación de cuenta** para agendar reparación
6. **Panel del técnico** para gestionar fichas, subir fotos, actualizar estados
7. **Panel del cliente** para ver avance de su reparación
8. **Carrito de repuestos interno** - se habilita si se necesita, lo activa técnico o cliente
9. **Sistema de tracking tipo DHL** - estados, fechas, fotos, todo en timeline
10. **Integración con APIs de tracking** - AliExpress, 17track, DHL, Correos Chile, etc.
11. **Sistema de tickets** con tiempos de respuesta (SLA) y escalado automático
12. **Respuestas automáticas inteligentes** - clasificación por IA, respuestas inmediatas
13. **La web se maneja sola** - automatización máxima, tú solo ves lo urgente
14. **Detección de instrumento por IA** - sube foto, el sistema detecta marca/modelo
15. **Drag & Drop** para subir imágenes + opción de buscar en PC
16. **Todo en base de datos** - historial completo por cliente
17. **Notificaciones automáticas** por email/SMS en cada cambio de estado
18. **Políticas claras** de bodega, retiro, responsabilidades
19. **Integración con Google Calendar** para agendamiento
20. **🎬 STREAMING EN VIVO** - 6-9 cámaras, cliente paga y VE su equipo siendo reparado
21. **Canal YouTube automático** - videos se publican SOLOS después del stream
22. **Portfolio automático** - "Últimos trabajos" se genera SOLO con fotos que subiste
23. **Flujo de trabajo en vivo** - web abierta mientras reparas, todo desde ahí
24. **Cotización JUSTA** - nunca cobrar más del 50% del valor del instrumento
25. **CDS.cl = Central autónoma 24/7** - funciona mientras reparas o duermes

## Estado Actual

| Componente                            | Estado                        | Completitud |
| ------------------------------------- | ----------------------------- | ----------- |
| Backend FastAPI                       | ✅ Funcional                  | 60%         |
| Frontend Vue 3                        | ✅ Funcional                  | 55%         |
| Base de datos                         | ✅ Estructura básica         | 50%         |
| Autenticación JWT                    | ✅ Implementado               | 80%         |
| Sistema de cotización IA             | 🟡 Parcial                    | 30%         |
| Diagnóstico visual interactivo       | ❌ No existe                  | 0%          |
| Carrito de repuestos interno          | ❌ No existe                  | 0%          |
| Sistema de tracking (tipo DHL)        | ❌ No existe                  | 0%          |
| Integración APIs tracking            | ❌ No existe                  | 0%          |
| Sistema de tickets                    | ❌ No existe                  | 0%          |
| Automatización / Respuestas auto     | ❌ No existe                  | 0%          |
| Detección de instrumento por IA      | ❌ No existe                  | 0%          |
| Drag & Drop de imágenes              | ❌ No existe                  | 0%          |
| **🎬 Streaming en vivo**        | ❌ No existe (hardware listo) | 0%          |
| **Portfolio automático**       | ❌ No existe                  | 0%          |
| **Flujo trabajo técnico**      | ❌ No existe                  | 0%          |
| **Cotización justa (% valor)** | ❌ No existe                  | 0%          |
| **YouTube auto-publicación**   | ❌ No existe                  | 0%          |
| Sistema de pagos (Flow.cl)            | ❌ No existe                  | 0%          |
| Integración Google Calendar          | ❌ No existe                  | 0%          |
| Políticas y términos                | ❌ No existe                  | 0%          |
| Scraper precios mercado               | ❌ No existe                  | 0%          |
| SSL/Seguridad producción             | ❌ Pendiente                  | 0%          |

---

# 2. ESTADO ACTUAL DEL PROYECTO

## 2.1 Backend (FastAPI)

### Lo que ESTÁ implementado:

```
✅ Estructura base FastAPI con lifespan
✅ CORS configurado para desarrollo
✅ Modelos SQLAlchemy: User, Instrument, Repair, Brand, Category
✅ Sistema de autenticación JWT básico
✅ Endpoints básicos: /api/v1/brands, /api/v1/instruments, /api/v1/auth
✅ Sistema de estados de reparación (7 estados)
✅ Configuración de multiplicadores de precio
```

### Lo que FALTA:

```
❌ Endpoint de cotización inteligente
❌ Análisis de imágenes para diagnóstico
❌ Sistema de agendamiento con calendario
❌ Envío de emails transaccionales
❌ Endpoint para subir fotos de reparaciones
❌ Sistema de notificaciones push/email
❌ Integración con pasarela de pagos
❌ API para políticas y términos
❌ Rate limiting y protección DDoS
❌ Logs estructurados para producción
```

## 2.2 Frontend (Vue 3)

### Lo que ESTÁ implementado:

```
✅ SPA con Vue Router
✅ Estado global con Pinia
✅ Rutas protegidas por autenticación
✅ Layouts: Master, páginas públicas y privadas
✅ Componentes básicos de dashboard
✅ Sistema de login/registro
✅ Panel admin básico (inventario, clientes, reparaciones)
```

### Lo que FALTA:

```
❌ Buscador inteligente marca → modelo
❌ Componente de diagnóstico visual interactivo
❌ Cuestionario dinámico de fallas
❌ Visualización de cotización en tiempo real
❌ Timeline de seguimiento de reparación
❌ Sistema de carga de fotos del cliente
❌ Carrito de pagos para repuestos
❌ Integración con Google Calendar widget
❌ Chat/WhatsApp widget
❌ Página de políticas y términos
❌ PWA para acceso móvil offline
```

## 2.3 Base de Datos

### Modelos actuales:

```sql
-- Existentes
users (id, email, password, role, created_at)
instruments (id, brand_id, name, model, type, year, valor_estimado, image)
repairs (id, client_id, instrument_id, status, estimated_price, notes)
brands (id, name)
categories (id, name)
diagnostics (id, repair_id, ...)
```

### Modelos FALTANTES:

```sql
-- Necesarios
instrument_components (id, instrument_id, type, name, position_x, position_y, clickable_area)
fault_templates (id, component_type, fault_name, base_price, labor_hours)
quotations (id, user_id, instrument_id, components_data, total_estimated, status)
appointments (id, user_id, repair_id, datetime, google_calendar_id, status)
payments (id, user_id, repair_id, amount, payment_method, transaction_id, status)
repair_photos (id, repair_id, url, uploaded_by, stage)
notifications (id, user_id, type, message, read, created_at)
policies (id, type, title, content, version, active)
audit_logs (id, user_id, action, entity, entity_id, details, created_at)
```

---

# 3. ANÁLISIS DE ARQUITECTURA

## 3.1 Arquitectura Actual

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Vue 3 SPA     │────▶│  FastAPI        │────▶│   SQLite        │
│   (Vite)        │     │  Backend        │     │   (desarrollo)  │
│   Puerto 5173   │     │  Puerto 8000    │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## 3.2 Arquitectura RECOMENDADA para Producción

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLOUDFLARE (CDN + WAF)                       │
│                    SSL/TLS + DDoS Protection + Cache                 │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         cPanel Hosting                               │
│  ┌─────────────────┐     ┌─────────────────┐     ┌───────────────┐ │
│  │   Vue 3 Build   │     │   FastAPI       │     │    MySQL      │ │
│  │   (Static)      │     │   (Passenger)   │     │   5GB limit   │ │
│  │   /public_html  │     │   Python App    │     │   2 databases │ │
│  └─────────────────┘     └─────────────────┘     └───────────────┘ │
│                                                                      │
│  ┌─────────────────┐     ┌─────────────────┐     ┌───────────────┐ │
│  │   Cron Jobs     │     │   Email SMTP    │     │   File        │ │
│  │   (tareas)      │     │   10 cuentas    │     │   Storage     │ │
│  └─────────────────┘     └─────────────────┘     └───────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              ▼                     ▼                     ▼
    ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
    │ Google Calendar │   │   Transbank/    │   │   Cloudinary    │
    │      API        │   │   Flow.cl       │   │   (imágenes)    │
    └─────────────────┘   └─────────────────┘   └─────────────────┘
```

## 3.3 Limitaciones de tu Hosting Actual

| Recurso | Límite          | Implicación                                                                         |
| ------- | ---------------- | ------------------------------------------------------------------------------------ |
| Espacio | 5 GB             | Suficiente para código, pero las imágenes deben ir a servicio externo (Cloudinary) |
| MySQL   | 2 bases de datos | Una para producción, una para staging                                               |
| Emails  | 10 cuentas       | Suficiente (noreply@, info@, soporte@, etc.)                                         |
| SSL     | Incluido gratis  | ✅ Perfecto                                                                          |
| Python  | Via Passenger    | Requiere configuración especial                                                     |

---

# 4. AUDITORÍA DE SEGURIDAD

## 4.1 Vulnerabilidades CRÍTICAS Detectadas

### 🔴 CRÍTICO - Secretos en código

**Archivo:** `config.py`

```python
# ❌ PELIGROSO - Secretos hardcodeados
secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
jwt_secret: str = os.getenv("JWT_SECRET", "your-jwt-secret-change-in-production")
```

**Solución:**

```python
# ✅ CORRECTO - Sin valores por defecto peligrosos
secret_key: str = os.getenv("SECRET_KEY")
jwt_secret: str = os.getenv("JWT_SECRET")

if not secret_key or not jwt_secret:
    raise ValueError("SECRET_KEY y JWT_SECRET son obligatorios en producción")
```

### 🔴 CRÍTICO - CORS muy permisivo

**Archivo:** `config.py`

```python
# ❌ Solo para desarrollo
allowed_origins: list = [
    "http://localhost:3000",
    "http://localhost:5173",
]
```

**Solución:**

```python
# ✅ Para producción
allowed_origins: list = os.getenv("ALLOWED_ORIGINS", "").split(",")
# En .env: ALLOWED_ORIGINS=https://cirujanodesintetizadores.cl,https://www.cirujanodesintetizadores.cl
```

### 🟡 MEDIO - Sin rate limiting

**Problema:** Cualquiera puede hacer miles de requests por segundo.

**Solución:** Agregar slowapi

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/api/v1/cotizar")
@limiter.limit("10/minute")
async def cotizar(request: Request):
    ...
```

### 🟡 MEDIO - Sin validación de archivos

**Problema:** No hay validación de imágenes subidas.

**Solución:**

```python
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

async def validate_image(file: UploadFile):
    # Verificar extensión
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, "Formato no permitido")
  
    # Verificar tamaño
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(400, "Archivo muy grande (max 5MB)")
  
    # Verificar que realmente es una imagen
    import imghdr
    if imghdr.what(None, h=content) not in ["jpeg", "png", "webp"]:
        raise HTTPException(400, "Archivo no es una imagen válida")
```

## 4.2 Checklist de Seguridad para Producción

| Item                             | Estado        | Prioridad |
| -------------------------------- | ------------- | --------- |
| Secretos en variables de entorno | ❌ Pendiente  | CRÍTICA  |
| CORS restringido a dominio       | ❌ Pendiente  | CRÍTICA  |
| HTTPS forzado                    | ❌ Pendiente  | CRÍTICA  |
| Rate limiting                    | ❌ Pendiente  | ALTA      |
| Validación de uploads           | ❌ Pendiente  | ALTA      |
| Headers de seguridad             | ❌ Pendiente  | ALTA      |
| SQL injection protection         | ✅ SQLAlchemy | OK        |
| XSS protection                   | 🟡 Parcial    | MEDIA     |
| CSRF protection                  | ❌ Pendiente  | MEDIA     |
| Password hashing                 | ✅ bcrypt     | OK        |
| JWT expiration                   | ✅ 30 min     | OK        |
| Audit logging                    | ❌ Pendiente  | MEDIA     |
| Backup automático               | ❌ Pendiente  | ALTA      |

---

# 5. FUNCIONALIDADES: IMPLEMENTADAS vs REQUERIDAS

## 5.1 Sistema de Cotización Inteligente

### Tu visión:

> "Busco mi instrumento por marca y modelo, muestra foto, el cliente marca lo malo en una interfaz visual, cuestionario aguas abajo, cotización aproximada"

### Estado actual: 🟡 30% implementado

**Lo que existe:**

- Catálogo de instrumentos con marcas
- Valor estimado por instrumento
- Multiplicadores de precio por categoría

**Lo que falta:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLUJO DE COTIZACIÓN                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. SELECCIÓN DE INSTRUMENTO                                    │
│     ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│     │ Marca ▼     │ ─▶ │ Modelo ▼    │ ─▶ │ [FOTO]      │      │
│     │ KORG        │    │ microKORG   │    │ Si no hay,  │      │
│     │ ROLAND      │    │ MS-2000     │    │ subir foto  │      │
│     │ YAMAHA      │    │ ...         │    │             │      │
│     └─────────────┘    └─────────────┘    └─────────────┘      │
│                                                                 │
│  2. DIAGNÓSTICO VISUAL INTERACTIVO                              │
│     ┌─────────────────────────────────────────────────────┐    │
│     │  [Imagen del instrumento con áreas clickeables]     │    │
│     │                                                     │    │
│     │   ┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐       │    │
│     │   │ ● │ ● │ ● │ ● │ ● │ ● │ ● │ ● │ ● │ ● │ Teclas │    │
│     │   └───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘       │    │
│     │                                                     │    │
│     │   ○ Botón 1  ○ Botón 2  ○ Botón 3  [Pote 1] [Pote2]│    │
│     │   ● = Seleccionado como malo                       │    │
│     └─────────────────────────────────────────────────────┘    │
│                                                                 │
│  3. CUESTIONARIO AGUAS ABAJO                                    │
│     ┌─────────────────────────────────────────────────────┐    │
│     │ ¿El equipo enciende?                                │    │
│     │   ○ Sí  ● No ──▶ [DESACTIVA resto de preguntas]    │    │
│     │                                                     │    │
│     │ ¿Produce sonido? (desactivado)                      │    │
│     │ ¿Las teclas responden? (desactivado)                │    │
│     └─────────────────────────────────────────────────────┘    │
│                                                                 │
│  4. RESULTADO                                                   │
│     ┌─────────────────────────────────────────────────────┐    │
│     │  ⚠️ PRECIO APROXIMADO: $45.000 - $85.000 CLP       │    │
│     │                                                     │    │
│     │  ╔═══════════════════════════════════════════════╗ │    │
│     │  ║ IMPORTANTE: Este valor es REFERENCIAL.        ║ │    │
│     │  ║ El precio final se confirma tras revisión     ║ │    │
│     │  ║ presencial en el taller.                      ║ │    │
│     │  ╚═══════════════════════════════════════════════╝ │    │
│     │                                                     │    │
│     │  [AGENDAR CITA]  [GUARDAR COTIZACIÓN]              │    │
│     └─────────────────────────────────────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5.1.1 Lógica de Precios y Cobros (REGLAS DE NEGOCIO)

**IMPORTANTE:** El cliente NO debe ver precios del instrumento por todos lados. La información de valor de mercado es solo para uso interno del técnico.

#### Lo que ve el CLIENTE vs lo que ve el TÉCNICO

| Información                     | Cliente ve          | Técnico ve        |
| -------------------------------- | ------------------- | ------------------ |
| Foto del instrumento             | ✅ Sí              | ✅ Sí             |
| Valor de mercado del instrumento | ❌ NO               | ✅ Sí             |
| Tier/Categoría del instrumento  | ❌ NO               | ✅ Sí             |
| Cotización de REPARACIÓN       | ✅ Sí (aproximada) | ✅ Sí (detallada) |
| Costo de presupuesto ($20.000)   | ✅ Sí              | ✅ Sí             |
| Cobro mínimo (10% del valor)    | ❌ NO               | ✅ Sí (calculado) |
| Precios de Reverb/eBay/Thomann   | ❌ NO               | ✅ Sí             |

#### Sistema de Tiers (Clasificación Interna)

```python
TIER_RANGES = {
    'legendary': {
        'min': 2000000,
        'max': 8000000,
        'min_charge_percent': 10,
        'description': 'Sintetizador legendario profesional (Minimoog, Prophet-5 vintage)'
    },
    'professional': {
        'min': 1000000,
        'max': 4000000,
        'min_charge_percent': 10,
        'description': 'Sintetizador profesional (Access Virus TI, Nord Lead)'
    },
    'historic': {
        'min': 1500000,
        'max': 5000000,
        'min_charge_percent': 10,
        'description': 'Sintetizador histórico vintage con valor de colección'
    },
    'boutique': {
        'min': 500000,
        'max': 3000000,
        'min_charge_percent': 10,
        'description': 'Sintetizador boutique, ediciones limitadas'
    },
    'specialized': {
        'min': 400000,
        'max': 2000000,
        'min_charge_percent': 10,
        'description': 'Sintetizador especializado para usos específicos'
    },
    'standard': {
        'min': 300000,
        'max': 1500000,
        'min_charge_percent': 10,
        'description': 'Sintetizador estándar (mayoría de equipos)'
    }
}
```

#### Reglas de Cobro

```
┌─────────────────────────────────────────────────────────────────┐
│                    LÓGICA DE COBROS                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. PRESUPUESTO (siempre se cobra)                              │
│     ┌─────────────────────────────────────────────────────┐    │
│     │  Costo: $20.000 CLP                                 │    │
│     │  - ABONABLE: Se descuenta del total si repara       │    │
│     │  - NO REEMBOLSABLE: Queda como pago por diagnóstico │    │
│     └─────────────────────────────────────────────────────┘    │
│                                                                 │
│  2. COBRO MÍNIMO POR REPARACIÓN                                 │
│     ┌─────────────────────────────────────────────────────┐    │
│     │  Fórmula: 10% del valor de mercado del instrumento  │    │
│     │                                                     │    │
│     │  Ejemplo:                                           │    │
│     │  - Instrumento vale $100.000 → Mínimo $10.000       │    │
│     │  - Instrumento vale $500.000 → Mínimo $50.000       │    │
│     │  - Instrumento vale $2.000.000 → Mínimo $200.000    │    │
│     │                                                     │    │
│     │  Este mínimo es solo por "tocar" el equipo.         │    │
│     │  La reparación real puede costar más.               │    │
│     └─────────────────────────────────────────────────────┘    │
│                                                                 │
│  3. COTIZACIÓN FINAL                                            │
│     ┌─────────────────────────────────────────────────────┐    │
│     │  = MAX(cobro_mínimo, costo_real_reparación)         │    │
│     │  + repuestos (si aplica)                            │    │
│     │  + gestión/importación (si aplica)                  │    │
│     │  - $20.000 (presupuesto ya pagado)                  │    │
│     └─────────────────────────────────────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### Scraper de Precios (Implementación Pendiente)

Para mantener valores actualizados, se requiere un sistema que consulte:

| Fuente                    | Tipo                | Prioridad | Frecuencia sugerida |
| ------------------------- | ------------------- | --------- | ------------------- |
| **Reverb**          | Usado/Nuevo         | ALTA      | Semanal             |
| **eBay**            | Usado internacional | ALTA      | Semanal             |
| **Thomann**         | Nuevo Europa        | MEDIA     | Mensual             |
| **Sweetwater**      | Nuevo USA           | MEDIA     | Mensual             |
| **MercadoLibre CL** | Local               | ALTA      | Semanal             |

**Modelo propuesto para almacenar precios:**

```python
class InstrumentPriceHistory(Base):
    __tablename__ = "instrument_price_history"
  
    id = Column(Integer, primary_key=True)
    instrument_id = Column(Integer, ForeignKey("instruments.id"))
  
    # Fuente del precio
    source = Column(String(50))  # 'reverb', 'ebay', 'thomann', etc.
    source_url = Column(String(500))
  
    # Precio
    price = Column(Integer)  # en CLP
    original_currency = Column(String(10))  # 'USD', 'EUR', 'CLP'
    original_price = Column(Integer)
  
    # Condición
    condition = Column(String(50))  # 'new', 'used_excellent', 'used_good', 'used_fair'
  
    # Disponibilidad en Chile
    available_in_chile = Column(Boolean, default=False)
    import_cost_estimate = Column(Integer, nullable=True)  # Costo estimado de importación
  
    fetched_at = Column(DateTime, default=datetime.utcnow)

class InstrumentValuation(Base):
    """Valor calculado actual del instrumento (promedio de fuentes)"""
    __tablename__ = "instrument_valuations"
  
    id = Column(Integer, primary_key=True)
    instrument_id = Column(Integer, ForeignKey("instruments.id"), unique=True)
  
    # Valores calculados
    min_value = Column(Integer)
    max_value = Column(Integer)
    avg_value = Column(Integer)
  
    # Cobro mínimo calculado
    min_charge = Column(Integer)  # 10% de avg_value
  
    # Disponibilidad
    available_locally = Column(Boolean)
    import_cost = Column(Integer, nullable=True)
  
    last_updated = Column(DateTime, default=datetime.utcnow)
```

**Endpoint para el técnico (dashboard interno):**

```python
@router.get("/admin/instruments/{instrument_id}/valuation")
async def get_instrument_valuation(
    instrument_id: int,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Retorna información de valor de mercado.
    SOLO PARA ADMIN/TÉCNICO - El cliente NO debe ver esto.
    """
    return {
        "instrument_id": instrument_id,
        "market_value": {
            "min": 450000,
            "max": 650000,
            "avg": 550000,
            "currency": "CLP"
        },
        "sources": [
            {"source": "reverb", "price": 520000, "condition": "used_good", "url": "..."},
            {"source": "ebay", "price": 580000, "condition": "used_excellent", "url": "..."},
        ],
        "min_charge": 55000,  # 10% de avg
        "tier": "standard",
        "available_in_chile": True,
        "import_estimate": None,
        "last_updated": "2026-01-06T12:00:00Z"
    }
```

## 5.2 Sistema de Gestión de Reparaciones

### Tu visión:

> "Creo ficha, se manda mail automático, cliente ve avance, yo actualizo estado"

### Estado actual: 🟡 50% implementado

**Lo que existe:**

- Modelo Repair con 7 estados
- CRUD básico de reparaciones
- Relación cliente-reparación

**Lo que falta:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLUJO DE REPARACIÓN                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  TÉCNICO (Dashboard Admin)              CLIENTE (Su panel)      │
│  ─────────────────────────             ───────────────────      │
│                                                                 │
│  1. Recibe equipo físicamente                                   │
│     │                                                           │
│     ▼                                                           │
│  2. Crea/busca usuario                                          │
│     │  ┌──────────────────────┐                                │
│     │  │ RUT: 12.345.678-9   │                                 │
│     │  │ Si existe ─▶ asociar │                                │
│     │  │ Si no ─▶ crear nuevo │                                │
│     │  └──────────────────────┘                                │
│     │                                                           │
│     ▼                                                           │
│  3. Crea ficha CDS-001            ──▶  📧 Email: "Tu equipo    │
│     │ - Instrumento                     fue recibido"          │
│     │ - Fotos de ingreso                                       │
│     │ - Fallas reportadas               👁️ Ve ficha en su     │
│     │ - Firma digital cliente           dashboard              │
│     │                                                           │
│     ▼                                                           │
│  4. Diagnóstico técnico           ──▶  📧 "Diagnóstico listo"  │
│     │ - Fotos internas                                         │
│     │ - Fallas encontradas              💰 Ve cotización       │
│     │ - Cotización final                   confirmada          │
│     │                                                           │
│     ▼                                                           │
│  5. Cliente aprueba/rechaza       ◀──  ✅ Aprueba en web       │
│     │                                  ❌ Rechaza (retira)     │
│     │                                                           │
│     ▼                                                           │
│  6. En reparación                 ──▶  📧 "En reparación"      │
│     │ - Actualiza avance %                                     │
│     │ - Notas técnicas                  📊 Ve progreso         │
│     │                                      en tiempo real      │
│     │                                                           │
│     ▼                                                           │
│  7. Esperando repuestos           ──▶  📧 "Esperando partes"   │
│     │ (si aplica)                       🛒 Puede pagar         │
│     │                                      repuestos extra     │
│     │                                                           │
│     ▼                                                           │
│  8. Completado                    ──▶  📧 "Listo para retiro"  │
│     │                                                           │
│     │                                   📍 Ve dirección        │
│     ▼                                      y horarios          │
│  9. Entregado                                                   │
│     │ - Firma de retiro                                        │
│     │ - Garantía activada                                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 5.3 Sistema de Carrito, Tracking y Pagos

### Tu visión:

> "Carrito se habilita si se necesita, lo activo yo o el cliente. Todo conectado con APIs de tracking internacional. CDS.cl es una central de atención y difusión de imagen."

### Estado actual: ❌ 0% implementado

### 5.3.1 Concepto: CDS.cl como Central de Operaciones

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│                    CDS.CL = CENTRAL DE OPERACIONES                      │
│                                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │   IMAGEN    │  │  ATENCIÓN   │  │  GESTIÓN    │  │  TRACKING   │   │
│  │   DE MARCA  │  │  AL CLIENTE │  │  INTERNA    │  │  GLOBAL     │   │
│  ├─────────────┤  ├─────────────┤  ├─────────────┤  ├─────────────┤   │
│  │ • Landing   │  │ • Cotizar   │  │ • Dashboard │  │ • AliExpress│   │
│  │ • Portfolio │  │ • Agendar   │  │   técnico   │  │ • DHL       │   │
│  │ • Redes     │  │ • Ver estado│  │ • Fichas    │  │ • 17track   │   │
│  │ • Blog      │  │ • Pagar     │  │ • Inventario│  │ • Correos CL│   │
│  │ • Contacto  │  │ • Historial │  │ • Reportes  │  │ • FedEx     │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
│                                                                         │
│                         TODO EN UN SOLO LUGAR                           │
│                         TODO EN BASE DE DATOS                           │
│                         TODO CON HISTORIAL                              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.3.2 Flujo del Carrito de Repuestos

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    FLUJO COMPLETO DE REPUESTOS                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ¿QUIÉN ACTIVA EL CARRITO?                                              │
│  ─────────────────────────                                              │
│                                                                         │
│  Opción A: TÉCNICO                    Opción B: CLIENTE                 │
│  ─────────────────                    ────────────────                  │
│  • Detecta necesidad                  • Desde su dashboard              │
│  • Agrega item con precio             • Solicita repuesto               │
│  • Cliente recibe notificación        • Técnico valida y cotiza         │
│                                                                         │
│                         ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  CARRITO ACTIVADO (visible en dashboard del cliente)            │   │
│  │                                                                  │   │
│  │  Reparación: CDS-047 - KORG MS-2000                             │   │
│  │  ────────────────────────────────────────────────────────────── │   │
│  │  □ Potenciómetro Alps 10K       $3.500    [AliExpress]          │   │
│  │    └─ Tiempo estimado: 25-40 días                               │   │
│  │  □ Encoder rotativo 24 pulsos   $2.800    [AliExpress]          │   │
│  │    └─ Tiempo estimado: 25-40 días                               │   │
│  │  □ Gestión e importación        $5.000                          │   │
│  │  ────────────────────────────────────────────────────────────── │   │
│  │  SUBTOTAL:                      $11.300                         │   │
│  │                                                                  │   │
│  │  [APROBAR Y PAGAR]    [TENGO DUDAS - CONTACTAR]                 │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                         │                                               │
│                         ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  PAGO (Flow.cl)                                                  │   │
│  │  • Tarjeta débito/crédito                                       │   │
│  │  • Transferencia                                                 │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                         │                                               │
│                         ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  TÉCNICO COMPRA EL REPUESTO                                      │   │
│  │  • Ingresa número de orden                                       │   │
│  │  • Ingresa tracking number                                       │   │
│  │  • Sistema conecta con API de tracking                          │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                         │                                               │
│                         ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  TRACKING EN TIEMPO REAL (tipo DHL/AliExpress)                  │   │
│  │                                                                  │   │
│  │  📦 Potenciómetro Alps 10K                                      │   │
│  │  ══════════════════════════════════════════════                 │   │
│  │  ✅ 15/01 - Pedido realizado                                    │   │
│  │  ✅ 16/01 - Preparando envío [foto]                             │   │
│  │  ✅ 18/01 - Despachado desde China                              │   │
│  │  ✅ 25/01 - En tránsito - Guangzhou                             │   │
│  │  ✅ 02/02 - Llegó a Chile - Aduana                              │   │
│  │  🔄 03/02 - En proceso de internación                           │   │
│  │  ○  --/-- - Entregado en destino                                │   │
│  │  ○  --/-- - Instalado en equipo                                 │   │
│  │                                                                  │   │
│  │  [Ver en 17track] [Ver en AliExpress]                           │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                         │                                               │
│                         ▼                                               │
│  📧 NOTIFICACIONES AUTOMÁTICAS EN CADA CAMBIO DE ESTADO                │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.3.3 Integración con APIs de Tracking

| Servicio                | API             | Cobertura             | Costo                |
| ----------------------- | --------------- | --------------------- | -------------------- |
| **17track**       | ✅ API REST     | 900+ carriers mundial | Free tier + paid     |
| **AfterShip**     | ✅ API REST     | 1000+ carriers        | Free 50 envíos/mes  |
| **TrackingMore**  | ✅ API REST     | 1100+ carriers        | Free tier disponible |
| **AliExpress**    | ✅ Scraping/API | Solo AliExpress       | Gratis               |
| **Correos Chile** | ✅ API          | Chile nacional        | Gratis               |
| **DHL**           | ✅ API oficial  | Internacional         | Gratis con cuenta    |

**Recomendación:** Usar **17track** o **AfterShip** como agregador universal + APIs específicas para casos especiales.

```python
# Servicio de tracking unificado
class TrackingService:
    """Servicio que consulta múltiples APIs de tracking"""
  
    CARRIERS = {
        'aliexpress': AliExpressTracker,
        'dhl': DHLTracker,
        'fedex': FedExTracker,
        'correos_chile': CorreosChileTracker,
        'generic': SeventeenTrackTracker,  # 17track como fallback
    }
  
    async def get_tracking_info(self, tracking_number: str, carrier: str = None):
        """
        Obtiene info de tracking.
        Si no se especifica carrier, usa 17track para detectar automáticamente.
        """
        if carrier and carrier in self.CARRIERS:
            tracker = self.CARRIERS[carrier]()
        else:
            tracker = self.CARRIERS['generic']()
      
        return await tracker.track(tracking_number)
  
    async def sync_all_pending_shipments(self):
        """Cron job: actualiza todos los envíos pendientes"""
        pending = await get_pending_shipments()
        for shipment in pending:
            info = await self.get_tracking_info(shipment.tracking_number)
            await update_shipment_status(shipment, info)
            if info.status_changed:
                await send_notification_email(shipment.repair.client, info)
```

### 5.3.4 Modelos de Base de Datos

```python
class RepairPart(Base):
    """Repuesto asociado a una reparación"""
    __tablename__ = "repair_parts"
  
    id = Column(Integer, primary_key=True)
    repair_id = Column(Integer, ForeignKey("repairs.id"), nullable=False)
    added_by_id = Column(Integer, ForeignKey("users.id"))  # Técnico o cliente
  
    # Info del repuesto
    name = Column(String(255), nullable=False)
    description = Column(Text)
    part_number = Column(String(100))
    quantity = Column(Integer, default=1)
    image_url = Column(String(500))
  
    # Precio desglosado
    unit_price = Column(Integer)  # CLP
    shipping_cost = Column(Integer, default=0)
    customs_cost = Column(Integer, default=0)  # Aduana si aplica
    management_fee = Column(Integer, default=0)  # Gestión
    total_price = Column(Integer)
  
    # Origen
    source = Column(String(50))  # 'aliexpress', 'mouser', 'digikey', 'local'
    source_url = Column(String(500))
    source_order_id = Column(String(100))  # ID de orden en origen
  
    # Estado
    status = Column(Enum(
        "suggested",        # Técnico sugirió, cliente no ha visto
        "pending_approval", # Esperando aprobación del cliente
        "approved",         # Aprobado, pendiente pago
        "paid",             # Pagado
        "ordered",          # Comprado en origen
        "shipped",          # En camino
        "in_customs",       # En aduana
        "delivered",        # Llegó al taller
        "installed",        # Instalado en equipo
        "cancelled"         # Cancelado
    ), default="suggested")
  
    # Timestamps de cada estado
    suggested_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime)
    paid_at = Column(DateTime)
    ordered_at = Column(DateTime)
    shipped_at = Column(DateTime)
    delivered_at = Column(DateTime)
    installed_at = Column(DateTime)
  
    # Relaciones
    repair = relationship("Repair", back_populates="parts")
    shipment = relationship("Shipment", back_populates="part", uselist=False)
    payment = relationship("Payment", back_populates="part")


class Shipment(Base):
    """Envío de un repuesto con tracking"""
    __tablename__ = "shipments"
  
    id = Column(Integer, primary_key=True)
    part_id = Column(Integer, ForeignKey("repair_parts.id"), unique=True)
  
    # Tracking
    carrier = Column(String(50))  # 'dhl', 'fedex', 'correos_chile', '4px', etc.
    tracking_number = Column(String(100))
    tracking_url = Column(String(500))  # URL directa al carrier
  
    # Origen y destino
    origin_country = Column(String(50))
    origin_city = Column(String(100))
  
    # Estado actual
    current_status = Column(String(100))
    current_location = Column(String(200))
    estimated_delivery = Column(DateTime)
  
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime)
    delivered_at = Column(DateTime)
  
    # Relación
    part = relationship("RepairPart", back_populates="shipment")
    events = relationship("ShipmentEvent", back_populates="shipment", order_by="ShipmentEvent.timestamp")


class ShipmentEvent(Base):
    """Evento de tracking (cada actualización del envío)"""
    __tablename__ = "shipment_events"
  
    id = Column(Integer, primary_key=True)
    shipment_id = Column(Integer, ForeignKey("shipments.id"))
  
    # Evento
    status = Column(String(100))  # 'in_transit', 'customs', 'delivered', etc.
    description = Column(String(500))  # "Paquete en centro de distribución Shanghai"
    location = Column(String(200))
    timestamp = Column(DateTime)
  
    # Foto del evento (si el técnico sube foto de llegada, etc.)
    photo_url = Column(String(500))
  
    # Metadata
    raw_data = Column(JSON)  # Respuesta cruda de la API
    created_at = Column(DateTime, default=datetime.utcnow)
  
    # Relación
    shipment = relationship("Shipment", back_populates="events")


class Payment(Base):
    """Pagos realizados"""
    __tablename__ = "payments"
  
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    repair_id = Column(Integer, ForeignKey("repairs.id"), nullable=True)
    part_id = Column(Integer, ForeignKey("repair_parts.id"), nullable=True)
  
    # Tipo y monto
    payment_type = Column(Enum("budget", "repair", "parts", "storage", "other"))
    amount = Column(Integer)  # CLP
    description = Column(String(500))
  
    # Flow.cl
    flow_token = Column(String(255))
    flow_order = Column(String(255))
    flow_status = Column(String(50))
  
    # Estado
    status = Column(Enum("pending", "processing", "paid", "failed", "refunded"))
  
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    paid_at = Column(DateTime)
  
    # Relaciones
    user = relationship("User")
    repair = relationship("Repair")
    part = relationship("RepairPart", back_populates="payment")
```

### 5.3.5 Vista del Cliente: Timeline Unificado

El cliente ve TODO en un solo timeline (tipo DHL):

```
┌─────────────────────────────────────────────────────────────────────────┐
│  REPARACIÓN CDS-047 - KORG MS-2000                                      │
│  Estado: EN REPARACIÓN - ESPERANDO REPUESTOS                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ════════════════════════════════════════════════════════════════════   │
│                                                                         │
│  ✅ 05/01/2026 10:30 - EQUIPO RECIBIDO                                  │
│     └─ Recibido en taller. Fotos de ingreso adjuntas.                  │
│        [📷 Ver 3 fotos]                                                 │
│                                                                         │
│  ✅ 06/01/2026 15:45 - DIAGNÓSTICO COMPLETADO                           │
│     └─ Se detectaron 2 potenciómetros dañados y 1 encoder.             │
│        Cotización: $45.000 (mano de obra) + repuestos                  │
│        [📷 Ver 5 fotos internas]                                        │
│                                                                         │
│  ✅ 06/01/2026 16:00 - COTIZACIÓN APROBADA                              │
│     └─ Cliente aprobó reparación.                                      │
│                                                                         │
│  ✅ 07/01/2026 09:00 - REPUESTOS SOLICITADOS                            │
│     └─ Se requieren repuestos importados.                              │
│        [🛒 Ver detalle de repuestos]                                    │
│                                                                         │
│  ✅ 07/01/2026 11:30 - PAGO DE REPUESTOS CONFIRMADO                     │
│     └─ Pago recibido: $11.300                                          │
│        [📄 Ver comprobante]                                             │
│                                                                         │
│  ✅ 07/01/2026 14:00 - REPUESTOS COMPRADOS                              │
│     └─ Pedido realizado en AliExpress. Orden #8847291034               │
│                                                                         │
│  ✅ 10/01/2026 08:00 - ENVÍO DESPACHADO                                 │
│     └─ Tracking: LP00847293847CN                                       │
│        Carrier: 4PX                                                     │
│        [📦 Ver tracking en tiempo real]                                 │
│                                                                         │
│  ✅ 18/01/2026 - EN TRÁNSITO                                            │
│     └─ Guangzhou, China → Santiago, Chile                              │
│                                                                         │
│  🔄 25/01/2026 - EN ADUANA CHILE                                        │
│     └─ Procesando internación...                                       │
│                                                                         │
│  ○  --/--/---- - REPUESTOS RECIBIDOS                                   │
│  ○  --/--/---- - REPARACIÓN COMPLETADA                                 │
│  ○  --/--/---- - LISTO PARA RETIRO                                     │
│  ○  --/--/---- - ENTREGADO                                             │
│                                                                         │
│  ════════════════════════════════════════════════════════════════════   │
│                                                                         │
│  📧 Notificaciones: Activadas (cada cambio de estado)                   │
│  📱 WhatsApp: +56 9 1234 5678                                           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.3.6 Pasarela de Pago (Flow.cl)

| Pasarela          | Comisión  | Integración    | Recomendación    |
| ----------------- | ---------- | --------------- | ----------------- |
| **Flow.cl** | 2.9% + IVA | API REST simple | ⭐ RECOMENDADO    |
| Transbank         | 2.5% + IVA | Más complejo   | Para alto volumen |
| MercadoPago       | 3.5% + IVA | SDK fácil      | Alternativa       |

### 5.3.7 Emails Automáticos por Evento

| Evento              | Email al Cliente                          | Email al Técnico                   |
| ------------------- | ----------------------------------------- | ----------------------------------- |
| Repuesto sugerido   | "Se requieren repuestos para tu equipo"   | -                                   |
| Cliente aprueba     | "Gracias por aprobar"                     | "Cliente aprobó repuestos CDS-XXX" |
| Pago confirmado     | "Pago recibido, procederemos a comprar"   | "Pago recibido CDS-XXX"             |
| Repuesto comprado   | "Repuesto comprado, pronto tracking"      | -                                   |
| Envío despachado   | "Tu repuesto está en camino" + tracking  | -                                   |
| En aduana           | "Repuesto en aduana Chile"                | -                                   |
| Entregado en taller | "Repuesto llegó, reanudamos reparación" | -                                   |
| Instalado           | "Repuesto instalado en tu equipo"         | -                                   |

## 5.4 Sistema de Tracking de Reparaciones (Timeline)

### Tu visión:

> "Como cuando AliExpress o DHL me manda un paquete, sale el estado, qué pasó qué día, y en mi caso con fotos"

### Estado actual: 🟡 Parcial (existen estados, falta timeline visual y fotos)

### 5.4.1 Modelo de Eventos de Reparación

```python
class RepairEvent(Base):
    """Cada evento/cambio en una reparación (timeline)"""
    __tablename__ = "repair_events"
  
    id = Column(Integer, primary_key=True)
    repair_id = Column(Integer, ForeignKey("repairs.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))  # Quién generó el evento
  
    # Evento
    event_type = Column(Enum(
        "created",              # Ficha creada
        "photos_added",         # Fotos agregadas
        "diagnosis_complete",   # Diagnóstico listo
        "quote_sent",           # Cotización enviada
        "quote_approved",       # Cliente aprobó
        "quote_rejected",       # Cliente rechazó
        "repair_started",       # Inicio de reparación
        "progress_update",      # Actualización de avance
        "parts_needed",         # Se necesitan repuestos
        "parts_ordered",        # Repuestos comprados
        "parts_received",       # Repuestos llegaron
        "repair_complete",      # Reparación terminada
        "ready_pickup",         # Listo para retiro
        "delivered",            # Entregado al cliente
        "note_added",           # Nota técnica agregada
        "status_changed"        # Cambio de estado genérico
    ))
  
    # Descripción
    title = Column(String(255))  # "Diagnóstico completado"
    description = Column(Text)   # Detalle largo si es necesario
  
    # Metadata
    old_status = Column(String(50))
    new_status = Column(String(50))
    progress_percent = Column(Integer)  # 0-100 si aplica
  
    # Visibilidad
    visible_to_client = Column(Boolean, default=True)  # Algunas notas son solo internas
  
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)
  
    # Relaciones
    repair = relationship("Repair", back_populates="events")
    photos = relationship("RepairEventPhoto", back_populates="event")
    created_by = relationship("User")


class RepairEventPhoto(Base):
    """Fotos asociadas a un evento de reparación"""
    __tablename__ = "repair_event_photos"
  
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("repair_events.id"))
  
    # Imagen
    url = Column(String(500), nullable=False)
    thumbnail_url = Column(String(500))
    caption = Column(String(255))
  
    # Metadata
    uploaded_at = Column(DateTime, default=datetime.utcnow)
  
    # Relación
    event = relationship("RepairEvent", back_populates="photos")
```

### 5.4.2 Cron Jobs Necesarios

```python
# Tareas programadas (Celery o APScheduler)

CRON_JOBS = {
    # Actualizar tracking de envíos pendientes
    "update_shipment_tracking": {
        "schedule": "every 4 hours",
        "function": "sync_all_pending_shipments"
    },
  
    # Enviar recordatorios de retiro
    "send_pickup_reminders": {
        "schedule": "daily at 10:00",
        "function": "send_pending_pickup_reminders"
    },
  
    # Cobrar bodegaje automático
    "charge_storage_fees": {
        "schedule": "monthly on day 1",
        "function": "generate_storage_invoices"
    },
  
    # Actualizar precios de mercado (scraper)
    "update_market_prices": {
        "schedule": "weekly on sunday",
        "function": "scrape_market_prices"
    },
  
    # Backup de base de datos
    "database_backup": {
        "schedule": "daily at 03:00",
        "function": "backup_database_to_cloud"
    }
}
```

## 5.6 Sistema de Tickets y Atención Automatizada

### Tu visión:

> "Tickets de atención con tiempo de respuesta, automatizar todo lo posible, respuestas automáticas, la web se debe manejar sola"

### Estado actual: ❌ 0% implementado

### 5.6.1 Concepto: Web Autónoma

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│                    CDS.CL = SISTEMA AUTÓNOMO 24/7                       │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                      CLIENTE INTERACTÚA                           │ │
│  │                            │                                      │ │
│  │                            ▼                                      │ │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐             │ │
│  │  │ Cotizar │  │ Ticket  │  │ Agendar │  │  Pagar  │             │ │
│  │  │   IA    │  │ Soporte │  │  Cita   │  │  Online │             │ │
│  │  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘             │ │
│  │       │            │            │            │                    │ │
│  │       ▼            ▼            ▼            ▼                    │ │
│  │  ┌─────────────────────────────────────────────────────────────┐ │ │
│  │  │              MOTOR DE AUTOMATIZACIÓN                        │ │ │
│  │  │                                                             │ │ │
│  │  │  • Respuestas automáticas inmediatas                       │ │ │
│  │  │  • Clasificación de tickets por IA                         │ │ │
│  │  │  • Detección de instrumento por imagen                     │ │ │
│  │  │  • Escalado automático si no hay respuesta                 │ │ │
│  │  │  • Notificaciones y recordatorios                          │ │ │
│  │  │  • Cierre automático de tickets resueltos                  │ │ │
│  │  └─────────────────────────────────────────────────────────────┘ │ │
│  │                            │                                      │ │
│  │                            ▼                                      │ │
│  │  ┌─────────────────────────────────────────────────────────────┐ │ │
│  │  │                    TÚ SOLO VES                              │ │ │
│  │  │                                                             │ │ │
│  │  │  📋 Dashboard con lo que REQUIERE tu atención              │ │ │
│  │  │  🔴 Tickets urgentes / sin resolver                        │ │ │
│  │  │  📊 Resumen diario por email                               │ │ │
│  │  └─────────────────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.6.2 Sistema de Tickets

```python
class Ticket(Base):
    """Ticket de soporte/consulta"""
    __tablename__ = "tickets"
  
    id = Column(Integer, primary_key=True)
    ticket_number = Column(String(20), unique=True)  # TKT-2026-0001
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Puede ser anónimo
    repair_id = Column(Integer, ForeignKey("repairs.id"), nullable=True)
  
    # Contacto (si no tiene cuenta)
    guest_name = Column(String(255))
    guest_email = Column(String(255))
    guest_phone = Column(String(50))
  
    # Contenido
    subject = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    category = Column(Enum(
        "quote_question",      # Pregunta sobre cotización
        "repair_status",       # Estado de reparación
        "payment_issue",       # Problema con pago
        "schedule_change",     # Cambio de cita
        "general_inquiry",     # Consulta general
        "complaint",           # Reclamo
        "warranty",            # Garantía
        "parts_question",      # Pregunta sobre repuestos
        "other"                # Otro
    ))
  
    # Prioridad (auto-asignada o manual)
    priority = Column(Enum("low", "medium", "high", "urgent"), default="medium")
  
    # Estado
    status = Column(Enum(
        "new",                 # Nuevo, sin leer
        "auto_replied",        # Respondido automáticamente
        "awaiting_response",   # Esperando respuesta del técnico
        "in_progress",         # En proceso
        "awaiting_customer",   # Esperando respuesta del cliente
        "resolved",            # Resuelto
        "closed"               # Cerrado
    ), default="new")
  
    # SLA (Service Level Agreement)
    sla_response_hours = Column(Integer, default=24)  # Tiempo máximo de respuesta
    sla_deadline = Column(DateTime)  # Fecha límite
    sla_breached = Column(Boolean, default=False)  # ¿Se pasó del tiempo?
  
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    first_response_at = Column(DateTime)
    resolved_at = Column(DateTime)
    closed_at = Column(DateTime)
  
    # Relaciones
    user = relationship("User")
    repair = relationship("Repair")
    messages = relationship("TicketMessage", back_populates="ticket")


class TicketMessage(Base):
    """Mensajes dentro de un ticket (conversación)"""
    __tablename__ = "ticket_messages"
  
    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"))
  
    # Autor
    author_type = Column(Enum("customer", "technician", "system"))  # system = automático
    author_id = Column(Integer, ForeignKey("users.id"), nullable=True)
  
    # Contenido
    message = Column(Text, nullable=False)
    is_auto_reply = Column(Boolean, default=False)
  
    # Adjuntos
    attachments = Column(JSON)  # [{"url": "...", "name": "foto.jpg"}]
  
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)
  
    # Relaciones
    ticket = relationship("Ticket", back_populates="messages")
```

### 5.6.3 Respuestas Automáticas Inteligentes

```python
# Configuración de respuestas automáticas
AUTO_RESPONSES = {
    "quote_question": {
        "immediate_reply": True,
        "template": """
Hola {name},

Gracias por tu consulta sobre cotización.

🔧 Puedes obtener una cotización aproximada inmediata usando nuestro 
   cotizador online: {cotizador_url}

📋 Si ya tienes una cotización y tienes dudas específicas, responde 
   este mensaje con el número de cotización y tu pregunta.

⏰ Tiempo de respuesta: Máximo 24 horas hábiles.

Saludos,
Cirujano de Sintetizadores (respuesta automática)
        """,
        "sla_hours": 24
    },
  
    "repair_status": {
        "immediate_reply": True,
        "template": """
Hola {name},

Gracias por contactarnos sobre el estado de tu reparación.

{repair_status_block}

📱 Puedes ver el estado actualizado en tiempo real en tu dashboard:
   {dashboard_url}

Si tienes dudas adicionales, responde este mensaje.

Saludos,
Cirujano de Sintetizadores (respuesta automática)
        """,
        "sla_hours": 12,
        "auto_resolve_if_info_provided": True
    },
  
    "payment_issue": {
        "immediate_reply": True,
        "priority": "high",
        "template": """
Hola {name},

Recibimos tu mensaje sobre un problema con el pago.

🔍 Estamos revisando tu caso con prioridad.
📧 Un técnico te contactará en las próximas 4 horas hábiles.

Si es urgente, puedes contactarnos por WhatsApp: +56 9 XXXX XXXX

Saludos,
Cirujano de Sintetizadores (respuesta automática)
        """,
        "sla_hours": 4,
        "notify_technician_immediately": True
    },
  
    "schedule_change": {
        "immediate_reply": True,
        "template": """
Hola {name},

Recibimos tu solicitud de cambio de cita.

📅 Tu cita actual: {current_appointment}

Para reagendar, puedes:
1. Usar nuestro sistema online: {reschedule_url}
2. Responder este mensaje con tu nueva fecha preferida

⏰ Procesaremos tu solicitud en máximo 12 horas.

Saludos,
Cirujano de Sintetizadores (respuesta automática)
        """,
        "sla_hours": 12
    },
  
    "complaint": {
        "immediate_reply": True,
        "priority": "urgent",
        "template": """
Hola {name},

Lamentamos que hayas tenido una mala experiencia.

🔴 Tu caso ha sido marcado como PRIORITARIO.
👤 El técnico responsable revisará personalmente tu situación.
📞 Te contactaremos en las próximas 2 horas hábiles.

Tu satisfacción es importante para nosotros.

Saludos,
Cirujano de Sintetizadores (respuesta automática)
        """,
        "sla_hours": 2,
        "notify_technician_immediately": True,
        "send_sms": True
    }
}


class AutoResponseEngine:
    """Motor de respuestas automáticas"""
  
    async def process_new_ticket(self, ticket: Ticket):
        """Procesa un ticket nuevo y genera respuesta automática"""
      
        # 1. Clasificar categoría si no viene (usando IA simple)
        if not ticket.category:
            ticket.category = await self.classify_ticket(ticket.message)
      
        # 2. Asignar prioridad
        config = AUTO_RESPONSES.get(ticket.category, AUTO_RESPONSES["general_inquiry"])
        if config.get("priority"):
            ticket.priority = config["priority"]
      
        # 3. Calcular SLA
        ticket.sla_response_hours = config.get("sla_hours", 24)
        ticket.sla_deadline = datetime.utcnow() + timedelta(hours=ticket.sla_response_hours)
      
        # 4. Generar respuesta automática
        if config.get("immediate_reply"):
            response = await self.generate_response(ticket, config["template"])
            await self.send_auto_reply(ticket, response)
            ticket.status = "auto_replied"
      
        # 5. Notificar al técnico si es urgente
        if config.get("notify_technician_immediately"):
            await self.notify_technician(ticket)
      
        # 6. Enviar SMS si es crítico
        if config.get("send_sms"):
            await self.send_sms_alert(ticket)
      
        await ticket.save()
  
    async def classify_ticket(self, message: str) -> str:
        """Clasifica el ticket por palabras clave (puede mejorarse con IA)"""
        message_lower = message.lower()
      
        if any(word in message_lower for word in ["cotiz", "precio", "cuanto", "cuesta", "valor"]):
            return "quote_question"
        elif any(word in message_lower for word in ["estado", "como va", "avance", "cuando", "listo"]):
            return "repair_status"
        elif any(word in message_lower for word in ["pago", "pagar", "transferencia", "cobro"]):
            return "payment_issue"
        elif any(word in message_lower for word in ["cita", "hora", "agendar", "cambiar fecha"]):
            return "schedule_change"
        elif any(word in message_lower for word in ["reclamo", "queja", "mal", "problema", "molesto"]):
            return "complaint"
        elif any(word in message_lower for word in ["garantía", "garantia", "se volvió", "falló"]):
            return "warranty"
        else:
            return "general_inquiry"
```

### 5.6.4 SLA y Escalado Automático

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    ESCALADO AUTOMÁTICO DE TICKETS                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  TICKET NUEVO                                                           │
│       │                                                                 │
│       ▼                                                                 │
│  ┌─────────────────┐                                                   │
│  │ Respuesta auto  │ ◀── Inmediata (segundos)                          │
│  │ + Asignar SLA   │                                                   │
│  └────────┬────────┘                                                   │
│           │                                                             │
│           ▼                                                             │
│  ┌─────────────────┐     ┌─────────────────┐                          │
│  │ ¿Respondido     │ SÍ  │ Ticket resuelto │                          │
│  │ dentro de SLA?  │────▶│ o en progreso   │                          │
│  └────────┬────────┘     └─────────────────┘                          │
│           │ NO                                                          │
│           ▼                                                             │
│  ┌─────────────────┐                                                   │
│  │ 50% del SLA     │────▶ 📧 Recordatorio al técnico                   │
│  └────────┬────────┘                                                   │
│           │                                                             │
│           ▼                                                             │
│  ┌─────────────────┐                                                   │
│  │ 80% del SLA     │────▶ 📱 SMS al técnico + Email urgente            │
│  └────────┬────────┘                                                   │
│           │                                                             │
│           ▼                                                             │
│  ┌─────────────────┐                                                   │
│  │ 100% SLA        │────▶ 🔴 Marca como INCUMPLIDO                     │
│  │ (SLA breach)    │     📧 Email de disculpa al cliente               │
│  └────────┬────────┘     📊 Registra en métricas                       │
│           │                                                             │
│           ▼                                                             │
│  ┌─────────────────┐                                                   │
│  │ 150% del SLA    │────▶ 📞 Llamada automática al técnico (Twilio)    │
│  └─────────────────┘     🎁 Ofrecer compensación al cliente            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.6.5 Cron Jobs de Automatización

```python
AUTOMATION_CRON_JOBS = {
    # Verificar SLA cada 15 minutos
    "check_sla_breaches": {
        "schedule": "every 15 minutes",
        "function": "check_and_escalate_tickets"
    },
  
    # Cerrar tickets sin respuesta del cliente (7 días)
    "auto_close_inactive": {
        "schedule": "daily at 09:00",
        "function": "close_inactive_tickets",
        "params": {"days_inactive": 7}
    },
  
    # Enviar resumen diario al técnico
    "daily_summary": {
        "schedule": "daily at 08:00",
        "function": "send_technician_daily_summary"
    },
  
    # Recordatorio de citas del día siguiente
    "appointment_reminders": {
        "schedule": "daily at 18:00",
        "function": "send_tomorrow_appointment_reminders"
    },
  
    # Recordatorio de retiro (equipos listos hace 7 días)
    "pickup_reminders": {
        "schedule": "daily at 10:00",
        "function": "send_pickup_reminders"
    },
  
    # Actualizar tracking de envíos
    "update_tracking": {
        "schedule": "every 4 hours",
        "function": "sync_all_shipment_tracking"
    },
  
    # Generar cobros de bodegaje
    "storage_fees": {
        "schedule": "monthly on day 1 at 00:00",
        "function": "generate_storage_fees"
    },
  
    # Backup de base de datos
    "database_backup": {
        "schedule": "daily at 03:00",
        "function": "backup_database"
    },
  
    # Limpiar archivos temporales
    "cleanup_temp_files": {
        "schedule": "weekly on sunday at 04:00",
        "function": "cleanup_temp_uploads"
    }
}
```

## 5.7 Detección Automática de Instrumentos (IA)

### Tu visión:

> "El algoritmo de Python detecta el teclado, ya sea nuestra base o la foto que suba el cliente, debe ser drag and drop y/o abrir ventana para buscar en PC"

### Estado actual: ❌ 0% implementado

### 5.7.1 Flujo de Subida de Imagen

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    SUBIDA DE IMAGEN INTERACTIVA                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                                                                 │   │
│  │     ┌─────────────────────────────────────────────────────┐    │   │
│  │     │                                                     │    │   │
│  │     │         📷 ARRASTRA TU FOTO AQUÍ                   │    │   │
│  │     │                                                     │    │   │
│  │     │              o                                      │    │   │
│  │     │                                                     │    │   │
│  │     │         [BUSCAR EN MI PC]                          │    │   │
│  │     │                                                     │    │   │
│  │     │    Formatos: JPG, PNG, WEBP (máx 10MB)            │    │   │
│  │     │                                                     │    │   │
│  │     └─────────────────────────────────────────────────────┘    │   │
│  │                                                                 │   │
│  │  ────────────────────────────────────────────────────────────  │   │
│  │                                                                 │   │
│  │  💡 Tips para una buena foto:                                  │   │
│  │     • Foto frontal del instrumento completo                    │   │
│  │     • Buena iluminación                                        │   │
│  │     • Que se vea la marca y modelo                             │   │
│  │                                                                 │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│                              │                                          │
│                              ▼                                          │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  🔄 Analizando imagen...                                        │   │
│  │  ████████████░░░░░░░░ 60%                                       │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│                              │                                          │
│                              ▼                                          │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  ✅ INSTRUMENTO DETECTADO                                       │   │
│  │                                                                 │   │
│  │  ┌─────────┐                                                   │   │
│  │  │ [FOTO]  │  KORG microKORG                                   │   │
│  │  │         │  Sintetizador analógico virtual                   │   │
│  │  │         │  37 teclas, 4 octavas                             │   │
│  │  └─────────┘                                                   │   │
│  │                                                                 │   │
│  │  ¿Es correcto?  [SÍ, CONTINUAR]  [NO, ES OTRO MODELO]         │   │
│  │                                                                 │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.7.2 Arquitectura de Detección

```python
class InstrumentDetector:
    """Servicio de detección de instrumentos por imagen"""
  
    def __init__(self):
        # Opción 1: Modelo local (más rápido, offline)
        self.local_model = self.load_local_model()
      
        # Opción 2: API externa (más preciso)
        self.vision_api = GoogleVisionAPI()  # o OpenAI Vision, Claude Vision
  
    async def detect_instrument(self, image_path: str) -> DetectionResult:
        """
        Detecta el instrumento en una imagen.
      
        Returns:
            DetectionResult con:
            - instrument_id: ID en nuestra BD (si existe)
            - brand: Marca detectada
            - model: Modelo detectado
            - confidence: 0-100%
            - suggestions: Lista de posibles coincidencias
        """
      
        # 1. Intentar con modelo local primero (rápido)
        local_result = await self.local_detection(image_path)
      
        if local_result.confidence > 85:
            return local_result
      
        # 2. Si no es seguro, usar API externa
        api_result = await self.api_detection(image_path)
      
        # 3. Buscar en nuestra base de datos
        matches = await self.find_in_database(api_result)
      
        return DetectionResult(
            brand=api_result.brand,
            model=api_result.model,
            confidence=api_result.confidence,
            instrument_id=matches[0].id if matches else None,
            suggestions=matches[:5]  # Top 5 coincidencias
        )
  
    async def local_detection(self, image_path: str):
        """Detección usando modelo entrenado localmente"""
        # Usar modelo CLIP o similar entrenado con imágenes de sintetizadores
        # Se entrena con las imágenes de nuestra base de datos
        pass
  
    async def api_detection(self, image_path: str):
        """Detección usando API de visión (Google, OpenAI, Claude)"""
      
        # Ejemplo con OpenAI Vision
        response = await openai.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": """
                        Analiza esta imagen de un instrumento musical electrónico.
                        Responde SOLO en JSON con este formato:
                        {
                            "brand": "marca del instrumento",
                            "model": "modelo específico",
                            "type": "synthesizer|keyboard|drum_machine|etc",
                            "confidence": 0-100,
                            "features": ["37 keys", "analog", etc]
                        }
                    """},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            }]
        )
      
        return parse_detection_response(response)
  
    async def find_in_database(self, detection) -> List[Instrument]:
        """Busca coincidencias en nuestra base de datos"""
      
        # Búsqueda por marca + modelo
        exact_match = await Instrument.query.filter(
            Instrument.brand.name.ilike(f"%{detection.brand}%"),
            Instrument.model.ilike(f"%{detection.model}%")
        ).first()
      
        if exact_match:
            return [exact_match]
      
        # Búsqueda fuzzy si no hay match exacto
        similar = await search_similar_instruments(
            brand=detection.brand,
            model=detection.model,
            limit=5
        )
      
        return similar
```

### 5.7.3 Componente Vue - Drag & Drop

```vue
<!-- components/ImageUploader.vue -->
<template>
  <div 
    class="upload-zone"
    :class="{ 'drag-over': isDragging, 'has-image': imagePreview }"
    @dragover.prevent="isDragging = true"
    @dragleave="isDragging = false"
    @drop.prevent="handleDrop"
    @click="openFilePicker"
  >
    <!-- Estado: Sin imagen -->
    <div v-if="!imagePreview && !isAnalyzing" class="upload-prompt">
      <div class="upload-icon">📷</div>
      <h3>Arrastra tu foto aquí</h3>
      <p>o</p>
      <button class="btn-browse">Buscar en mi PC</button>
      <p class="formats">Formatos: JPG, PNG, WEBP (máx 10MB)</p>
    </div>
  
    <!-- Estado: Analizando -->
    <div v-if="isAnalyzing" class="analyzing">
      <div class="spinner"></div>
      <p>Analizando imagen...</p>
      <div class="progress-bar">
        <div :style="{ width: progress + '%' }"></div>
      </div>
    </div>
  
    <!-- Estado: Resultado -->
    <div v-if="detectionResult" class="detection-result">
      <img :src="imagePreview" class="preview" />
      <div class="result-info">
        <span class="confidence" :class="confidenceClass">
          {{ detectionResult.confidence }}% seguro
        </span>
        <h3>{{ detectionResult.brand }} {{ detectionResult.model }}</h3>
        <p>{{ detectionResult.type }}</p>
      
        <div class="actions">
          <button @click="confirmDetection" class="btn-confirm">
            ✓ Sí, es correcto
          </button>
          <button @click="showAlternatives" class="btn-other">
            ✗ No, es otro modelo
          </button>
        </div>
      </div>
    </div>
  
    <input 
      ref="fileInput"
      type="file"
      accept="image/jpeg,image/png,image/webp"
      @change="handleFileSelect"
      hidden
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useInstrumentDetection } from '@/composables/useInstrumentDetection'

const { detectInstrument, isAnalyzing, progress, detectionResult } = useInstrumentDetection()

const isDragging = ref(false)
const imagePreview = ref(null)
const fileInput = ref(null)

const handleDrop = async (e) => {
  isDragging.value = false
  const file = e.dataTransfer.files[0]
  await processFile(file)
}

const handleFileSelect = async (e) => {
  const file = e.target.files[0]
  await processFile(file)
}

const processFile = async (file) => {
  if (!file || !file.type.startsWith('image/')) return
  if (file.size > 10 * 1024 * 1024) {
    alert('La imagen es muy grande (máximo 10MB)')
    return
  }
  
  // Mostrar preview
  imagePreview.value = URL.createObjectURL(file)
  
  // Enviar a detección
  await detectInstrument(file)
}

const openFilePicker = () => {
  fileInput.value.click()
}

const confirmDetection = () => {
  emit('detected', detectionResult.value)
}

const showAlternatives = () => {
  emit('showAlternatives', detectionResult.value.suggestions)
}
</script>
```

### 5.7.4 APIs de Visión Recomendadas

| Servicio                      | Costo           | Precisión | Velocidad   | Recomendación        |
| ----------------------------- | --------------- | ---------- | ----------- | --------------------- |
| **Google Cloud Vision** | $1.50/1000 imgs | Alta       | Rápida     | ⭐ Recomendado        |
| **OpenAI GPT-4 Vision** | $0.01/imagen    | Muy alta   | Media       | Para casos difíciles |
| **Claude Vision**       | $0.01/imagen    | Muy alta   | Media       | Alternativa           |
| **Modelo local (CLIP)** | Gratis          | Media      | Muy rápida | Primera línea        |

**Estrategia recomendada:**

1. Primero: Modelo local (gratis, rápido)
2. Si confianza < 85%: API externa
3. Si aún no hay match: Pedir confirmación manual

### 5.7.5 Entrenamiento del Modelo Local

```python
# Script para entrenar modelo local con nuestras imágenes
# Se ejecuta una vez y luego se actualiza periódicamente

async def train_local_model():
    """
    Entrena modelo de detección con imágenes de nuestra BD.
    Usa transfer learning sobre CLIP o similar.
    """
  
    # 1. Obtener todas las imágenes de instrumentos
    instruments = await Instrument.query.filter(
        Instrument.image.isnot(None)
    ).all()
  
    # 2. Preparar dataset
    dataset = []
    for inst in instruments:
        dataset.append({
            "image": inst.image["url"],
            "label": f"{inst.brand.name} {inst.model}",
            "instrument_id": inst.id
        })
  
    # 3. Entrenar (usando CLIP fine-tuning o similar)
    model = train_clip_classifier(dataset)
  
    # 4. Guardar modelo
    model.save("models/instrument_detector_v1.pt")
  
    return model
```

## 5.8 Resumen de Integraciones API Necesarias

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    MAPA DE INTEGRACIONES API                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  PAGOS                          TRACKING                                │
│  ──────                         ────────                                │
│  • Flow.cl ────────────────────• 17track (universal)                   │
│                                 • AliExpress API                        │
│  CALENDARIO                     • DHL API                               │
│  ──────────                     • Correos Chile                         │
│  • Google Calendar API          • FedEx API                             │
│                                                                         │
│  IMÁGENES                       COMUNICACIÓN                            │
│  ────────                       ────────────                            │
│  • Cloudinary (storage)         • SendGrid/Mailgun (email)              │
│  • Google Vision (detección)    • Twilio (SMS)                          │
│  • OpenAI Vision (backup)       • WhatsApp Business API                 │
│                                                                         │
│  PRECIOS                        STREAMING/VIDEO                         │
│  ───────                        ───────────────                         │
│  • Reverb (scraping)            • YouTube API (live + publicación)      │
│  • eBay API                     • OBS WebSocket (control remoto)        │
│  • Thomann (scraping)           • Instagram API (auto-post)             │
│                                                                         │
│  ANALYTICS                      INFRAESTRUCTURA                         │
│  ─────────                      ──────────────                          │
│  • Google Analytics 4           • cPanel (hosting)                      │
│  • Mixpanel (eventos)           • Cloudflare (CDN + WAF)               │
│  • Sentry (errores)             • Redis (caché)                        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## 5.9 STREAMING EN VIVO - Reparación Transmitida (DIFERENCIADOR ÚNICO)

### Tu visión:

> "El cliente paga extra y VE su equipo siendo reparado EN VIVO. Tengo 6-9 cámaras con OBS. Se publica solo en YouTube después."

### Estado actual: ❌ 0% implementado (hardware listo)

### 5.9.1 Concepto: NADIE hace esto

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│          🎬 REPARACIÓN EN VIVO = SERVICIO PREMIUM + MARKETING           │
│                                                                         │
│   MIENTRAS TÚ REPARAS (2 AM, cuando sea):                              │
│   ═══════════════════════════════════════                              │
│                                                                         │
│   ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐                    │
│   │CAM 1│ │CAM 2│ │CAM 3│ │CAM 4│ │CAM 5│ │CAM 6│  + más             │
│   │Mesa │ │Micro│ │PCB  │ │Manos│ │Cara │ │General                    │
│   └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘                    │
│      └───────┴───────┴───────┼───────┴───────┘                         │
│                              ▼                                          │
│                    ┌─────────────────┐                                 │
│                    │      OBS        │                                 │
│                    │  (Multi-cámara) │                                 │
│                    └────────┬────────┘                                 │
│              ┌──────────────┼──────────────┐                           │
│              ▼              ▼              ▼                            │
│     ┌──────────────┐ ┌──────────┐ ┌──────────────┐                    │
│     │ YOUTUBE LIVE │ │ TU WEB   │ │ GRABACIÓN    │                    │
│     │ (privado/    │ │ (embed)  │ │ LOCAL        │                    │
│     │  público)    │ │          │ │              │                    │
│     └──────────────┘ └──────────┘ └──────────────┘                    │
│                                                                         │
│   RESULTADO SIN ESFUERZO EXTRA:                                        │
│   ✅ Cliente VE su equipo siendo reparado (paga premium)               │
│   ✅ Contenido YouTube SE GENERA SOLO                                  │
│   ✅ Marketing orgánico mientras duermes                               │
│   ✅ Transparencia total = confianza                                   │
│   ✅ Diferenciador ÚNICO en Chile/Latinoamérica                        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.9.2 Modelo de Negocio

| Opción                | Descripción                             | Precio                      |
| ---------------------- | ---------------------------------------- | --------------------------- |
| **Estándar**    | Reparación normal, timeline con fotos   | Precio base                 |
| **Premium VIVO** | Cliente ve en vivo, recibe video         | +$30.000-50.000             |
| **Público**     | Se transmite público, se sube a YouTube | -$15.000-25.000 (descuento) |

### 5.9.3 Flujo Técnico

```
TÚ EN TU DASHBOARD:
1. Click "INICIAR STREAM" en la reparación
2. Sistema crea YouTube Live automáticamente
3. Envía link al cliente
4. OBS empieza a transmitir
5. Click "MARCAR MOMENTO" cuando pasa algo importante
6. Click "TERMINAR"
7. Video se publica SOLO con capítulos automáticos
```

## 5.10 Portfolio AUTOMÁTICO - "Últimos Trabajos"

### Tu visión:

> "Entrego, y se genera SOLA la sección 'Último trabajo'. No hago nada más."

### Estado actual: ❌ 0% implementado

### 5.10.1 Flujo 100% Automático

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    PORTFOLIO SE GENERA SOLO                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  TÚ HACES:                             SISTEMA HACE (AUTOMÁTICO):      │
│  ═════════                             ══════════════════════════       │
│                                                                         │
│  1. Subes fotos mientras          ──▶  Guarda con metadata             │
│     reparas (ya lo haces)                                              │
│                                                                         │
│  2. Marcas "ENTREGADO"            ──▶  Espera 48 hrs (por reclamos)    │
│                                                                         │
│  3. (NADA MÁS)                    ──▶  Selecciona mejores fotos        │
│                                        Genera título automático        │
│                                        Crea descripción del trabajo    │
│                                        Añade video si hubo stream      │
│                                        Publica en "Últimos trabajos"   │
│                                        Publica en Instagram (opcional) │
│                                        Publica en Facebook (opcional)  │
│                                                                         │
│  RESULTADO: Portfolio SIEMPRE actualizado, CERO esfuerzo              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.10.2 Vista en la Web

```
┌─────────────────────────────────────────────────────────────────────────┐
│  ÚLTIMOS TRABAJOS                                    [Ver todos →]      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐        │
│  │  [FOTO FINAL]   │  │  [FOTO FINAL]   │  │  [FOTO FINAL]   │        │
│  │  ▶ (video)      │  │                 │  │  ▶ (video)      │        │
│  ├─────────────────┤  ├─────────────────┤  ├─────────────────┤        │
│  │ KORG MS-2000    │  │ ROLAND JX-3P    │  │ YAMAHA DX7      │        │
│  │ Restauración    │  │ Fuente de poder │  │ Cambio batería  │        │
│  │ Hace 2 días     │  │ Hace 5 días     │  │ Hace 1 semana   │        │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘        │
│                                                                         │
│  (Se actualiza SOLO cada vez que entregas un trabajo)                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## 5.11 Flujo de Trabajo del Técnico (Web Abierta Mientras Reparas)

### Tu visión:

> "Me siento a trabajar con la web abierta y voy haciendo todo desde ahí."

### Estado actual: ❌ 0% implementado

### 5.11.1 Dashboard del Técnico - Vista de Trabajo

```
┌─────────────────────────────────────────────────────────────────────────┐
│  🔧 MODO TRABAJO - CDS-047 KORG MS-2000                    [STREAMING] │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────┐  ┌─────────────────────────────────────┐  │
│  │ ESTADO: En reparación   │  │  CRONÓMETRO: 02:34:15              │  │
│  │ [▼ Cambiar estado]      │  │  [⏸ Pausar] [⏹ Terminar]          │  │
│  └─────────────────────────┘  └─────────────────────────────────────┘  │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  📷 SUBIR FOTO RÁPIDA                                           │   │
│  │  ─────────────────────                                          │   │
│  │  [📷 Desde cámara]  [📁 Desde PC]  [Arrastrar aquí]            │   │
│  │                                                                 │   │
│  │  Tipo: ○ Proceso  ○ Problema  ○ Solución  ○ Final              │   │
│  │  Nota: [________________________________] [Subir]              │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  📝 AGREGAR TRABAJO REALIZADO                                   │   │
│  │  ────────────────────────────                                   │   │
│  │  [+ Mano de obra]  [+ Insumo]  [+ Repuesto]                    │   │
│  │                                                                 │   │
│  │  AGREGADOS HOY:                                                 │   │
│  │  ✓ MO-005 Reemplazo potenciómetro x2      $24.000              │   │
│  │  ✓ INS-001 Soldadura (15cm)               $1.500               │   │
│  │  ✓ INS-002 Flux x3                        $1.500               │   │
│  │  ✓ REP-012 Potenciómetro Alps 10K x2      $7.000               │   │
│  │  ──────────────────────────────────────────────────            │   │
│  │  SUBTOTAL HOY:                            $34.000               │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  💬 NOTA RÁPIDA (visible para cliente)                          │   │
│  │  [Encontré el problema, capacitor de la fuente inflado...]     │   │
│  │  [Enviar nota]  □ Notificar al cliente por email               │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌───────────────────┐  ┌───────────────────┐  ┌───────────────────┐  │
│  │ [📌 MARCAR        │  │ [🛒 AGREGAR       │  │ [✅ MARCAR COMO   │  │
│  │  MOMENTO]         │  │  REPUESTO]        │  │  COMPLETADO]      │  │
│  └───────────────────┘  └───────────────────┘  └───────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.11.2 Catálogos Predefinidos (Click y Listo)

```python
# Todo predefinido, solo haces click
LABOR_CATALOG = {
    "MO-001": {"name": "Diagnóstico básico", "price": 20000},
    "MO-002": {"name": "Diagnóstico avanzado", "price": 35000},
    "MO-003": {"name": "Limpieza general interna", "price": 15000},
    "MO-004": {"name": "Limpieza de contactos", "price": 8000},
    "MO-005": {"name": "Reemplazo potenciómetro (c/u)", "price": 12000},
    "MO-006": {"name": "Reemplazo encoder (c/u)", "price": 15000},
    "MO-007": {"name": "Reemplazo tecla/contacto (c/u)", "price": 5000},
    "MO-008": {"name": "Soldadura SMD (hora)", "price": 25000},
    "MO-009": {"name": "Soldadura through-hole (hora)", "price": 15000},
    "MO-010": {"name": "Reparación fuente de poder", "price": 45000},
    "MO-011": {"name": "Actualización firmware", "price": 20000},
    "MO-012": {"name": "Calibración completa", "price": 25000},
}

CONSUMABLES_CATALOG = {
    "INS-001": {"name": "Soldadura 60/40", "price": 100, "unit": "cm"},
    "INS-002": {"name": "Flux", "price": 500, "unit": "aplicación"},
    "INS-003": {"name": "Alcohol isopropílico", "price": 200, "unit": "ml"},
    "INS-004": {"name": "Pasta térmica", "price": 1000, "unit": "aplicación"},
    "INS-005": {"name": "Spray limpiador", "price": 300, "unit": "aplicación"},
    "INS-006": {"name": "Cinta Kapton", "price": 150, "unit": "cm"},
}
```

## 5.12 Sistema de Cotización JUSTA (Basado en Valor Real)

### Tu visión:

> "No puedo cobrar 300 por instrumento de 100. Se compran 3 nuevos. Hay que ser JUSTOS."

### Estado actual: ❌ 0% implementado

### 5.12.1 Regla de Oro

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   ⚠️ NUNCA COBRAR MÁS DEL 50% DEL VALOR DEL INSTRUMENTO               │
│      (a menos que cliente lo autorice expresamente)                    │
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │  VALOR INSTRUMENTO    │  MÁXIMO RECOMENDADO                     │  │
│   │───────────────────────────────────────────────────────────────  │  │
│   │  $100.000             │  $50.000 (50%)                         │  │
│   │  $300.000             │  $120.000 (40%)                        │  │
│   │  $500.000             │  $175.000 (35%)                        │  │
│   │  $1.000.000           │  $300.000 (30%)                        │  │
│   │  $2.000.000+          │  $500.000 (25%) o evaluar              │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│   SI LA COTIZACIÓN SUPERA EL LÍMITE:                                   │
│   → Sistema AVISA automáticamente                                      │
│   → Sugiere: "Quizás convenga buscar otro equipo"                     │
│   → Cliente decide (firma aceptación especial si quiere continuar)    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.12.2 Desglose Transparente para el Cliente

```
┌─────────────────────────────────────────────────────────────────────────┐
│  COTIZACIÓN CDS-047 - KORG MS-2000                                      │
│  Valor de mercado del instrumento: $450.000                            │
│  Máximo recomendado: $157.500 (35%)                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  MANO DE OBRA                                                           │
│  ─────────────                                                          │
│  MO-002  Diagnóstico avanzado              1    $35.000      $35.000   │
│  MO-005  Reemplazo potenciómetro           2    $12.000      $24.000   │
│  MO-004  Limpieza de contactos             1    $8.000       $8.000    │
│                                            ─────────────────────────── │
│                                            Subtotal MO:      $67.000   │
│                                                                         │
│  INSUMOS                                                                │
│  ───────                                                                │
│  INS-001  Soldadura 60/40                  15cm  $100        $1.500    │
│  INS-002  Flux                             3     $500        $1.500    │
│  INS-003  Alcohol isopropílico             50ml  $200        $10.000   │
│                                            ─────────────────────────── │
│                                            Subtotal Insumos: $13.000   │
│                                                                         │
│  REPUESTOS                                                              │
│  ─────────                                                              │
│  REP-012  Potenciómetro Alps 10K           2     $3.500      $7.000    │
│                                            ─────────────────────────── │
│                                            Subtotal Repuestos: $7.000  │
│                                                                         │
│  ═══════════════════════════════════════════════════════════════════   │
│  TOTAL:                                                      $87.000   │
│  ═══════════════════════════════════════════════════════════════════   │
│                                                                         │
│  ✅ El total ($87.000) está DENTRO del máximo recomendado ($157.500)  │
│                                                                         │
│  Presupuesto pagado: -$20.000                                          │
│  ─────────────────────────────────────────────────────────────────────  │
│  A PAGAR:                                                    $67.000   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 5.13 Políticas y Términos

> "Política de compromiso, recepción, si no retira en X tiempo asume bodega, todo estipulado en ROJO MAYÚSCULA lo importante"

### Estado actual: ❌ 0% implementado

**Documentos necesarios:**

1. **Términos y Condiciones del Servicio**

   - Alcance del servicio
   - Proceso de cotización
   - Tiempos de reparación
   - Garantía post-reparación
2. **Política de Presupuesto y Cobros**

   ```
   ╔═══════════════════════════════════════════════════════════════╗
   ║  💰 POLÍTICA DE PRESUPUESTO                                   ║
   ╠═══════════════════════════════════════════════════════════════╣
   ║                                                               ║
   ║  COSTO DEL PRESUPUESTO: $20.000 CLP                          ║
   ║                                                               ║
   ║  • Este valor se cobra al momento de dejar el equipo         ║
   ║  • Es ABONABLE: Si decide reparar, se descuenta del total    ║
   ║  • Es NO REEMBOLSABLE: Si no repara, queda como pago por     ║
   ║    el tiempo de diagnóstico técnico                          ║
   ║                                                               ║
   ║  El presupuesto incluye:                                     ║
   ║  - Revisión completa del equipo                              ║
   ║  - Diagnóstico técnico detallado                             ║
   ║  - Cotización itemizada de la reparación                     ║
   ║  - Fotos del estado interno (si aplica)                      ║
   ║                                                               ║
   ╚═══════════════════════════════════════════════════════════════╝
   ```
3. **Política de Recepción de Equipos**

   - Estado del equipo al ingreso
   - Responsabilidad por daños previos
   - Fotos obligatorias de ingreso
4. **Política de Bodega/Almacenamiento**

   ```
   ╔═══════════════════════════════════════════════════════════════╗
   ║  ⚠️ IMPORTANTE - POLÍTICA DE RETIRO                          ║
   ╠═══════════════════════════════════════════════════════════════╣
   ║                                                               ║
   ║  • Plazo de retiro: 30 días desde notificación               ║
   ║  • Después de 30 días: $5.000 CLP/mes por bodegaje           ║
   ║  • Después de 90 días: El equipo se considera ABANDONADO     ║
   ║  • Equipos abandonados serán donados o reciclados            ║
   ║                                                               ║
   ║  AL ACEPTAR ESTOS TÉRMINOS, USTED CONFIRMA HABER LEÍDO       ║
   ║  Y COMPRENDIDO ESTA POLÍTICA.                                ║
   ╚═══════════════════════════════════════════════════════════════╝
   ```
5. **Política de Privacidad (GDPR-like)**

   - Datos que recolectas
   - Uso de fotos
   - Retención de datos
6. **Exención de Responsabilidad**

   - Equipos antiguos/frágiles
   - Reparaciones no garantizadas
   - Límites de responsabilidad

### Implementación técnica de políticas

```python
class Policy(Base):
    """Modelo para almacenar políticas versionadas"""
    __tablename__ = "policies"
  
    id = Column(Integer, primary_key=True)
    type = Column(String(50))  # 'terms', 'budget', 'storage', 'privacy', 'liability'
    title = Column(String(255))
    content = Column(Text)  # Contenido en Markdown
    version = Column(String(20))  # '1.0', '1.1', etc.
    is_active = Column(Boolean, default=True)
    requires_acceptance = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class PolicyAcceptance(Base):
    """Registro de aceptación de políticas por usuario"""
    __tablename__ = "policy_acceptances"
  
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    policy_id = Column(Integer, ForeignKey("policies.id"))
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    accepted_at = Column(DateTime, default=datetime.utcnow)
```

### Flujo de aceptación obligatoria

```
┌─────────────────────────────────────────────────────────────────┐
│  ANTES DE AGENDAR CITA O DEJAR EQUIPO                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  □ He leído y acepto los Términos y Condiciones                │
│  □ He leído y acepto la Política de Presupuesto ($20.000)      │
│  □ He leído y acepto la Política de Bodegaje                   │
│  □ He leído y acepto la Política de Privacidad                 │
│                                                                 │
│  ⚠️ DEBE MARCAR TODAS LAS CASILLAS PARA CONTINUAR              │
│                                                                 │
│  [CANCELAR]                        [ACEPTO Y CONTINUAR]         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

# 6. PLAN DE IMPLEMENTACIÓN

## 6.1 Fase 1: Fundamentos (2-3 semanas)

### Backend

```
□ Migrar de SQLite a MySQL (compatibilidad cPanel)
□ Implementar variables de entorno seguras
□ Agregar rate limiting (slowapi)
□ Configurar CORS para producción
□ Crear endpoints de políticas/términos
□ Implementar sistema de logs
```

### Frontend

```
□ Crear página de términos y condiciones
□ Crear página de políticas
□ Implementar checkbox obligatorio de aceptación
□ Agregar meta tags SEO básicos
□ Configurar Google Analytics
□ Implementar PWA básica
```

### Infraestructura

```
□ Configurar SSL en cPanel
□ Configurar dominio www.cirujanodesintetizadores.cl
□ Crear cuenta Cloudinary para imágenes
□ Configurar emails transaccionales
□ Implementar backup automático
```

## 6.2 Fase 2: Cotizador Inteligente (3-4 semanas)

### Backend

```
□ Modelo InstrumentComponent (teclas, botones, potes, etc.)
□ Modelo FaultTemplate (tipos de falla y precios base)
□ Modelo Quotation (cotizaciones guardadas)
□ Endpoint POST /api/v1/cotizar
□ Lógica de cálculo de precios
□ Validación de imágenes subidas
```

### Frontend

```
□ Componente BrandModelSelector
□ Componente VisualDiagnostic (imagen interactiva)
□ Componente SmartQuestionnaire (preguntas aguas abajo)
□ Componente QuotationResult (con disclaimers)
□ Flujo completo de cotización
□ Guardar cotización sin cuenta
```

### Base de datos

```sql
-- Poblar con datos reales
INSERT INTO instrument_components (instrument_id, type, name, position_data)
VALUES 
  (1, 'key', 'Tecla C1', '{"x": 10, "y": 200, "w": 20, "h": 100}'),
  (1, 'key', 'Tecla C#1', '{"x": 30, "y": 200, "w": 15, "h": 60}'),
  (1, 'knob', 'Cutoff', '{"x": 300, "y": 50, "r": 25}'),
  ...
```

## 6.2.1 Fase 2B: Scraper de Precios de Mercado (2 semanas)

### Objetivo

Sistema automático para consultar precios en Reverb, eBay, Thomann y calcular el valor de mercado de cada instrumento. **Esta información es SOLO para uso interno del técnico.**

### Backend - Scraper

```
□ Servicio de scraping con requests/BeautifulSoup o Playwright
□ Modelo InstrumentPriceHistory (historial de precios)
□ Modelo InstrumentValuation (valor calculado actual)
□ Conversión de divisas USD/EUR → CLP (API externa)
□ Cálculo automático de cobro mínimo (10% del valor)
□ Estimación de costo de importación si no está en Chile
□ Cron job para actualización semanal
```

### Fuentes a implementar

```python
PRICE_SOURCES = {
    'reverb': {
        'base_url': 'https://reverb.com/marketplace',
        'priority': 1,
        'frequency': 'weekly',
        'parser': 'reverb_parser'
    },
    'ebay': {
        'base_url': 'https://www.ebay.com/sch/',
        'priority': 2,
        'frequency': 'weekly',
        'parser': 'ebay_parser'
    },
    'thomann': {
        'base_url': 'https://www.thomann.de/intl/',
        'priority': 3,
        'frequency': 'monthly',
        'parser': 'thomann_parser'
    },
    'mercadolibre_cl': {
        'base_url': 'https://listado.mercadolibre.cl/',
        'priority': 1,
        'frequency': 'weekly',
        'parser': 'mercadolibre_parser'
    }
}
```

### Dashboard interno (solo admin)

```
□ Vista de valoración por instrumento
□ Gráfico de historial de precios
□ Indicador de disponibilidad en Chile
□ Cálculo automático de cobro mínimo
□ Botón para forzar actualización manual
```

### Consideraciones técnicas

```
⚠️ Rate limiting para no ser bloqueado
⚠️ User-Agent rotativo
⚠️ Caché de resultados (no consultar mismo modelo 2 veces al día)
⚠️ Fallback si una fuente falla
⚠️ Logs de errores de scraping
```

## 6.3 Fase 3: Sistema de Reparaciones Completo (3-4 semanas)

### Backend

```
□ Endpoint para crear ficha desde cotización
□ Sistema de numeración CDS-XXX
□ Upload de fotos por etapa
□ Notificaciones por email (plantillas HTML)
□ Webhook para actualizaciones
□ API de firma digital simple
```

### Frontend

```
□ Dashboard técnico mejorado
□ Formulario de ficha de ingreso
□ Componente de carga de fotos
□ Timeline visual de estados
□ Vista de cliente de su reparación
□ Sistema de aprobación de cotización
```

### Emails transaccionales

```
□ Plantilla: Equipo recibido
□ Plantilla: Diagnóstico listo
□ Plantilla: En reparación
□ Plantilla: Esperando repuestos
□ Plantilla: Listo para retiro
□ Plantilla: Recordatorio de retiro
```

## 6.4 Fase 4: Agendamiento y Calendario (2 semanas)

### Backend

```
□ Integración Google Calendar API
□ Modelo Appointment
□ Endpoint para crear/modificar citas
□ Sincronización bidireccional
□ Recordatorios automáticos
```

### Frontend

```
□ Widget de selección de fecha/hora
□ Vista de disponibilidad
□ Confirmación de cita
□ Cancelación/reagendamiento
```

## 6.5 Fase 5: Sistema de Pagos (2-3 semanas)

### Backend

```
□ Integración Flow.cl API
□ Modelo Payment
□ Endpoint de inicio de pago
□ Webhook de confirmación
□ Historial de pagos
```

### Frontend

```
□ Carrito de repuestos
□ Checkout con Flow.cl
□ Historial de pagos del cliente
□ Comprobantes descargables
```

## 6.6 Fase 6: Optimización y Marketing (Continuo)

```
□ Google Analytics 4 configurado
□ Google Search Console
□ Schema.org markup (LocalBusiness)
□ Open Graph para redes sociales
□ Widget de WhatsApp
□ Integración Instagram feed
□ Sistema de reseñas
□ Blog técnico (SEO)
```

---

# 7. INTEGRACIÓN CON HOSTING cPanel

## 7.1 Estructura de Archivos en cPanel

```
/home/tuusuario/
├── public_html/                    # Frontend Vue (build)
│   ├── index.html
│   ├── assets/
│   └── .htaccess
│
├── backend/                        # Backend FastAPI
│   ├── app/
│   ├── venv/
│   ├── passenger_wsgi.py          # Archivo requerido por Passenger
│   └── requirements.txt
│
└── logs/
    ├── access.log
    └── error.log
```

## 7.2 Configuración de Python en cPanel

**Archivo: `passenger_wsgi.py`**

```python
import sys
import os

# Agregar el path de la aplicación
sys.path.insert(0, os.path.dirname(__file__))

# Importar la app FastAPI
from app.main import app as application
```

**Archivo: `.htaccess` en backend/**

```apache
PassengerAppRoot /home/tuusuario/backend
PassengerBaseURI /api
PassengerPython /home/tuusuario/backend/venv/bin/python
```

## 7.3 Configuración de MySQL

```python
# config.py para producción
database_url: str = os.getenv(
    "DATABASE_URL", 
    "mysql+pymysql://usuario:password@localhost/cirujano_db"
)
```

## 7.4 Configuración de Emails

```python
# Usando el SMTP de cPanel
SMTP_SERVER = "mail.cirujanodesintetizadores.cl"
SMTP_PORT = 465  # SSL
SMTP_USER = "noreply@cirujanodesintetizadores.cl"
FROM_EMAIL = "Cirujano de Sintetizadores <noreply@cirujanodesintetizadores.cl>"
```

## 7.5 SSL y Dominio

1. En cPanel → SSL/TLS → Instalar certificado Let's Encrypt
2. Forzar HTTPS en `.htaccess`:

```apache
RewriteEngine On
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
```

---

# 8. SEO, ANALYTICS Y MARKETING

## 8.1 SEO Técnico

### Meta tags esenciales

```html
<!-- index.html -->
<title>Cirujano de Sintetizadores | Reparación de Teclados y Sintetizadores en Chile</title>
<meta name="description" content="Servicio técnico especializado en reparación de sintetizadores, teclados, pianos electrónicos y equipos de audio. Cotiza en línea. Santiago, Chile.">
<meta name="keywords" content="reparación sintetizadores, teclados, KORG, Roland, Yamaha, servicio técnico, Chile">

<!-- Open Graph -->
<meta property="og:title" content="Cirujano de Sintetizadores">
<meta property="og:description" content="Reparación profesional de instrumentos electrónicos">
<meta property="og:image" content="https://cirujanodesintetizadores.cl/og-image.jpg">
<meta property="og:url" content="https://cirujanodesintetizadores.cl">

<!-- Twitter -->
<meta name="twitter:card" content="summary_large_image">
```

### Schema.org (LocalBusiness)

```json
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "Cirujano de Sintetizadores",
  "image": "https://cirujanodesintetizadores.cl/logo.png",
  "description": "Servicio técnico especializado en reparación de sintetizadores y teclados",
  "address": {
    "@type": "PostalAddress",
    "addressLocality": "Santiago",
    "addressCountry": "CL"
  },
  "telephone": "+56912345678",
  "priceRange": "$$",
  "openingHours": "Mo-Fr 09:00-18:00",
  "sameAs": [
    "https://instagram.com/cirujanodesintetizadores",
    "https://facebook.com/cirujanodesintetizadores"
  ]
}
```

## 8.2 Google Analytics 4

```html
<!-- En index.html, antes de </head> -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

### Eventos a trackear

```javascript
// Cotización iniciada
gtag('event', 'begin_quote', { instrument: 'KORG microKORG' });

// Cotización completada
gtag('event', 'complete_quote', { value: 45000, currency: 'CLP' });

// Cita agendada
gtag('event', 'schedule_appointment');

// Pago completado
gtag('event', 'purchase', { value: 85000, currency: 'CLP' });
```

## 8.3 Integraciones de Marketing

### WhatsApp Widget

```html
<a href="https://wa.me/56912345678?text=Hola,%20necesito%20cotizar%20una%20reparación" 
   class="whatsapp-float">
  <i class="fab fa-whatsapp"></i>
</a>
```

### Instagram Feed (Embebido)

```html
<script src="https://www.instagram.com/embed.js"></script>
<blockquote class="instagram-media" data-instgrm-permalink="...">
</blockquote>
```

---

# 9. PRESUPUESTO DE DESARROLLO

## 9.1 Si contratas desarrollador

| Fase                 | Horas estimadas       | Costo aprox (USD)         |
| -------------------- | --------------------- | ------------------------- |
| Fase 1: Fundamentos  | 40-60 hrs             | $800 - $1,500             |
| Fase 2: Cotizador    | 80-120 hrs            | $1,600 - $3,000           |
| Fase 3: Reparaciones | 60-80 hrs             | $1,200 - $2,000           |
| Fase 4: Calendario   | 30-40 hrs             | $600 - $1,000             |
| Fase 5: Pagos        | 40-60 hrs             | $800 - $1,500             |
| Fase 6: Marketing    | 20-30 hrs             | $400 - $750               |
| **TOTAL**      | **270-390 hrs** | **$5,400 - $9,750** |

## 9.2 Costos de Servicios Externos

| Servicio                     | Costo mensual         | Notas           |
| ---------------------------- | --------------------- | --------------- |
| Hosting actual               | ~$5-10 USD            | Ya pagado       |
| Cloudinary (imágenes)       | $0 (free tier)        | 25GB gratis     |
| Flow.cl                      | 2.9% por transacción | Sin mensualidad |
| Google Workspace             | $6 USD/usuario        | Opcional        |
| Dominio (.cl)                | ~$15 USD/año         | Ya pagado       |
| **Total fijo mensual** | **~$10-20 USD** |                 |

## 9.3 Si lo haces tú mismo (con mi ayuda)

Puedo ayudarte a implementar cada fase paso a paso. El costo sería solo tu tiempo y los servicios externos mínimos.

---

# 10. ROADMAP DE IMPLEMENTACIÓN

## Timeline Sugerido

```
2026
────────────────────────────────────────────────────────────────────────

ENERO                           FEBRERO                         MARZO
├── Semana 1-2 ──────────────┼── Semana 1-2 ─────────────────┼── Semana 1-2
│   FASE 1: Fundamentos      │   FASE 2: Cotizador           │   FASE 3: Reparaciones
│   • Seguridad              │   • Componentes visuales      │   • Flujo completo
│   • MySQL migration        │   • Cuestionario dinámico     │   • Emails automáticos
│   • SSL/dominio            │   • Cálculo de precios        │   • Dashboard técnico
│                            │                               │
├── Semana 3-4 ──────────────┼── Semana 3-4 ─────────────────┼── Semana 3-4
│   FASE 1: (cont.)          │   FASE 2: (cont.)             │   FASE 4: Calendario
│   • Políticas legales      │   • Testing                   │   • Google Calendar
│   • Analytics básico       │   • Ajustes UX                │   • Agendamiento
│   • Deploy inicial         │   • Deploy v2                 │   • Deploy v3
│                            │                               │
────────────────────────────────────────────────────────────────────────

ABRIL                           MAYO                            JUNIO+
├── Semana 1-4 ──────────────┼── Semana 1-4 ─────────────────┼── Continuo
│   FASE 5: Pagos            │   FASE 6: Marketing           │   OPTIMIZACIÓN
│   • Flow.cl integration    │   • SEO avanzado              │   • Nuevas features
│   • Carrito                │   • Redes sociales            │   • Feedback usuarios
│   • Historial              │   • Blog técnico              │   • Mejoras UX
│   • Deploy v4              │   • Deploy final              │   • Mantenimiento
│                            │                               │
────────────────────────────────────────────────────────────────────────
```

## Hitos Clave

| Fecha       | Hito             | Entregable                            |
| ----------- | ---------------- | ------------------------------------- |
| Fin Enero   | MVP Online       | Sitio básico funcionando con SSL     |
| Fin Febrero | Cotizador Live   | Clientes pueden cotizar online        |
| Fin Marzo   | Sistema Completo | Gestión de reparaciones + calendario |
| Fin Abril   | Pagos Activos    | Clientes pueden pagar online          |
| Fin Mayo    | Marketing Ready  | SEO + Redes integradas                |

---

# 11. PRÓXIMOS PASOS INMEDIATOS

## Esta semana deberías:

1. **Seguridad** (URGENTE)

   - [ ] Crear archivo `.env` con secretos reales
   - [ ] Nunca commitear `.env` a Git
2. **Hosting**

   - [ ] Acceder a cPanel
   - [ ] Verificar versión de Python disponible
   - [ ] Crear base de datos MySQL
3. **Dominio**

   - [ ] Apuntar DNS a tu hosting
   - [ ] Activar SSL gratuito
4. **Decisiones**

   - [ ] Definir precios base de reparación
   - [ ] Escribir borrador de políticas
   - [ ] Listar los 20 instrumentos más comunes que reparas

---

# 12. CONCLUSIÓN

Tu proyecto tiene una base sólida (60% del backend, 55% del frontend), pero necesita trabajo significativo para cumplir tu visión completa. Las prioridades son:

1. **🔴 CRÍTICO:** Seguridad antes de producción
2. **🟠 ALTO:** Sistema de cotización inteligente (tu diferenciador)
3. **🟡 MEDIO:** Flujo completo de reparaciones con notificaciones
4. **🟢 NORMAL:** Pagos, calendario, marketing

¿Por dónde quieres empezar? Puedo ayudarte con código específico para cualquiera de estas fases.

---

*Documento generado por Claude - Auditoría Técnica*
*Enero 2026*
