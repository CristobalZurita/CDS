# Sistema de Cotización Interactiva con Diagnóstico Visual
## Documentación Técnica Completa

---

## 📋 Tabla de Contenidos

1. [Descripción General](#descripción-general)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Tecnologías Utilizadas](#tecnologías-utilizadas)
4. [Instalación y Configuración](#instalación-y-configuración)
5. [Flujo de Usuario](#flujo-de-usuario)
6. [Flujo de Técnico](#flujo-de-técnico)
7. [API Endpoints](#api-endpoints)
8. [Base de Datos](#base-de-datos)
9. [Procesamiento de Imágenes](#procesamiento-de-imágenes)
10. [Cálculo de Cotizaciones](#cálculo-de-cotizaciones)

---

## 🎯 Descripción General

Sistema completo de diagnóstico visual interactivo para instrumentos musicales que permite:

### Para el Cliente:
- ✅ Seleccionar o subir fotos de su instrumento
- ✅ Completar planilla de componentes (teclas, botones, etc.)
- ✅ Marcar fallas directamente sobre las fotos (doble clic)
- ✅ Recibir cotización automática preliminar
- ✅ Aceptar disclaimer obligatorio
- ✅ Obtener código de referencia

### Para el Técnico:
- ✅ Revisar diagnósticos recibidos
- ✅ Ajustar cotizaciones
- ✅ Crear templates de instrumentos
- ✅ Usar OpenCV para detectar controles automáticamente
- ✅ Gestionar evidencia fotográfica
- ✅ Seguimiento de estado (pendiente → revisado → aprobado → completado)

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                         FRONTEND                            │
│  ┌──────────────────┐  ┌──────────────────┐               │
│  │ InteractiveDiag  │  │ TechnicianDash   │               │
│  │  (Cliente)       │  │   (Técnico)      │               │
│  └────────┬─────────┘  └─────────┬────────┘               │
│           │                       │                         │
└───────────┼───────────────────────┼─────────────────────────┘
            │                       │
            │      REST API         │
            ▼                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Diagnostic   │  │ Template     │  │ Quote        │     │
│  │ Endpoints    │  │ Manager      │  │ Calculator   │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
└─────────┼──────────────────┼──────────────────┼────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                   DATABASE (SQLite/PostgreSQL)               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Instrument│  │Diagnostic│  │ Photos   │  │  Quote   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
          ▲
          │
   ┌──────┴──────┐
   │   OpenCV    │
   │  (Python)   │
   └─────────────┘
```

---

## 💻 Tecnologías Utilizadas

### Frontend
- **Vue 3** (Composition API)
- **SCSS** para estilos
- **Canvas API** para markup de fotos
- **FileReader API** para upload de imágenes

### Backend
- **FastAPI** (Python 3.9+)
- **SQLAlchemy** (ORM)
- **Pydantic** (validación de datos)
- **OpenCV** (detección de controles)
- **Pillow** (procesamiento de imágenes)

### Base de Datos
- **SQLite** (desarrollo)
- **PostgreSQL** (producción recomendada)

---

## 🚀 Instalación y Configuración

### 1. Backend Setup

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# Instalar dependencias
pip install fastapi uvicorn sqlalchemy pydantic python-multipart
pip install opencv-python-headless numpy pillow

# Crear base de datos y seed data
python backend_api.py
# En otra terminal:
curl -X POST http://localhost:8000/api/admin/seed-database
```

### 2. Frontend Setup

```bash
# Instalar dependencias de Vue
npm install vue@3 vue-router@4

# Copiar componentes a tu proyecto Vue
# - InteractiveInstrumentDiagnostic.vue → /src/components/
# - TechnicianDashboard.vue → /src/components/

# Agregar rutas en router
```

### 3. Configuración de Rutas (Vue Router)

```javascript
// router/index.js
const routes = [
  {
    path: '/diagnostico',
    name: 'Diagnostic',
    component: () => import('@/components/InteractiveInstrumentDiagnostic.vue')
  },
  {
    path: '/dashboard-tecnico',
    name: 'TechnicianDashboard',
    component: () => import('@/components/TechnicianDashboard.vue'),
    meta: { requiresAuth: true }  // Solo técnicos
  }
]
```

### 4. Variables de Entorno

```bash
# .env
DATABASE_URL=sqlite:///./diagnostic_system.db
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_ORIGINS=http://localhost:8080,https://tudominio.com
```

---

## 👤 Flujo de Usuario (Cliente)

### Paso 1: Selección de Instrumento

```
Usuario → Busca en catálogo O sube fotos
       ↓
Sistema → Valida formato de imágenes
       ↓
Sistema → Asigna vista (frontal/trasera/cenital)
```

**Requisitos:**
- Mínimo 2 fotos (frontal y trasera recomendadas)
- Formatos: JPG, PNG, WEBP
- Tamaño máximo: 10MB por foto

### Paso 2: Completar Planilla

```
Usuario → Marca checkboxes de componentes existentes
       ↓
Sistema → Guarda componentes seleccionados
       ↓
Usuario → Ingresa cantidad si aplica (ej: 61 teclas)
```

**Categorías disponibles:**
- Teclas (keys, keybed, aftertouch)
- Controles (knobs, sliders, buttons, switches)
- Conectividad (audio I/O, MIDI, CV/Gate, USB)
- Otros (display, power, pedals, wheels)

### Paso 3: Marcado Visual Interactivo

```
Usuario → Selecciona tipo de falla (roto, faltante, suelto, etc.)
       ↓
Usuario → Doble clic sobre componente afectado en foto
       ↓
Sistema → Crea marcador visual con número y tipo
       ↓
Sistema → Almacena coordenadas (x, y) y tipo de falla
```

**Tipos de falla:**
1. 🔧 Roto - Componente dañado
2. ⊖ Faltante - Componente ausente
3. ⇄ Suelto - Componente inestable
4. 🔊 Ruidoso - Ruido o estática
5. 🔒 Atascado - Componente bloqueado
6. 🧪 Oxidado - Corrosión visible

**Funciones disponibles:**
- Cambiar entre fotos (tabs)
- Deshacer último marcador
- Limpiar todos los marcadores
- Editar marcador existente
- Ver lista de todas las fallas marcadas

### Paso 4: Cotización y Confirmación

```
Sistema → Calcula cotización preliminar
       ↓
Sistema → Muestra disclaimer obligatorio
       ↓
Usuario → Lee y acepta disclaimer
       ↓
Usuario → Envía diagnóstico
       ↓
Sistema → Genera código de referencia (DIAG-XXXXXXXX)
       ↓
Sistema → Envía email confirmación
```

**Cálculo de cotización incluye:**
- Tarifa base de diagnóstico: $25,000 CLP
- Costo de reparaciones (según tipo y cantidad de fallas)
- Factor de complejidad (según tier del instrumento)
- Ajuste por número de componentes
- Estimación de tiempo (días hábiles)

---

## 🔧 Flujo de Técnico

### Dashboard Principal

```
Técnico → Accede a dashboard
       ↓
Sistema → Muestra estadísticas (pendientes, en proceso, completados)
       ↓
Técnico → Selecciona diagnóstico
       ↓
Sistema → Muestra detalles completos
```

### Revisión de Diagnóstico

**Información disponible:**
1. Datos del cliente (nombre, email, teléfono)
2. Instrumento (marca, modelo, año)
3. Fotos con marcadores visibles
4. Lista de fallas agrupadas por tipo
5. Componentes identificados
6. Cotización preliminar

**Acciones disponibles:**
- Cambiar estado (pendiente → revisado → aprobado → completado)
- Ajustar cotización manualmente
- Agregar notas internas
- Enviar cotización ajustada al cliente
- Descargar reporte PDF

### Gestión de Templates

```
Técnico → Crea nuevo template
       ↓
Técnico → Sube fotos de referencia (frontal, trasera, cenital)
       ↓
Técnico → Click en "Detectar controles" (OpenCV)
       ↓
Sistema → Analiza foto y sugiere controles
       ↓
Técnico → Revisa y ajusta detección
       ↓
Técnico → Completa información de componentes
       ↓
Sistema → Guarda template para uso futuro
```

**Detección automática OpenCV:**
- Detecta círculos (knobs, botones)
- Detecta rectángulos (sliders, teclas)
- Calcula posición (x, y) y dimensiones
- Asigna confianza (0-1) a cada detección

---

## 🔌 API Endpoints

### Instrumentos

#### GET /api/instruments
Obtener catálogo de instrumentos

**Query Parameters:**
- `search` (opcional): Búsqueda por marca o modelo

**Response:**
```json
[
  {
    "id": 1,
    "brand": "Moog",
    "model": "Minimoog Model D",
    "year": 1970,
    "type": "Analog Synthesizer",
    "estimated_value": 5000000,
    "complexity_tier": "vintage",
    "front_photo_url": "/uploads/moog-minimoog.jpg",
    "template_json": {
      "keys": 44,
      "knobs": 24,
      "switches": 18,
      "wheels": 2
    }
  }
]
```

#### GET /api/instruments/{instrument_id}
Obtener detalles de un instrumento específico

#### POST /api/instruments/{instrument_id}/detect-controls
Detectar controles en una foto usando OpenCV

**Request:**
- Multipart form data con imagen

**Response:**
```json
{
  "instrument_id": 1,
  "detected_controls": [
    {
      "id": "detected_knob_1",
      "type": "knob",
      "x": 120,
      "y": 80,
      "radius": 15,
      "confidence": 0.85
    }
  ],
  "count": 24
}
```

### Diagnósticos

#### POST /api/diagnostics/submit
Enviar diagnóstico completo

**Request Body:**
```json
{
  "instrument_id": 1,
  "selected_components": ["keys", "knobs", "sliders"],
  "component_quantities": {
    "keys": 61,
    "knobs": 12,
    "sliders": 8
  },
  "photos": [
    {
      "view": "front",
      "base64_image": "data:image/jpeg;base64,...",
      "markers": [
        {
          "x": 150.5,
          "y": 200.3,
          "actual_x": 300,
          "actual_y": 400,
          "type": "broken",
          "timestamp": 1706543210000
        }
      ]
    }
  ],
  "customer_name": "Juan Pérez",
  "customer_email": "juan@email.com",
  "customer_phone": "+56912345678"
}
```

**Response:**
```json
{
  "success": true,
  "reference_code": "DIAG-ABC12345",
  "diagnostic_id": 42,
  "quote": {
    "base_diagnostic": 25000,
    "repair_cost": 45000,
    "complexity_factor": 1.35,
    "complexity_adjustment": 15750,
    "parts_cost": 0,
    "subtotal": 85750,
    "total": 85750,
    "estimated_days": 5,
    "breakdown": [
      {
        "description": "Reparación: broken",
        "type": "broken",
        "cost": 15000
      }
    ]
  }
}
```

#### GET /api/diagnostics/{reference_code}
Obtener estado de diagnóstico por código de referencia

### Cotizaciones

#### POST /api/quotes/{quote_id}/approve
Cliente aprueba cotización

**Response:**
```json
{
  "success": true,
  "message": "Quote approved"
}
```

---

## 🗄️ Base de Datos

### Modelo de Datos

```sql
-- Instrumentos del catálogo
CREATE TABLE instruments (
    id INTEGER PRIMARY KEY,
    brand VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    year INTEGER,
    type VARCHAR(50),
    estimated_value FLOAT,
    complexity_tier VARCHAR(20) DEFAULT 'standard',
    front_photo_url VARCHAR(255),
    back_photo_url VARCHAR(255),
    top_photo_url VARCHAR(255),
    template_json JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Fotos de referencia con mapas de controles
CREATE TABLE instrument_photos (
    id INTEGER PRIMARY KEY,
    instrument_id INTEGER REFERENCES instruments(id),
    view_type VARCHAR(20) NOT NULL,
    photo_url VARCHAR(255) NOT NULL,
    control_map JSON,
    width INTEGER,
    height INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Diagnósticos de clientes
CREATE TABLE diagnostics (
    id INTEGER PRIMARY KEY,
    reference_code VARCHAR(20) UNIQUE NOT NULL,
    customer_name VARCHAR(100),
    customer_email VARCHAR(100),
    customer_phone VARCHAR(20),
    instrument_id INTEGER REFERENCES instruments(id),
    custom_instrument_description TEXT,
    selected_components JSON NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Fotos subidas por clientes con marcadores
CREATE TABLE diagnostic_photos (
    id INTEGER PRIMARY KEY,
    diagnostic_id INTEGER REFERENCES diagnostics(id),
    view_type VARCHAR(20) NOT NULL,
    photo_url VARCHAR(255) NOT NULL,
    markers JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Cotizaciones generadas
CREATE TABLE quotes (
    id INTEGER PRIMARY KEY,
    diagnostic_id INTEGER UNIQUE REFERENCES diagnostics(id),
    base_diagnostic_fee FLOAT DEFAULT 25000,
    repair_cost FLOAT NOT NULL,
    complexity_adjustment FLOAT DEFAULT 0,
    parts_cost FLOAT DEFAULT 0,
    subtotal FLOAT NOT NULL,
    total FLOAT NOT NULL,
    estimated_days INTEGER DEFAULT 5,
    cost_breakdown JSON,
    approved_by_customer BOOLEAN DEFAULT FALSE,
    approved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Índices Recomendados

```sql
CREATE INDEX idx_instruments_brand ON instruments(brand);
CREATE INDEX idx_instruments_model ON instruments(model);
CREATE INDEX idx_diagnostics_reference ON diagnostics(reference_code);
CREATE INDEX idx_diagnostics_status ON diagnostics(status);
CREATE INDEX idx_diagnostics_created ON diagnostics(created_at);
```

---

## 🖼️ Procesamiento de Imágenes (OpenCV)

### Detección de Controles

#### 1. Detección de Círculos (Knobs, Botones)

```python
def detect_circles(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    circles = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        dp=1,              # Resolución inversa
        minDist=30,        # Distancia mínima entre centros
        param1=50,         # Umbral Canny superior
        param2=30,         # Umbral acumulador
        minRadius=10,      # Radio mínimo (10px)
        maxRadius=50       # Radio máximo (50px)
    )
    return circles
```

**Casos de uso:**
- Knobs rotatorios
- Botones circulares
- LEDs indicadores

#### 2. Detección de Rectángulos (Sliders, Teclas)

```python
def detect_rectangles(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    contours, _ = cv2.findContours(
        edges,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )
    
    rectangles = []
    for contour in contours:
        if cv2.contourArea(contour) > 100:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = float(w) / h
            
            # Filtrar por aspect ratio
            if 2 < aspect_ratio < 10:  # Sliders horizontales
                rectangles.append({
                    'type': 'slider',
                    'x': x + w/2,
                    'y': y + h/2,
                    'width': w,
                    'height': h
                })
    
    return rectangles
```

**Casos de uso:**
- Faders lineales
- Sliders
- Teclas de piano
- Botones rectangulares

### Mejoras Avanzadas (Futuras)

1. **Machine Learning:**
   - Entrenar CNN para clasificar tipos de controles
   - Usar YOLO para detección de objetos
   - Transfer learning con ResNet/VGG

2. **Preprocesamiento:**
   - Corrección de perspectiva (4-point transform)
   - Normalización de iluminación
   - Eliminación de ruido

3. **Post-procesamiento:**
   - Clustering de detecciones similares
   - Validación de posiciones lógicas
   - Interpolación para controles ocultos

---

## 💰 Cálculo de Cotizaciones

### Fórmula Base

```
TOTAL = BASE_DIAGNOSTIC + REPAIR_COST × COMPLEXITY_FACTOR + PARTS_COST
```

### Componentes del Cálculo

#### 1. Tarifa Base de Diagnóstico
```python
BASE_DIAGNOSTIC = 25000  # CLP
```

#### 2. Costo de Reparaciones por Tipo

```python
FAULT_BASE_PRICES = {
    "broken": 15000,    # Componente roto
    "missing": 20000,   # Componente faltante
    "loose": 8000,      # Componente suelto
    "noisy": 12000,     # Ruido/estática
    "stuck": 10000,     # Atascado
    "oxidized": 18000   # Oxidación
}

repair_cost = sum(FAULT_BASE_PRICES[marker.type] for marker in markers)
```

#### 3. Factor de Complejidad

**Por tier del instrumento:**
```python
COMPLEXITY_TIERS = {
    "simple": 1.0,      # Instrumentos básicos
    "standard": 1.2,    # Instrumentos estándar
    "complex": 1.5,     # Instrumentos complejos
    "vintage": 2.0      # Instrumentos vintage (partes escasas)
}
```

**Por dificultad de componentes:**
```python
COMPONENT_DIFFICULTY = {
    "keys": 1.5,        # Teclas (mecánica compleja)
    "keybed": 2.0,      # Lecho de teclas (difícil)
    "knobs": 1.0,       # Knobs (estándar)
    "sliders": 1.2,     # Sliders (mediano)
    "buttons": 0.8,     # Botones (fácil)
    "switches": 0.9,    # Switches (fácil)
    "audio_out": 1.3,   # Conectores audio (soldadura)
    "midi": 1.1,        # MIDI (estándar)
    "display": 2.5,     # Display (muy difícil)
    "power": 2.0        # Fuente de poder (riesgo alto)
}
```

**Cálculo combinado:**
```python
base_complexity = COMPLEXITY_TIERS[instrument.tier]

component_complexity = sum(
    (COMPONENT_DIFFICULTY[comp] - 1.0) × quantity × 0.1
    for comp, quantity in components.items()
)

complexity_factor = base_complexity + component_complexity
complexity_adjustment = repair_cost × (complexity_factor - 1.0)
```

#### 4. Costo de Partes

```python
parts_cost = count_missing_faults × 15000  # Promedio por parte
```

#### 5. Estimación de Tiempo

```python
estimated_days = max(3, min(15, 
    num_faults + (num_components // 5)
))
```

**Rangos:**
- Mínimo: 3 días hábiles
- Máximo: 15 días hábiles

### Ejemplo Completo

**Input:**
- Instrumento: Moog Minimoog (vintage, tier = 2.0)
- Componentes: 44 teclas, 24 knobs, 18 switches
- Fallas: 3 knobs rotos, 2 keys sueltas, 1 oxidación

**Cálculo:**
```
BASE_DIAGNOSTIC = 25,000

REPAIR_COST:
  3 × broken (15,000) = 45,000
  2 × loose (8,000) = 16,000
  1 × oxidized (18,000) = 18,000
  TOTAL = 79,000

COMPLEXITY_FACTOR:
  Base (vintage) = 2.0
  Keys: (1.5 - 1.0) × 44 × 0.1 = 2.2
  Knobs: (1.0 - 1.0) × 24 × 0.1 = 0
  Switches: (0.9 - 1.0) × 18 × 0.1 = -0.18
  TOTAL = 2.0 + 2.2 + 0 - 0.18 = 4.02

COMPLEXITY_ADJUSTMENT:
  79,000 × (4.02 - 1.0) = 238,580

PARTS_COST:
  0 × 15,000 = 0

TOTAL:
  25,000 + 79,000 + 238,580 + 0 = 342,580 CLP

ESTIMATED_DAYS:
  6 faults + (87 components / 5) = 23.4
  max(3, min(15, 23)) = 15 días
```

---

## 🔐 Seguridad y Validación

### Validación de Entrada

```python
# Pydantic schemas automáticamente validan
class DiagnosticSubmission(BaseModel):
    customer_email: EmailStr  # Valida formato email
    selected_components: List[str]  # No vacío
    photos: List[PhotoSubmission]  # Mínimo 1 foto
    
    @validator('photos')
    def validate_photos(cls, v):
        if len(v) < 2:
            raise ValueError('Mínimo 2 fotos requeridas')
        return v
```

### Sanitización de Archivos

```python
def validate_image(file: UploadFile):
    # Verificar tipo MIME
    if not file.content_type.startswith('image/'):
        raise HTTPException(400, "Archivo no es una imagen")
    
    # Verificar tamaño
    file.file.seek(0, 2)  # Ir al final
    size = file.file.tell()
    if size > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(400, "Archivo muy grande")
    
    file.file.seek(0)  # Volver al inicio
    
    # Verificar que es imagen válida
    try:
        img = Image.open(file.file)
        img.verify()
    except:
        raise HTTPException(400, "Archivo corrupto")
    
    return True
```

### Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/diagnostics/submit")
@limiter.limit("5/hour")  # Máximo 5 diagnósticos por hora
async def submit_diagnostic(...):
    ...
```

---

## 📊 Métricas y Monitoreo

### KPIs Sugeridos

1. **Conversión:**
   - % de diagnósticos que llegan a Paso 4
   - % de cotizaciones aprobadas por clientes
   - Tiempo promedio desde envío hasta aprobación

2. **Calidad:**
   - Precisión de cotizaciones (comparar preliminar vs final)
   - Tiempo real de reparación vs estimado
   - Satisfacción del cliente (NPS)

3. **Operacional:**
   - Número de diagnósticos por día
   - Tiempo promedio de revisión por técnico
   - Utilización de templates vs custom

### Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('diagnostic_system.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

@app.post("/api/diagnostics/submit")
async def submit_diagnostic(...):
    logger.info(f"New diagnostic submission: {reference_code}")
    logger.debug(f"Components: {submission.selected_components}")
    logger.info(f"Quote calculated: {quote_calc.total} CLP")
```

---

## 🚀 Deployment

### Producción con Docker

**Dockerfile:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Instalar dependencias del sistema para OpenCV
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "backend_api:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/diagnostic
    volumes:
      - ./uploads:/app/uploads
    depends_on:
      - db
  
  db:
    image: postgres:14
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: diagnostic
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  postgres_data:
```

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name tudominio.com;

    location /api/ {
        proxy_pass http://backend:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /uploads/ {
        alias /var/www/uploads/;
    }

    location / {
        root /var/www/frontend;
        try_files $uri $uri/ /index.html;
    }
}
```

---

## 📝 Testing

### Tests Unitarios (pytest)

```python
# test_quotation.py
def test_calculate_quote_basic():
    instrument = InstrumentModel(
        brand="Test",
        model="Test Model",
        complexity_tier="standard"
    )
    
    markers = [
        FaultMarker(x=0, y=0, actual_x=0, actual_y=0, 
                   type="broken", timestamp=0)
    ]
    
    quote = calculate_quote(instrument, markers, ["keys"], {"keys": 44})
    
    assert quote.base_diagnostic == 25000
    assert quote.repair_cost == 15000
    assert quote.total > 25000

def test_complexity_vintage():
    instrument = InstrumentModel(complexity_tier="vintage")
    markers = [FaultMarker(..., type="broken", ...)]
    
    quote = calculate_quote(instrument, markers, [], {})
    
    assert quote.complexity_factor >= 2.0
```

### Tests de Integración

```python
from fastapi.testclient import TestClient

client = TestClient(app)

def test_submit_diagnostic():
    payload = {
        "selected_components": ["keys", "knobs"],
        "photos": [
            {
                "view": "front",
                "base64_image": "data:image/jpeg;base64,/9j/4AAQ...",
                "markers": [...]
            }
        ],
        "customer_email": "test@test.com"
    }
    
    response = client.post("/api/diagnostics/submit", json=payload)
    
    assert response.status_code == 200
    assert "reference_code" in response.json()
```

---

## 🐛 Troubleshooting

### Problemas Comunes

1. **OpenCV no detecta controles:**
   - Verificar iluminación de la foto
   - Ajustar parámetros de HoughCircles
   - Probar con preprocesamiento (blur, threshold)

2. **Cálculo de cotización incorrecto:**
   - Verificar que FAULT_BASE_PRICES esté actualizado
   - Revisar complexity_tier del instrumento
   - Verificar component_quantities en request

3. **Fotos no se guardan:**
   - Verificar permisos de directorio `uploads/`
   - Verificar tamaño de imagen (máximo 10MB)
   - Revisar formato de base64

4. **Performance lento:**
   - Agregar índices a tablas
   - Optimizar queries con `.join()`
   - Implementar cache con Redis
   - Comprimir imágenes antes de guardar

---

## 📚 Próximos Pasos

### Mejoras Sugeridas

1. **Email Notifications:**
   - Enviar confirmación al cliente
   - Notificar técnico de nuevos diagnósticos
   - Recordatorios de cotización pendiente

2. **PDF Generation:**
   - Generar reporte PDF con fotos marcadas
   - Incluir desglose detallado de costos
   - Firma digital para aprobación

3. **Payment Integration:**
   - Integrar Webpay/Mercadopago
   - Permitir pago online de diagnóstico
   - Sistema de anticipos

4. **Mobile App:**
   - Versión nativa iOS/Android
   - Captura de fotos optimizada
   - Notificaciones push

5. **ML Improvements:**
   - Entrenar modelo custom para instrumentos
   - Clasificación automática de fallas
   - Sugerencias de reparación

---

## 📞 Soporte

Para preguntas o reportar bugs:
- Email: soporte@tudominio.com
- GitHub: https://github.com/tu-repo/diagnostic-system
- Documentación: https://docs.tudominio.com

---

## 📄 Licencia

MIT License - Ver LICENSE.txt para más detalles

---

**Versión:** 1.0.0  
**Última actualización:** Enero 2026  
**Autor:** Tu Empresa
