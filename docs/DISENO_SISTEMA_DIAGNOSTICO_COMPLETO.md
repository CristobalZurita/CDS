# Sistema de Diagnóstico Visual Completo
## Cirujano de Sintetizadores - Diseño Técnico v2

---

## 1. Arquitectura General

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              ARQUITECTURA                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   FRONTEND (Vue 3)                         BACKEND (FastAPI)                │
│   ┌─────────────────┐                      ┌─────────────────┐              │
│   │ Cliente Público │◄────────────────────►│ /api/templates  │              │
│   │ - Cotizar       │                      │ /api/uploads    │              │
│   │ - Ver estado    │                      │ /api/diagnostic │              │
│   └─────────────────┘                      │ /api/evidence   │              │
│                                            └────────┬────────┘              │
│   ┌─────────────────┐                               │                       │
│   │ Dashboard Admin │◄──────────────────────────────┤                       │
│   │ - Diagnosticar  │                               │                       │
│   │ - Marcar fallas │                               ▼                       │
│   │ - Subir fotos   │                      ┌─────────────────┐              │
│   │ - Timeline      │                      │   PostgreSQL    │              │
│   └─────────────────┘                      │   + S3/MinIO    │              │
│                                            │   (fotos)       │              │
│                                            └─────────────────┘              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Modelos de Base de Datos

### 2.1 Esquema SQL

```sql
-- ============================================
-- TEMPLATES DE INSTRUMENTOS
-- ============================================

-- Marcas de instrumentos
CREATE TABLE instrument_brands (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,      -- "Yamaha", "Roland", "Korg"
    slug VARCHAR(100) NOT NULL UNIQUE,      -- "yamaha", "roland", "korg"
    logo_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Categorías de instrumentos
CREATE TABLE instrument_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,             -- "Sintetizador", "Teclado", "Drum Machine"
    slug VARCHAR(100) NOT NULL UNIQUE
);

-- Templates de instrumentos (el catálogo maestro)
CREATE TABLE instrument_templates (
    id SERIAL PRIMARY KEY,
    brand_id INTEGER REFERENCES instrument_brands(id),
    category_id INTEGER REFERENCES instrument_categories(id),

    model VARCHAR(200) NOT NULL,            -- "DX7", "Juno-106", "MS-20"
    slug VARCHAR(200) NOT NULL UNIQUE,      -- "yamaha-dx7", "roland-juno-106"
    year_start INTEGER,                     -- 1983
    year_end INTEGER,                       -- 1986 (null si aún se fabrica)

    -- Imagen principal del template
    image_url VARCHAR(500) NOT NULL,
    image_width INTEGER NOT NULL,
    image_height INTEGER NOT NULL,
    thumbnail_url VARCHAR(500),

    -- Especificaciones técnicas
    specs JSONB DEFAULT '{}',               -- {"keys": 61, "polyphony": 16, ...}

    -- Mapa de componentes (zonas clickeables)
    component_map JSONB NOT NULL DEFAULT '{}',

    -- Estado del template
    status VARCHAR(20) DEFAULT 'draft',     -- 'draft', 'published', 'archived'
    is_verified BOOLEAN DEFAULT FALSE,      -- Template verificado por técnico
    verified_by INTEGER REFERENCES users(id),
    verified_at TIMESTAMP,

    -- Estadísticas
    usage_count INTEGER DEFAULT 0,          -- Cuántas veces se ha usado

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(brand_id, model)
);

-- Índices para búsqueda rápida
CREATE INDEX idx_templates_brand ON instrument_templates(brand_id);
CREATE INDEX idx_templates_category ON instrument_templates(category_id);
CREATE INDEX idx_templates_status ON instrument_templates(status);
CREATE INDEX idx_templates_slug ON instrument_templates(slug);


-- ============================================
-- CATÁLOGO DE FALLAS
-- ============================================

-- Tipos de componentes
CREATE TABLE component_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,       -- 'key', 'button', 'knob', 'slider', etc.
    label VARCHAR(100) NOT NULL,            -- 'Tecla', 'Botón', 'Potenciómetro'
    icon VARCHAR(50),                       -- Icono para UI
    color VARCHAR(7)                        -- Color hex para visualización
);

INSERT INTO component_types (name, label, icon, color) VALUES
    ('key', 'Tecla', 'piano', '#FFFFFF'),
    ('button', 'Botón', 'circle', '#4CAF50'),
    ('knob', 'Potenciómetro', 'adjust', '#2196F3'),
    ('slider', 'Slider/Fader', 'sliders-h', '#FF9800'),
    ('connector', 'Conector', 'plug', '#9C27B0'),
    ('display', 'Display', 'tv', '#00BCD4'),
    ('switch', 'Switch', 'toggle-on', '#795548');

-- Catálogo de fallas posibles
CREATE TABLE fault_catalog (
    id SERIAL PRIMARY KEY,
    component_type_id INTEGER REFERENCES component_types(id),

    code VARCHAR(50) NOT NULL UNIQUE,       -- 'KEY_NO_SOUND', 'POT_SCRATCHY'
    name VARCHAR(100) NOT NULL,             -- 'Tecla sin sonido'
    description TEXT,                       -- Descripción detallada

    -- Costos base
    base_labor_cost INTEGER NOT NULL,       -- Costo mano de obra (CLP)
    base_parts_cost INTEGER DEFAULT 0,      -- Costo repuestos estimado
    estimated_time_minutes INTEGER,         -- Tiempo estimado

    -- Repuestos típicos necesarios
    typical_parts JSONB DEFAULT '[]',       -- ["rubber_contact", "spring"]

    -- Causas comunes
    common_causes TEXT[],

    -- Nivel de dificultad (para priorización)
    difficulty_level INTEGER DEFAULT 1,     -- 1-5

    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Datos iniciales del catálogo
INSERT INTO fault_catalog (component_type_id, code, name, base_labor_cost, estimated_time_minutes) VALUES
    -- Fallas de teclas
    (1, 'KEY_NO_SOUND', 'Tecla sin sonido', 5000, 15),
    (1, 'KEY_STUCK', 'Tecla atascada', 8000, 20),
    (1, 'KEY_DOUBLE_TRIGGER', 'Tecla dispara doble', 4000, 10),
    (1, 'KEY_VELOCITY_FAIL', 'Velocidad no funciona', 6000, 20),
    (1, 'KEY_BROKEN', 'Tecla rota físicamente', 15000, 30),

    -- Fallas de potenciómetros
    (3, 'POT_SCRATCHY', 'Potenciómetro con ruido', 12000, 25),
    (3, 'POT_DEAD', 'Potenciómetro muerto', 15000, 30),
    (3, 'POT_JUMPING', 'Valores saltan', 10000, 20),

    -- Fallas de sliders
    (4, 'SLIDER_SCRATCHY', 'Slider con ruido', 10000, 20),
    (4, 'SLIDER_DEAD_SPOT', 'Zona muerta en slider', 12000, 25),
    (4, 'SLIDER_BROKEN', 'Slider roto', 18000, 35),

    -- Fallas de botones
    (2, 'BTN_NO_RESPONSE', 'Botón sin respuesta', 6000, 15),
    (2, 'BTN_INTERMITTENT', 'Botón intermitente', 8000, 20),
    (2, 'BTN_STUCK', 'Botón atascado', 7000, 15),

    -- Fallas de conectores
    (5, 'CONN_NO_SIGNAL', 'Sin señal', 15000, 30),
    (5, 'CONN_NOISE', 'Ruido/estática', 12000, 25),
    (5, 'CONN_INTERMITTENT', 'Conexión intermitente', 10000, 20),

    -- Fallas de display
    (6, 'DISP_DEAD', 'Display muerto', 45000, 60),
    (6, 'DISP_FADED', 'Display desvanecido', 35000, 45),
    (6, 'DISP_PIXELS', 'Pixeles muertos', 40000, 50);


-- ============================================
-- DIAGNÓSTICOS Y COTIZACIONES
-- ============================================

-- Sesión de diagnóstico (cada vez que alguien usa el sistema)
CREATE TABLE diagnostic_sessions (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT gen_random_uuid() UNIQUE,

    -- Quién inició el diagnóstico
    user_id INTEGER REFERENCES users(id),   -- NULL si es cliente anónimo
    client_email VARCHAR(255),              -- Email si no está logueado
    client_name VARCHAR(255),

    -- Instrumento
    template_id INTEGER REFERENCES instrument_templates(id),

    -- Si es instrumento nuevo (no existe template)
    is_custom_instrument BOOLEAN DEFAULT FALSE,
    custom_brand VARCHAR(100),
    custom_model VARCHAR(200),
    custom_image_url VARCHAR(500),

    -- Estado
    status VARCHAR(30) DEFAULT 'in_progress',  -- 'in_progress', 'completed', 'converted'
    -- converted = se convirtió en reparación real

    -- Vinculación con reparación (si se convierte)
    repair_id INTEGER REFERENCES repairs(id),

    -- Cotización calculada
    total_labor_cost INTEGER DEFAULT 0,
    total_parts_cost INTEGER DEFAULT 0,
    total_estimated INTEGER DEFAULT 0,

    -- Notas
    client_notes TEXT,                      -- Notas del cliente
    technician_notes TEXT,                  -- Notas del técnico

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- Fallas marcadas en un diagnóstico
CREATE TABLE diagnostic_faults (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES diagnostic_sessions(id) ON DELETE CASCADE,

    -- Qué componente
    component_id VARCHAR(100) NOT NULL,     -- 'key-23', 'btn-algorithm', etc.
    component_type VARCHAR(50) NOT NULL,    -- 'key', 'button', 'knob'
    component_label VARCHAR(200),           -- 'Tecla 24 (C3)', 'Botón Algorithm'

    -- Posición en la imagen (para renderizar marcador)
    position_x INTEGER NOT NULL,
    position_y INTEGER NOT NULL,

    -- Tipo de falla
    fault_id INTEGER REFERENCES fault_catalog(id),

    -- Costos (pueden sobrescribir los del catálogo)
    labor_cost INTEGER,
    parts_cost INTEGER,

    -- Notas específicas
    notes TEXT,

    -- Marcado por
    marked_by INTEGER REFERENCES users(id), -- NULL si es cliente
    marked_at TIMESTAMP DEFAULT NOW(),

    -- Prioridad (para orden de reparación)
    priority INTEGER DEFAULT 1              -- 1=normal, 2=alta, 3=crítica
);

CREATE INDEX idx_diag_faults_session ON diagnostic_faults(session_id);


-- ============================================
-- SISTEMA DE EVIDENCIA FOTOGRÁFICA
-- ============================================

-- Fotos de evidencia (timeline de reparación)
CREATE TABLE repair_evidence (
    id SERIAL PRIMARY KEY,
    repair_id INTEGER REFERENCES repairs(id) ON DELETE CASCADE,

    -- Tipo de evidencia
    evidence_type VARCHAR(30) NOT NULL,
    -- 'initial_client'     = Foto subida por cliente al cotizar
    -- 'initial_technician' = Foto tomada por técnico al recibir
    -- 'diagnostic'         = Foto durante diagnóstico (mostrando falla)
    -- 'progress'           = Foto de avance de trabajo
    -- 'before_after'       = Comparativa antes/después
    -- 'internal'           = Foto interna del instrumento
    -- 'final'              = Foto final post-reparación

    -- Archivo
    image_url VARCHAR(500) NOT NULL,
    thumbnail_url VARCHAR(500),

    -- Metadatos de imagen
    original_filename VARCHAR(255),
    file_size INTEGER,
    mime_type VARCHAR(50),
    width INTEGER,
    height INTEGER,

    -- Anotaciones sobre la imagen
    annotations JSONB DEFAULT '[]',
    -- [{"x": 150, "y": 200, "type": "marker", "label": "Daño aquí", "color": "red"}]

    -- Descripción
    caption TEXT,
    notes TEXT,

    -- Visibilidad
    is_visible_to_client BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT FALSE,      -- Mostrar destacada en timeline

    -- Orden en timeline
    display_order INTEGER DEFAULT 0,

    -- Quién subió
    uploaded_by INTEGER REFERENCES users(id),
    uploaded_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_evidence_repair ON repair_evidence(repair_id);
CREATE INDEX idx_evidence_type ON repair_evidence(evidence_type);


-- ============================================
-- FOTOS SUBIDAS POR CLIENTES (INSTRUMENTOS NUEVOS)
-- ============================================

CREATE TABLE client_instrument_uploads (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT gen_random_uuid() UNIQUE,

    -- Cliente
    user_id INTEGER REFERENCES users(id),
    client_email VARCHAR(255),

    -- Información del instrumento
    brand_name VARCHAR(100) NOT NULL,
    model_name VARCHAR(200) NOT NULL,
    year_approximate INTEGER,
    serial_number VARCHAR(100),

    -- Imagen subida
    image_url VARCHAR(500) NOT NULL,
    image_width INTEGER,
    image_height INTEGER,
    original_filename VARCHAR(255),

    -- Validación de la imagen
    validation_status VARCHAR(20) DEFAULT 'pending',
    -- 'pending', 'approved', 'rejected', 'needs_retake'
    validation_notes TEXT,
    validated_by INTEGER REFERENCES users(id),
    validated_at TIMESTAMP,

    -- Si se convierte en template oficial
    converted_to_template_id INTEGER REFERENCES instrument_templates(id),

    -- Sesión de diagnóstico asociada
    diagnostic_session_id INTEGER REFERENCES diagnostic_sessions(id),

    created_at TIMESTAMP DEFAULT NOW()
);

-- Reglas de validación para subidas
CREATE TABLE upload_validation_rules (
    id SERIAL PRIMARY KEY,
    rule_type VARCHAR(50) NOT NULL,         -- 'dimension', 'format', 'size', 'content'
    rule_key VARCHAR(50) NOT NULL,
    rule_value VARCHAR(200) NOT NULL,
    error_message TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

INSERT INTO upload_validation_rules (rule_type, rule_key, rule_value, error_message) VALUES
    ('dimension', 'min_width', '1200', 'La imagen debe tener al menos 1200px de ancho'),
    ('dimension', 'min_height', '400', 'La imagen debe tener al menos 400px de alto'),
    ('dimension', 'max_width', '4000', 'La imagen no debe exceder 4000px de ancho'),
    ('dimension', 'max_height', '3000', 'La imagen no debe exceder 3000px de alto'),
    ('dimension', 'aspect_ratio_min', '2.0', 'La foto debe ser horizontal (vista frontal)'),
    ('dimension', 'aspect_ratio_max', '5.0', 'La proporción de la imagen no es válida'),
    ('size', 'max_bytes', '10485760', 'El archivo no debe exceder 10MB'),
    ('format', 'allowed_types', 'image/jpeg,image/png,image/webp', 'Solo se permiten imágenes JPG, PNG o WebP'),
    ('content', 'require_instrument', 'true', 'La foto debe mostrar el instrumento completo de frente');
```

---

## 3. Flujo de Usuario: Cliente Cotizando Online

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FLUJO: CLIENTE COTIZA ONLINE                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PASO 1: Seleccionar Instrumento                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────────────┐    │    │
│  │  │ Yamaha  │  │ Roland  │  │  Korg   │  │ No encuentro mi     │    │    │
│  │  │  DX7    │  │ Juno106 │  │  MS-20  │  │ instrumento         │    │    │
│  │  │  ✓      │  │         │  │         │  │ [SUBIR FOTO]        │    │    │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────────────────┘    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  PASO 2A: Si existe template → Mostrar imagen con zonas                     │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  [Imagen del DX7 con zonas clickeables]                              │    │
│  │                                                                      │    │
│  │  "Haga clic en cada componente que presenta problemas"               │    │
│  │                                                                      │    │
│  │  Fallas marcadas: 3                                                  │    │
│  │  - Tecla 24: Sin sonido                                              │    │
│  │  - Slider Data: Ruido                                                │    │
│  │  - Botón Store: No responde                                          │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  PASO 2B: Si NO existe template → Subir foto                                │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  📤 SUBIR FOTO DE SU INSTRUMENTO                                     │    │
│  │                                                                      │    │
│  │  Requisitos:                                                         │    │
│  │  ✓ Foto frontal completa del instrumento                             │    │
│  │  ✓ Buena iluminación, sin reflejos                                   │    │
│  │  ✓ Mínimo 1200x400 pixeles                                           │    │
│  │  ✓ Formato JPG o PNG (máx 10MB)                                      │    │
│  │                                                                      │    │
│  │  Marca: [Yamaha        ▼]                                            │    │
│  │  Modelo: [____________]                                              │    │
│  │  Año aprox: [1985]                                                   │    │
│  │                                                                      │    │
│  │  [Arrastrar imagen aquí o clic para seleccionar]                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  PASO 3: Describir síntomas (si subió foto sin template)                    │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Ya que no tenemos mapa de su instrumento, describa los problemas:   │    │
│  │                                                                      │    │
│  │  □ Teclas con problemas    ¿Cuántas? [3]  ¿Cuáles? [___________]     │    │
│  │  □ Botones defectuosos     ¿Cuántos? [_]                             │    │
│  │  □ Potenciómetros          ¿Cuántos? [_]  Tipo: [Ruido/Muerto/...]   │    │
│  │  □ Sliders/Faders          ¿Cuántos? [_]                             │    │
│  │  □ Conectores              ¿Cuáles? [___________]                    │    │
│  │  □ Display                 Problema: [___________]                   │    │
│  │  □ Otro                    Descripción: [___________]                │    │
│  │                                                                      │    │
│  │  Descripción adicional:                                              │    │
│  │  [_______________________________________________]                   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  PASO 4: Cotización estimada                                                │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  ⚠️ COTIZACIÓN INDICATIVA                                            │    │
│  │                                                                      │    │
│  │  Instrumento: Yamaha DX7                                             │    │
│  │  Fallas detectadas: 3                                                │    │
│  │                                                                      │    │
│  │  Mano de obra estimada:    $23.000                                   │    │
│  │  Repuestos estimados:      $ 8.000                                   │    │
│  │  ─────────────────────────────────                                   │    │
│  │  TOTAL ESTIMADO:           $31.000 CLP                               │    │
│  │                                                                      │    │
│  │  [Ver disclaimer] [Solicitar diagnóstico formal →]                   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Flujo de Usuario: Técnico en Dashboard

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FLUJO: TÉCNICO DIAGNOSTICA EN DASH                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PASO 1: Ver solicitud de diagnóstico                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  📋 NUEVA SOLICITUD #4521                                            │    │
│  │                                                                      │    │
│  │  Cliente: Juan Pérez                                                 │    │
│  │  Instrumento: Yamaha DX7 (1985)                                      │    │
│  │  Fecha solicitud: 28/01/2026                                         │    │
│  │                                                                      │    │
│  │  Síntomas reportados por cliente:                                    │    │
│  │  - 3 teclas sin sonido                                               │    │
│  │  - Slider con ruido                                                  │    │
│  │  - Botón Store no responde                                           │    │
│  │                                                                      │    │
│  │  Cotización online del cliente: $31.000                              │    │
│  │                                                                      │    │
│  │  [Ver foto del cliente] [Iniciar diagnóstico →]                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  PASO 2: Trabajar sobre foto REAL (del cliente o propia)                    │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  🔧 DIAGNÓSTICO TÉCNICO - DX7 de Juan Pérez                          │    │
│  │                                                                      │    │
│  │  Foto: [Usar template] [Usar foto cliente] [Subir foto propia]       │    │
│  │                                                                      │    │
│  │  ┌───────────────────────────────────────────────────────────────┐   │    │
│  │  │                                                               │   │    │
│  │  │  [FOTO REAL DEL INSTRUMENTO DEL CLIENTE]                      │   │    │
│  │  │                                                               │   │    │
│  │  │     ❌ ← Click = Marcar falla aquí                            │   │    │
│  │  │              Tecla 24 - Sin sonido                            │   │    │
│  │  │                                                               │   │    │
│  │  │           ❌ ← Slider Data Entry - Ruido al mover             │   │    │
│  │  │                                                               │   │    │
│  │  └───────────────────────────────────────────────────────────────┘   │    │
│  │                                                                      │    │
│  │  Panel de fallas: [+ Agregar] [Lista: 5 fallas]                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  PASO 3: Documentar con fotos adicionales                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  📸 EVIDENCIA FOTOGRÁFICA                                            │    │
│  │                                                                      │    │
│  │  [+ Subir foto diagnóstico]                                          │    │
│  │  [+ Subir foto interna]                                              │    │
│  │  [+ Subir foto progreso]                                             │    │
│  │                                                                      │    │
│  │  Timeline de evidencia:                                              │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐             │    │
│  │  │ Inicial  │  │Diagnóst. │  │ Interno  │  │ Avance 1 │             │    │
│  │  │ Cliente  │  │ Técnico  │  │ Abierto  │  │ 30%      │             │    │
│  │  │ 28/01    │  │ 29/01    │  │ 29/01    │  │ 01/02    │             │    │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘             │    │
│  │                                                                      │    │
│  │  □ Mostrar al cliente   □ Marcar como destacada                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  PASO 4: Generar cotización formal                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  📋 COTIZACIÓN FORMAL                                                │    │
│  │                                                                      │    │
│  │  Fallas confirmadas: 5                                               │    │
│  │  (2 adicionales detectadas en diagnóstico)                           │    │
│  │                                                                      │    │
│  │  Desglose:                                                           │    │
│  │  - 3x Teclas sin sonido          $15.000                             │    │
│  │  - 1x Slider con ruido           $12.000                             │    │
│  │  - 1x Botón sin respuesta        $ 6.000                             │    │
│  │  - 1x Condensador inflado (NEW)  $18.000                             │    │
│  │  - 1x Pista oxidada (NEW)        $25.000                             │    │
│  │  ────────────────────────────────────────                            │    │
│  │  Mano de obra:                   $76.000                             │    │
│  │  Repuestos estimados:            $22.800                             │    │
│  │  ────────────────────────────────────────                            │    │
│  │  TOTAL:                          $98.800 CLP                         │    │
│  │                                                                      │    │
│  │  [Guardar borrador] [Enviar al cliente →]                            │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Componentes Vue Necesarios

### 5.1 Estructura de Carpetas

```
src/vue/components/diagnostic/
├── InstrumentSelector.vue         # Selector de marca/modelo
├── InstrumentTemplateGrid.vue     # Grid de templates disponibles
├── InstrumentUploader.vue         # Uploader para instrumentos nuevos
├── DiagnosticCanvas.vue           # Canvas interactivo principal
├── FaultMarkerOverlay.vue         # Overlay SVG con marcadores
├── FaultListPanel.vue             # Panel lateral de fallas
├── FaultSelectionModal.vue        # Modal para elegir tipo de falla
├── QuotationSummary.vue           # Resumen de cotización
├── EvidenceGallery.vue            # Galería de fotos de evidencia
├── EvidenceUploader.vue           # Subida de fotos de evidencia
├── EvidenceTimeline.vue           # Timeline visual de fotos
└── AnnotationTool.vue             # Herramienta para anotar fotos

src/vue/content/pages/
├── CotizadorPage.vue              # Página pública de cotización
└── admin/
    ├── DiagnosticPage.vue         # Diagnóstico para técnico
    └── EvidenceManagementPage.vue # Gestión de evidencias
```

### 5.2 Componente Principal: DiagnosticCanvas

```vue
<!-- src/vue/components/diagnostic/DiagnosticCanvas.vue -->
<template>
  <div class="diagnostic-canvas">
    <!-- Toolbar -->
    <div class="canvas-toolbar">
      <div class="toolbar-left">
        <span class="instrument-name">
          {{ instrument.brand }} {{ instrument.model }}
        </span>
      </div>
      <div class="toolbar-right">
        <button
          v-if="canUseTemplate"
          :class="['btn-source', { active: imageSource === 'template' }]"
          @click="setImageSource('template')"
        >
          Usar Template
        </button>
        <button
          v-if="clientImage"
          :class="['btn-source', { active: imageSource === 'client' }]"
          @click="setImageSource('client')"
        >
          Foto Cliente
        </button>
        <button class="btn-upload" @click="showUploader = true">
          <i class="fa-solid fa-camera" />
          Subir Foto
        </button>
      </div>
    </div>

    <!-- Canvas Area -->
    <div
      ref="canvasContainer"
      class="canvas-container"
      @click="handleCanvasClick"
    >
      <!-- Imagen base -->
      <img
        ref="baseImage"
        :src="currentImageUrl"
        class="base-image"
        @load="onImageLoad"
        draggable="false"
      />

      <!-- Overlay de zonas (solo si usa template) -->
      <FaultMarkerOverlay
        v-if="imageSource === 'template' && componentMap"
        :width="imageWidth"
        :height="imageHeight"
        :component-map="componentMap"
        :marked-faults="markedFaults"
        @zone-click="handleZoneClick"
      />

      <!-- Marcadores de fallas (modo libre) -->
      <div
        v-for="fault in markedFaults"
        :key="fault.id"
        class="fault-marker"
        :class="fault.markerClass"
        @click.stop="editFault(fault)"
      >
        <span class="marker-icon">✕</span>
        <span class="marker-number">{{ fault.index }}</span>
      </div>

      <!-- Cursor de nuevo marcador -->
      <div
        v-if="isPlacingMarker"
        class="placement-cursor"
        :class="cursorClass"
      >
        <span>+ Click para marcar falla</span>
      </div>
    </div>

    <!-- Panel de fallas -->
    <FaultListPanel
      :faults="markedFaults"
      :fault-catalog="faultCatalog"
      @remove="removeFault"
      @edit="editFault"
      @update-type="updateFaultType"
    />

    <!-- Resumen de cotización -->
    <QuotationSummary
      :faults="markedFaults"
      :labor-total="laborTotal"
      :parts-total="partsTotal"
      @generate-report="generateReport"
    />

    <!-- Modal de selección de falla -->
    <FaultSelectionModal
      v-if="showFaultModal"
      :component="selectedComponent"
      :position="modalPosition"
      :fault-catalog="availableFaults"
      @select="onFaultTypeSelected"
      @cancel="cancelFaultSelection"
    />

    <!-- Uploader de foto -->
    <EvidenceUploader
      v-if="showUploader"
      :repair-id="repairId"
      evidence-type="diagnostic"
      @uploaded="onPhotoUploaded"
      @close="showUploader = false"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import FaultMarkerOverlay from './FaultMarkerOverlay.vue'
import FaultListPanel from './FaultListPanel.vue'
import QuotationSummary from './QuotationSummary.vue'
import FaultSelectionModal from './FaultSelectionModal.vue'
import EvidenceUploader from './EvidenceUploader.vue'
import { useApi } from '@/composables/useApi'

const props = defineProps({
  // Instrumento (template o custom)
  instrument: { type: Object, required: true },
  // Sesión de diagnóstico existente (para edición)
  sessionId: { type: Number, default: null },
  // ID de reparación (si ya existe)
  repairId: { type: Number, default: null },
  // Imagen del cliente (si subió)
  clientImage: { type: String, default: null },
  // Modo: 'client' (público) o 'technician' (admin)
  mode: { type: String, default: 'client' }
})

const emit = defineEmits(['report-generated', 'session-saved'])

const api = useApi()

// Estado
const imageSource = ref('template')  // 'template', 'client', 'custom'
const markedFaults = ref([])
const showFaultModal = ref(false)
const showUploader = ref(false)
const selectedComponent = ref(null)
const isPlacingMarker = ref(false)
const faultCatalog = ref([])

// Imagen
const canvasContainer = ref(null)
const baseImage = ref(null)
const imageWidth = ref(0)
const imageHeight = ref(0)

// Computeds
const currentImageUrl = computed(() => {
  if (imageSource.value === 'client' && props.clientImage) {
    return props.clientImage
  }
  return props.instrument.image_url
})

const componentMap = computed(() => {
  return props.instrument.component_map || null
})

const canUseTemplate = computed(() => {
  return !!props.instrument.component_map
})

const laborTotal = computed(() => {
  return markedFaults.value.reduce((sum, f) => sum + (f.labor_cost || 0), 0)
})

const partsTotal = computed(() => {
  return Math.round(laborTotal.value * 0.3) // Estimación 30%
})

// Cargar catálogo de fallas
onMounted(async () => {
  const data = await api.get('/diagnostic/fault-catalog')
  faultCatalog.value = data

  // Si hay sesión existente, cargar fallas
  if (props.sessionId) {
    const session = await api.get(`/diagnostic/sessions/${props.sessionId}`)
    markedFaults.value = session.faults || []
  }
})

// Handlers
const handleCanvasClick = (event) => {
  if (imageSource.value === 'template') return // Usa overlay de zonas

  // Modo libre: marcar donde hizo click
  const rect = canvasContainer.value.getBoundingClientRect()
  const x = event.clientX - rect.left
  const y = event.clientY - rect.top

  // Convertir a coordenadas relativas de imagen
  const relX = (x / rect.width) * imageWidth.value
  const relY = (y / rect.height) * imageHeight.value

  selectedComponent.value = {
    id: `custom-${Date.now()}`,
    type: 'custom',
    label: 'Componente',
    x: relX,
    y: relY
  }

  showFaultModal.value = true
}

const handleZoneClick = (zone) => {
  // Click en zona de template
  if (isFaultMarked(zone.id)) {
    editFault(getFaultByComponentId(zone.id))
    return
  }

  selectedComponent.value = {
    id: zone.id,
    type: zone.type,
    label: zone.label,
    x: zone.x + zone.width / 2,
    y: zone.y + zone.height / 2
  }

  showFaultModal.value = true
}

const onFaultTypeSelected = (faultType) => {
  const faultInfo = faultCatalog.value.find(f => f.id === faultType)

  markedFaults.value.push({
    id: Date.now(),
    index: markedFaults.value.length + 1,
    component_id: selectedComponent.value.id,
    component_type: selectedComponent.value.type,
    component_label: selectedComponent.value.label,
    position_x: selectedComponent.value.x,
    position_y: selectedComponent.value.y,
    fault_id: faultType,
    fault_name: faultInfo?.name || 'Falla',
    labor_cost: faultInfo?.base_labor_cost || 0,
    notes: ''
  })

  showFaultModal.value = false
  selectedComponent.value = null

  // Autoguardar
  saveSession()
}

const removeFault = (faultId) => {
  markedFaults.value = markedFaults.value.filter(f => f.id !== faultId)
  // Renumerar
  markedFaults.value.forEach((f, i) => f.index = i + 1)
  saveSession()
}

const saveSession = async () => {
  const data = {
    template_id: props.instrument.id,
    faults: markedFaults.value,
    total_labor_cost: laborTotal.value,
    total_parts_cost: partsTotal.value
  }

  if (props.sessionId) {
    await api.put(`/diagnostic/sessions/${props.sessionId}`, data)
  } else {
    const result = await api.post('/diagnostic/sessions', data)
    emit('session-saved', result.id)
  }
}

const generateReport = async () => {
  const report = {
    instrument: props.instrument,
    faults: markedFaults.value,
    quotation: {
      labor: laborTotal.value,
      parts: partsTotal.value,
      total: laborTotal.value + partsTotal.value
    }
  }

  emit('report-generated', report)
}

// Helpers
const isFaultMarked = (componentId) => {
  return markedFaults.value.some(f => f.component_id === componentId)
}

const getFaultByComponentId = (componentId) => {
  return markedFaults.value.find(f => f.component_id === componentId)
}

const getFaultMarkerStyle = (fault) => {
  const xPercent = (fault.position_x / imageWidth.value) * 100
  const yPercent = (fault.position_y / imageHeight.value) * 100
  return {
    left: `${xPercent}%`,
    top: `${yPercent}%`
  }
}

const onImageLoad = () => {
  imageWidth.value = baseImage.value.naturalWidth
  imageHeight.value = baseImage.value.naturalHeight
}
</script>

/* Estilos movidos a la capa Sass global del proyecto */
@use "@/scss/_core.scss" as *;

.diagnostic-canvas {
  display: grid;
  grid-template-columns: 1fr 320px;
  grid-template-rows: auto 1fr auto;
  gap: $spacer-md;
  height: 100%;
  min-height: 600px;
}

.canvas-toolbar {
  grid-column: 1 / -1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: $spacer-md;
  background: $color-white;
  border-radius: $border-radius-md;
  box-shadow: $shadow-sm;
}

.instrument-name {
  font-size: $text-lg;
  font-weight: $fw-bold;
  color: $color-dark;
}

.toolbar-right {
  display: flex;
  gap: $spacer-sm;
}

.btn-source {
  padding: $spacer-sm $spacer-md;
  border: 2px solid $light-4;
  border-radius: $border-radius-md;
  background: $color-white;
  cursor: pointer;
  transition: $transition-fast;

  &.active {
    border-color: $color-primary;
    background: rgba($color-primary, 0.1);
    color: $color-primary;
  }
}

.btn-upload {
  padding: $spacer-sm $spacer-md;
  background: $color-primary;
  color: $color-white;
  border: none;
  border-radius: $border-radius-md;
  cursor: pointer;

  i {
    margin-right: $spacer-xs;
  }
}

.canvas-container {
  position: relative;
  background: $light-1;
  border-radius: $border-radius-lg;
  overflow: hidden;
  cursor: crosshair;
}

.base-image {
  width: 100%;
  height: auto;
  display: block;
  user-select: none;
}

.fault-marker {
  position: absolute;
  transform: translate(-50%, -50%);
  width: 32px;
  height: 32px;
  background: $color-danger;
  border: 3px solid $color-white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: $shadow-md;
  transition: $transition-fast;

  &:hover {
    transform: translate(-50%, -50%) scale(1.2);
  }

  .marker-icon {
    color: $color-white;
    font-weight: $fw-bold;
    font-size: $text-lg;
  }

  .marker-number {
    position: absolute;
    top: -8px;
    right: -8px;
    background: $color-dark;
    color: $color-white;
    font-size: $text-xs;
    width: 18px;
    height: 18px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

// Responsive
@include media-breakpoint-down(lg) {
  .diagnostic-canvas {
    grid-template-columns: 1fr;
  }
}
```

---

## 6. API Endpoints

### 6.1 Templates

```python
# GET /api/diagnostic/templates
# Lista todos los templates disponibles (con filtros)
{
    "templates": [
        {
            "id": 1,
            "brand": "Yamaha",
            "model": "DX7",
            "slug": "yamaha-dx7",
            "thumbnail_url": "/img/yamaha-dx7-thumb.jpg",
            "category": "Sintetizador",
            "is_verified": true,
            "component_count": {
                "keys": 61,
                "buttons": 32,
                "sliders": 1,
                "knobs": 0
            }
        },
        ...
    ],
    "total": 45,
    "page": 1,
    "per_page": 20
}

# GET /api/diagnostic/templates/{slug}
# Obtiene template completo con mapa de componentes

# POST /api/diagnostic/templates
# Crear nuevo template (solo admin)

# PUT /api/diagnostic/templates/{id}
# Actualizar template (solo admin)
```

### 6.2 Sesiones de Diagnóstico

```python
# POST /api/diagnostic/sessions
# Crear nueva sesión de diagnóstico
{
    "template_id": 1,  # o null si es custom
    "custom_brand": "Casio",
    "custom_model": "CZ-101",
    "custom_image_url": "/uploads/...",
    "client_notes": "3 teclas no suenan"
}

# GET /api/diagnostic/sessions/{id}
# Obtener sesión con todas las fallas

# PUT /api/diagnostic/sessions/{id}
# Actualizar sesión (agregar/quitar fallas)

# POST /api/diagnostic/sessions/{id}/faults
# Agregar falla a sesión
{
    "component_id": "key-24",
    "component_type": "key",
    "position_x": 450,
    "position_y": 380,
    "fault_id": 1,
    "notes": "No responde al tacto"
}

# DELETE /api/diagnostic/sessions/{id}/faults/{fault_id}
# Eliminar falla

# POST /api/diagnostic/sessions/{id}/convert
# Convertir sesión en reparación formal
```

### 6.3 Evidencia Fotográfica

```python
# POST /api/repairs/{id}/evidence
# Subir foto de evidencia
# (multipart/form-data)
{
    "file": <binary>,
    "evidence_type": "diagnostic",  # initial_client, diagnostic, progress, internal, final
    "caption": "Vista del circuito principal",
    "is_visible_to_client": true
}

# GET /api/repairs/{id}/evidence
# Listar todas las evidencias de una reparación

# PUT /api/repairs/{id}/evidence/{evidence_id}
# Actualizar metadatos (caption, visibilidad, anotaciones)

# POST /api/repairs/{id}/evidence/{evidence_id}/annotations
# Agregar anotación a foto
{
    "x": 150,
    "y": 200,
    "type": "marker",  # marker, arrow, circle, text
    "label": "Condensador inflado",
    "color": "#ff0000"
}
```

### 6.4 Subida de Instrumentos Nuevos

```python
# POST /api/diagnostic/instruments/upload
# Cliente sube foto de instrumento no catalogado
{
    "file": <binary>,
    "brand_name": "Ensoniq",
    "model_name": "ESQ-1",
    "year_approximate": 1986
}

# Response
{
    "upload_id": "uuid...",
    "validation_status": "pending",  # o "approved" si pasa validaciones automáticas
    "validation_errors": [],  # ["Imagen muy pequeña", "Debe ser horizontal"]
    "temporary_image_url": "/tmp/...",
    "diagnostic_session_id": 123
}

# GET /api/diagnostic/instruments/uploads/{uuid}
# Estado de validación de subida

# PUT /api/admin/instruments/uploads/{uuid}/validate
# Admin valida/rechaza subida
{
    "status": "approved",  # approved, rejected, needs_retake
    "notes": "Aprobado, crear template",
    "convert_to_template": true
}
```

---

## 7. Validación de Imágenes (Frontend + Backend)

### 7.1 Validador Frontend

```javascript
// src/utils/imageValidator.js

export const IMAGE_RULES = {
  minWidth: 1200,
  minHeight: 400,
  maxWidth: 4000,
  maxHeight: 3000,
  maxSizeBytes: 10 * 1024 * 1024, // 10MB
  allowedTypes: ['image/jpeg', 'image/png', 'image/webp'],
  aspectRatioMin: 2.0,  // Debe ser horizontal
  aspectRatioMax: 5.0
}

export async function validateInstrumentImage(file) {
  const errors = []

  // Validar tipo
  if (!IMAGE_RULES.allowedTypes.includes(file.type)) {
    errors.push('Formato no válido. Use JPG, PNG o WebP.')
  }

  // Validar tamaño
  if (file.size > IMAGE_RULES.maxSizeBytes) {
    errors.push(`El archivo excede ${IMAGE_RULES.maxSizeBytes / 1024 / 1024}MB`)
  }

  // Validar dimensiones
  const dimensions = await getImageDimensions(file)

  if (dimensions.width < IMAGE_RULES.minWidth) {
    errors.push(`Ancho mínimo: ${IMAGE_RULES.minWidth}px (actual: ${dimensions.width}px)`)
  }

  if (dimensions.height < IMAGE_RULES.minHeight) {
    errors.push(`Alto mínimo: ${IMAGE_RULES.minHeight}px (actual: ${dimensions.height}px)`)
  }

  const aspectRatio = dimensions.width / dimensions.height
  if (aspectRatio < IMAGE_RULES.aspectRatioMin) {
    errors.push('La imagen debe ser horizontal (vista frontal del instrumento)')
  }

  return {
    valid: errors.length === 0,
    errors,
    dimensions
  }
}

function getImageDimensions(file) {
  return new Promise((resolve) => {
    const img = new Image()
    img.onload = () => {
      resolve({ width: img.width, height: img.height })
      URL.revokeObjectURL(img.src)
    }
    img.src = URL.createObjectURL(file)
  })
}
```

### 7.2 Componente Uploader

```vue
<!-- src/vue/components/diagnostic/InstrumentUploader.vue -->
<template>
  <div class="instrument-uploader">
    <h3>Subir foto de su instrumento</h3>

    <!-- Requisitos -->
    <div class="upload-requirements">
      <h4>Requisitos de la foto:</h4>
      <ul>
        <li>
          <i :class="['fa-solid', reqMet.horizontal ? 'fa-check' : 'fa-xmark']" />
          Vista frontal completa (horizontal)
        </li>
        <li>
          <i :class="['fa-solid', reqMet.size ? 'fa-check' : 'fa-xmark']" />
          Mínimo 1200 x 400 píxeles
        </li>
        <li>
          <i :class="['fa-solid', reqMet.format ? 'fa-check' : 'fa-xmark']" />
          Formato JPG, PNG o WebP (máx 10MB)
        </li>
        <li>
          <i :class="['fa-solid', reqMet.lighting ? 'fa-check' : 'fa-xmark']" />
          Buena iluminación, sin reflejos
        </li>
      </ul>
    </div>

    <!-- Ejemplo visual -->
    <div class="upload-example">
      <div class="example-good">
        <img src="/img/upload-example-good.jpg" alt="Ejemplo correcto" />
        <span class="label good">✓ Correcto</span>
      </div>
      <div class="example-bad">
        <img src="/img/upload-example-bad.jpg" alt="Ejemplo incorrecto" />
        <span class="label bad">✗ Incorrecto</span>
      </div>
    </div>

    <!-- Información del instrumento -->
    <div class="instrument-info">
      <div class="form-group">
        <label>Marca *</label>
        <input
          v-model="brandName"
          type="text"
          placeholder="Ej: Yamaha, Roland, Korg..."
          required
        />
      </div>
      <div class="form-group">
        <label>Modelo *</label>
        <input
          v-model="modelName"
          type="text"
          placeholder="Ej: DX7, Juno-106, MS-20..."
          required
        />
      </div>
      <div class="form-group">
        <label>Año aproximado</label>
        <input
          v-model.number="yearApprox"
          type="number"
          min="1960"
          max="2030"
          placeholder="1985"
        />
      </div>
    </div>

    <!-- Drop zone -->
    <div
      class="dropzone"
      :class="{ 'dragover': isDragging, 'has-file': previewUrl }"
      @dragover.prevent="isDragging = true"
      @dragleave="isDragging = false"
      @drop.prevent="handleDrop"
      @click="triggerFileInput"
    >
      <input
        ref="fileInput"
        type="file"
        accept="image/jpeg,image/png,image/webp"
        @change="handleFileSelect"
        hidden
      />

      <div v-if="!previewUrl" class="dropzone-content">
        <i class="fa-solid fa-cloud-arrow-up" />
        <p>Arrastre la imagen aquí o haga clic para seleccionar</p>
      </div>

      <div v-else class="preview-content">
        <img :src="previewUrl" alt="Preview" />
        <button class="btn-remove" @click.stop="clearFile">
          <i class="fa-solid fa-trash" />
        </button>
      </div>
    </div>

    <!-- Errores de validación -->
    <div v-if="validationErrors.length" class="validation-errors">
      <p v-for="error in validationErrors" :key="error">
        <i class="fa-solid fa-triangle-exclamation" />
        {{ error }}
      </p>
    </div>

    <!-- Botón subir -->
    <button
      class="btn-submit"
      :disabled="!canSubmit || isUploading"
      @click="submitUpload"
    >
      <span v-if="isUploading">
        <i class="fa-solid fa-spinner fa-spin" />
        Subiendo...
      </span>
      <span v-else>
        Continuar con esta foto →
      </span>
    </button>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { validateInstrumentImage } from '@/utils/imageValidator'
import { useApi } from '@/composables/useApi'

const emit = defineEmits(['uploaded', 'cancel'])

const api = useApi()

// Form data
const brandName = ref('')
const modelName = ref('')
const yearApprox = ref(null)

// File handling
const fileInput = ref(null)
const selectedFile = ref(null)
const previewUrl = ref(null)
const isDragging = ref(false)
const isUploading = ref(false)
const validationErrors = ref([])

// Requirements met
const reqMet = ref({
  horizontal: false,
  size: false,
  format: false,
  lighting: true // Asumimos por defecto
})

const canSubmit = computed(() => {
  return (
    selectedFile.value &&
    validationErrors.value.length === 0 &&
    brandName.value.trim() &&
    modelName.value.trim()
  )
})

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = async (event) => {
  const file = event.target.files[0]
  if (file) await processFile(file)
}

const handleDrop = async (event) => {
  isDragging.value = false
  const file = event.dataTransfer.files[0]
  if (file) await processFile(file)
}

const processFile = async (file) => {
  // Validar
  const validation = await validateInstrumentImage(file)

  validationErrors.value = validation.errors
  reqMet.value.format = file.type.startsWith('image/')
  reqMet.value.size = validation.dimensions.width >= 1200
  reqMet.value.horizontal = validation.dimensions.width > validation.dimensions.height * 2

  if (validation.valid) {
    selectedFile.value = file
    previewUrl.value = URL.createObjectURL(file)
  }
}

const clearFile = () => {
  selectedFile.value = null
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
    previewUrl.value = null
  }
  validationErrors.value = []
}

const submitUpload = async () => {
  if (!canSubmit.value) return

  isUploading.value = true

  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('brand_name', brandName.value)
    formData.append('model_name', modelName.value)
    if (yearApprox.value) {
      formData.append('year_approximate', yearApprox.value)
    }

    const result = await api.upload('/diagnostic/instruments/upload', formData)

    emit('uploaded', {
      uploadId: result.upload_id,
      imageUrl: result.temporary_image_url,
      sessionId: result.diagnostic_session_id
    })
  } catch (error) {
    validationErrors.value = [error.message || 'Error al subir la imagen']
  } finally {
    isUploading.value = false
  }
}
</script>
```

---

## 8. Timeline de Evidencia (Vista Cliente)

```vue
<!-- src/vue/components/repair/RepairEvidenceTimeline.vue -->
<template>
  <div class="evidence-timeline">
    <h3>Progreso de su reparación</h3>

    <div class="timeline">
      <div
        v-for="(evidence, index) in visibleEvidence"
        :key="evidence.id"
        class="timeline-item"
        :class="evidence.evidence_type"
      >
        <div class="timeline-marker">
          <i :class="getIcon(evidence.evidence_type)" />
        </div>

        <div class="timeline-content">
          <div class="timeline-date">
            {{ formatDate(evidence.uploaded_at) }}
          </div>

          <div class="timeline-image" @click="openLightbox(evidence)">
            <img :src="evidence.thumbnail_url || evidence.image_url" :alt="evidence.caption" />
            <div class="image-overlay">
              <i class="fa-solid fa-search-plus" />
            </div>
          </div>

          <div class="timeline-caption">
            {{ evidence.caption }}
          </div>

          <!-- Anotaciones visibles -->
          <div v-if="evidence.annotations?.length" class="timeline-annotations">
            <span v-for="ann in evidence.annotations" :key="ann.id">
              {{ ann.label }}
            </span>
          </div>
        </div>

        <div class="timeline-line" v-if="index < visibleEvidence.length - 1" />
      </div>
    </div>

    <!-- Lightbox -->
    <div v-if="lightboxImage" class="lightbox" @click="closeLightbox">
      <img :src="lightboxImage.image_url" :alt="lightboxImage.caption" />
      <button class="close-btn">&times;</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  evidence: { type: Array, default: () => [] }
})

const lightboxImage = ref(null)

// Solo mostrar evidencias visibles para cliente
const visibleEvidence = computed(() => {
  return props.evidence
    .filter(e => e.is_visible_to_client)
    .sort((a, b) => new Date(a.uploaded_at) - new Date(b.uploaded_at))
})

const getIcon = (type) => {
  const icons = {
    'initial_client': 'fa-solid fa-camera',
    'initial_technician': 'fa-solid fa-clipboard-check',
    'diagnostic': 'fa-solid fa-stethoscope',
    'internal': 'fa-solid fa-microchip',
    'progress': 'fa-solid fa-wrench',
    'final': 'fa-solid fa-check-circle'
  }
  return icons[type] || 'fa-solid fa-image'
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('es-CL', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const openLightbox = (evidence) => {
  lightboxImage.value = evidence
}

const closeLightbox = () => {
  lightboxImage.value = null
}
</script>
```

---

## 9. Resumen de Implementación

### Fase 1: MVP (3-4 semanas)
- [ ] Modelos de BD para templates y diagnósticos
- [ ] 5 templates manuales de instrumentos populares
- [ ] Componente DiagnosticCanvas básico
- [ ] CRUD de sesiones de diagnóstico
- [ ] Cálculo de cotización

### Fase 2: Subida de Instrumentos (2 semanas)
- [ ] Uploader con validación
- [ ] Sistema de validación admin
- [ ] Conversión a template

### Fase 3: Evidencia Fotográfica (2 semanas)
- [ ] Subida de fotos por técnico
- [ ] Anotaciones sobre fotos
- [ ] Timeline para cliente

### Fase 4: Mejoras (Ongoing)
- [ ] Más templates
- [ ] Detección automática con OpenCV
- [ ] App móvil para técnico

---

## 10. Notas Técnicas

### Storage de Imágenes
- Usar MinIO/S3 compatible para almacenar imágenes
- Generar thumbnails automáticamente (300x200)
- Comprimir originales a máx 2000px de ancho
- Retener originales 90 días, luego solo thumbnails

### Performance
- Lazy loading de imágenes en grids
- SVG para overlays (no canvas bitmap)
- Debounce en guardado automático de sesiones

### Seguridad
- Validar tipos MIME en backend
- Escanear malware en uploads
- Limitar uploads por IP/usuario
- Firmar URLs de acceso a imágenes
