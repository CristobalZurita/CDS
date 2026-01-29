# Sistema de Diagnóstico Visual Interactivo
## Cirujano de Sintetizadores - Diseño Técnico

---

## 1. Visión General

Sistema que permite al técnico o usuario "pinchar" componentes defectuosos
sobre una imagen del instrumento, generando automáticamente un diagnóstico
y cotización estimada.

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLUJO DEL SISTEMA                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Seleccionar    2. Cargar        3. Pinchar      4. Generar  │
│     Instrumento       Template         Fallas          Reporte  │
│                                                                 │
│  ┌─────────┐      ┌─────────┐      ┌─────────┐      ┌─────────┐ │
│  │ YAMAHA  │  →   │  Foto   │  →   │  Click  │  →   │ $$$     │ │
│  │  DX7    │      │ + Mapa  │      │  Zonas  │      │ Report  │ │
│  └─────────┘      └─────────┘      └─────────┘      └─────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Arquitectura de Datos

### 2.1 Modelo de Instrumento (Template)

```javascript
// Ejemplo: Yamaha DX7
{
  "id": "yamaha-dx7",
  "brand": "Yamaha",
  "model": "DX7",
  "category": "synthesizer",
  "year_range": "1983-1986",
  "image": "/instruments/yamaha-dx7-front.jpg",
  "image_dimensions": { "width": 1920, "height": 600 },

  // Definición de componentes
  "components": {
    "keyboard": {
      "type": "keys",
      "count": 61,
      "octaves": 5,
      "key_type": "weighted",
      // Zona general del teclado
      "bounding_box": { "x": 50, "y": 350, "width": 1820, "height": 200 },
      // Generación automática de zonas por tecla
      "auto_generate": true,
      "key_width": 28,
      "black_key_pattern": [1, 3, 6, 8, 10] // posiciones de teclas negras en octava
    },

    "buttons": [
      {
        "id": "btn-algorithm",
        "label": "Algorithm Select",
        "zone": { "x": 120, "y": 80, "width": 40, "height": 40 },
        "possible_faults": ["no_response", "intermittent", "stuck"]
      },
      {
        "id": "btn-operator",
        "label": "Operator Select",
        "zone": { "x": 180, "y": 80, "width": 40, "height": 40 },
        "possible_faults": ["no_response", "intermittent", "stuck"]
      }
      // ... más botones
    ],

    "sliders": [
      {
        "id": "slider-data",
        "label": "Data Entry Slider",
        "zone": { "x": 1600, "y": 60, "width": 30, "height": 120 },
        "possible_faults": ["scratchy", "dead_spot", "no_response", "jumping"]
      }
    ],

    "potentiometers": [
      {
        "id": "pot-volume",
        "label": "Volume",
        "zone": { "x": 1750, "y": 100, "width": 50, "height": 50 },
        "possible_faults": ["scratchy", "dead", "intermittent"]
      }
    ],

    "connectors": [
      {
        "id": "out-left",
        "label": "Output L",
        "zone": { "x": 1850, "y": 280, "width": 30, "height": 30 },
        "possible_faults": ["no_signal", "noise", "intermittent", "physical_damage"]
      },
      {
        "id": "midi-in",
        "label": "MIDI In",
        "zone": { "x": 1800, "y": 280, "width": 25, "height": 25 },
        "possible_faults": ["no_data", "intermittent"]
      }
    ],

    "display": {
      "id": "lcd-main",
      "label": "LCD Display",
      "zone": { "x": 800, "y": 50, "width": 200, "height": 80 },
      "possible_faults": ["dead_pixels", "no_backlight", "faded", "dead"]
    }
  }
}
```

### 2.2 Catálogo de Fallas y Costos

```javascript
{
  "fault_catalog": {
    // Fallas de teclas
    "key_no_sound": {
      "label": "Tecla sin sonido",
      "description": "La tecla no produce ningún sonido al presionarla",
      "causes": ["Contacto de goma sucio", "Contacto dañado", "Problema en bus"],
      "repair_time_minutes": 15,
      "base_cost": 5000,
      "parts_required": ["rubber_contact"]
    },
    "key_stuck": {
      "label": "Tecla atascada",
      "description": "La tecla no regresa a su posición",
      "causes": ["Muelle roto", "Suciedad", "Deformación"],
      "repair_time_minutes": 20,
      "base_cost": 8000,
      "parts_required": ["spring", "lubricant"]
    },
    "key_double_trigger": {
      "label": "Tecla dispara doble",
      "description": "Una pulsación genera dos notas",
      "causes": ["Contacto sucio", "Rebote mecánico"],
      "repair_time_minutes": 10,
      "base_cost": 4000
    },

    // Fallas de potenciómetros
    "pot_scratchy": {
      "label": "Potenciómetro con ruido",
      "description": "Genera ruido al girar",
      "causes": ["Suciedad interna", "Desgaste de pista"],
      "repair_time_minutes": 25,
      "base_cost": 12000,
      "parts_required": ["pot_cleaner", "replacement_pot"]
    },
    "pot_dead": {
      "label": "Potenciómetro muerto",
      "description": "No responde en ninguna posición",
      "repair_time_minutes": 30,
      "base_cost": 15000,
      "parts_required": ["replacement_pot"]
    },

    // Fallas de sliders
    "slider_scratchy": {
      "label": "Slider con ruido",
      "repair_time_minutes": 20,
      "base_cost": 10000
    },
    "slider_dead_spot": {
      "label": "Slider con zona muerta",
      "repair_time_minutes": 25,
      "base_cost": 12000
    },

    // Fallas de botones
    "button_no_response": {
      "label": "Botón sin respuesta",
      "repair_time_minutes": 15,
      "base_cost": 6000
    },
    "button_intermittent": {
      "label": "Botón intermitente",
      "repair_time_minutes": 20,
      "base_cost": 8000
    },

    // Fallas de conectores
    "connector_no_signal": {
      "label": "Salida sin señal",
      "repair_time_minutes": 30,
      "base_cost": 15000,
      "parts_required": ["jack_connector"]
    },
    "connector_noise": {
      "label": "Salida con ruido",
      "repair_time_minutes": 25,
      "base_cost": 12000
    },

    // Fallas de display
    "display_dead": {
      "label": "Display muerto",
      "repair_time_minutes": 60,
      "base_cost": 45000,
      "parts_required": ["lcd_display"]
    },
    "display_faded": {
      "label": "Display desvanecido",
      "repair_time_minutes": 45,
      "base_cost": 35000
    }
  }
}
```

---

## 3. Componente Vue - Editor Visual

### 3.1 Componente Principal

```vue
<!-- src/vue/components/diagnostic/InstrumentDiagnosticEditor.vue -->
<template>
  <div class="diagnostic-editor">
    <!-- Selector de instrumento -->
    <div class="instrument-selector">
      <label>Seleccionar Instrumento:</label>
      <select v-model="selectedInstrumentId" @change="loadInstrument">
        <option value="">-- Elegir modelo --</option>
        <option v-for="inst in instruments" :key="inst.id" :value="inst.id">
          {{ inst.brand }} {{ inst.model }}
        </option>
      </select>
    </div>

    <!-- Canvas interactivo -->
    <div class="canvas-container" v-if="currentInstrument">
      <div
        class="instrument-image-wrapper"
        :style="{ width: canvasWidth + 'px', height: canvasHeight + 'px' }"
      >
        <!-- Imagen base del instrumento -->
        <img
          :src="currentInstrument.image"
          class="instrument-image"
          @load="onImageLoad"
        />

        <!-- Overlay SVG para zonas clickeables -->
        <svg
          class="zones-overlay"
          :viewBox="`0 0 ${imageWidth} ${imageHeight}`"
          @click="handleClick"
        >
          <!-- Zonas de teclas -->
          <g class="keyboard-zones">
            <rect
              v-for="key in keyboardZones"
              :key="key.id"
              :x="key.x"
              :y="key.y"
              :width="key.width"
              :height="key.height"
              :class="['zone', 'zone-key', { 'zone-marked': isMarked(key.id) }]"
              :data-id="key.id"
              :data-type="'key'"
            />
          </g>

          <!-- Zonas de botones -->
          <g class="button-zones">
            <rect
              v-for="btn in buttonZones"
              :key="btn.id"
              :x="btn.zone.x"
              :y="btn.zone.y"
              :width="btn.zone.width"
              :height="btn.zone.height"
              :class="['zone', 'zone-button', { 'zone-marked': isMarked(btn.id) }]"
              :data-id="btn.id"
              :data-type="'button'"
            />
          </g>

          <!-- Zonas de sliders -->
          <g class="slider-zones">
            <rect
              v-for="slider in sliderZones"
              :key="slider.id"
              :x="slider.zone.x"
              :y="slider.zone.y"
              :width="slider.zone.width"
              :height="slider.zone.height"
              :class="['zone', 'zone-slider', { 'zone-marked': isMarked(slider.id) }]"
              :data-id="slider.id"
              :data-type="'slider'"
            />
          </g>

          <!-- Zonas de potenciómetros -->
          <g class="pot-zones">
            <circle
              v-for="pot in potZones"
              :key="pot.id"
              :cx="pot.zone.x + pot.zone.width/2"
              :cy="pot.zone.y + pot.zone.height/2"
              :r="pot.zone.width/2"
              :class="['zone', 'zone-pot', { 'zone-marked': isMarked(pot.id) }]"
              :data-id="pot.id"
              :data-type="'pot'"
            />
          </g>

          <!-- Marcadores de fallas -->
          <g class="fault-markers">
            <g v-for="fault in markedFaults" :key="fault.id">
              <circle
                :cx="fault.x"
                :cy="fault.y"
                r="12"
                class="fault-marker"
              />
              <text
                :x="fault.x"
                :y="fault.y + 4"
                class="fault-marker-text"
              >✕</text>
            </g>
          </g>
        </svg>
      </div>
    </div>

    <!-- Panel lateral: Fallas marcadas -->
    <div class="faults-panel" v-if="markedFaults.length > 0">
      <h3>Fallas Detectadas ({{ markedFaults.length }})</h3>

      <div class="fault-list">
        <div
          v-for="fault in markedFaults"
          :key="fault.id"
          class="fault-item"
        >
          <div class="fault-header">
            <span class="fault-component">{{ fault.componentLabel }}</span>
            <button @click="removeFault(fault.id)" class="btn-remove">×</button>
          </div>

          <select v-model="fault.faultType" class="fault-type-select">
            <option value="">Seleccionar tipo de falla</option>
            <option
              v-for="ft in getAvailableFaults(fault.componentType)"
              :key="ft.id"
              :value="ft.id"
            >
              {{ ft.label }} - ${{ ft.base_cost.toLocaleString() }}
            </option>
          </select>

          <textarea
            v-model="fault.notes"
            placeholder="Notas adicionales..."
            class="fault-notes"
          />
        </div>
      </div>

      <!-- Resumen de cotización -->
      <div class="quote-summary">
        <h4>Cotización Estimada</h4>
        <div class="quote-line">
          <span>Mano de obra:</span>
          <span>${{ laborCost.toLocaleString() }}</span>
        </div>
        <div class="quote-line">
          <span>Repuestos estimados:</span>
          <span>${{ partsCost.toLocaleString() }}</span>
        </div>
        <div class="quote-total">
          <span>TOTAL:</span>
          <span>${{ totalCost.toLocaleString() }} CLP</span>
        </div>

        <button @click="generateReport" class="btn-generate">
          Generar Reporte de Diagnóstico
        </button>
      </div>
    </div>

    <!-- Modal de selección de falla -->
    <FaultSelectionModal
      v-if="showFaultModal"
      :component="selectedComponent"
      :available-faults="availableFaultsForComponent"
      @select="onFaultSelected"
      @close="showFaultModal = false"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import FaultSelectionModal from './FaultSelectionModal.vue'

// Estado
const selectedInstrumentId = ref('')
const currentInstrument = ref(null)
const markedFaults = ref([])
const showFaultModal = ref(false)
const selectedComponent = ref(null)

// Cargar instrumento desde API o JSON local
const loadInstrument = async () => {
  if (!selectedInstrumentId.value) {
    currentInstrument.value = null
    return
  }

  // TODO: Cargar desde API
  const response = await fetch(`/api/instruments/${selectedInstrumentId.value}`)
  currentInstrument.value = await response.json()
  markedFaults.value = []
}

// Generar zonas de teclado automáticamente
const keyboardZones = computed(() => {
  if (!currentInstrument.value?.components?.keyboard) return []

  const kb = currentInstrument.value.components.keyboard
  const keys = []
  const keyWidth = kb.key_width || 28
  const blackKeyPattern = kb.black_key_pattern || [1, 3, 6, 8, 10]

  let xPos = kb.bounding_box.x

  for (let i = 0; i < kb.count; i++) {
    const noteInOctave = i % 12
    const isBlackKey = blackKeyPattern.includes(noteInOctave)

    keys.push({
      id: `key-${i}`,
      x: xPos,
      y: isBlackKey ? kb.bounding_box.y : kb.bounding_box.y + 60,
      width: keyWidth - 2,
      height: isBlackKey ? 100 : 140,
      isBlack: isBlackKey,
      noteNumber: i
    })

    // Solo avanzar x para teclas blancas
    if (!isBlackKey) {
      xPos += keyWidth
    }
  }

  return keys
})

// Click handler
const handleClick = (event) => {
  const target = event.target
  if (!target.dataset.id) return

  const componentId = target.dataset.id
  const componentType = target.dataset.type

  if (isMarked(componentId)) {
    // Ya está marcado, mostrar modal para editar
    return
  }

  // Encontrar info del componente
  const component = findComponent(componentId, componentType)
  selectedComponent.value = {
    id: componentId,
    type: componentType,
    label: component?.label || componentId,
    x: parseFloat(target.getAttribute('cx') || target.getAttribute('x')),
    y: parseFloat(target.getAttribute('cy') || target.getAttribute('y'))
  }

  showFaultModal.value = true
}

// Verificar si componente está marcado
const isMarked = (componentId) => {
  return markedFaults.value.some(f => f.componentId === componentId)
}

// Agregar falla
const onFaultSelected = (faultType) => {
  markedFaults.value.push({
    id: Date.now(),
    componentId: selectedComponent.value.id,
    componentType: selectedComponent.value.type,
    componentLabel: selectedComponent.value.label,
    faultType: faultType,
    x: selectedComponent.value.x,
    y: selectedComponent.value.y,
    notes: ''
  })
  showFaultModal.value = false
}

// Calcular costos
const laborCost = computed(() => {
  return markedFaults.value.reduce((sum, fault) => {
    const faultInfo = getFaultInfo(fault.faultType)
    return sum + (faultInfo?.base_cost || 0)
  }, 0)
})

const partsCost = computed(() => {
  // Estimación de repuestos (30% del costo de mano de obra)
  return Math.round(laborCost.value * 0.3)
})

const totalCost = computed(() => laborCost.value + partsCost.value)

// Generar reporte
const generateReport = () => {
  const report = {
    instrument: currentInstrument.value,
    faults: markedFaults.value,
    quotation: {
      labor: laborCost.value,
      parts: partsCost.value,
      total: totalCost.value
    },
    generatedAt: new Date().toISOString()
  }

  // Emitir para guardar o mostrar
  emit('report-generated', report)
}
</script>
```

---

## 4. Backend Python (Opcional - Para Detección Automática)

### 4.1 Detector de Componentes con OpenCV

```python
# backend/services/instrument_detector.py

import cv2
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class DetectedComponent:
    id: str
    type: str  # 'key', 'button', 'knob', 'slider', 'connector'
    x: int
    y: int
    width: int
    height: int
    confidence: float

class InstrumentComponentDetector:
    """
    Detecta componentes en una imagen de instrumento musical.
    Usa técnicas de visión por computadora (no ML) para detectar:
    - Teclas (por patrón blanco/negro repetitivo)
    - Botones (círculos pequeños)
    - Knobs/Potenciómetros (círculos medianos)
    - Sliders (rectángulos verticales)
    """

    def __init__(self):
        self.templates = {}  # Templates precargados por tipo

    def detect_keyboard(self, image: np.ndarray) -> List[DetectedComponent]:
        """
        Detecta teclas de piano/sintetizador.
        Busca el patrón característico de teclas blancas y negras.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Detectar bordes verticales (separación entre teclas)
        edges = cv2.Canny(gray, 50, 150)

        # Buscar líneas verticales
        lines = cv2.HoughLinesP(
            edges, 1, np.pi/180,
            threshold=50,
            minLineLength=100,
            maxLineGap=10
        )

        # Encontrar región del teclado (zona con muchas líneas verticales paralelas)
        keyboard_region = self._find_keyboard_region(lines, image.shape)

        if keyboard_region is None:
            return []

        # Dentro de la región, detectar teclas individuales
        keys = self._segment_keys(gray, keyboard_region)

        return keys

    def detect_circular_components(
        self,
        image: np.ndarray,
        min_radius: int = 10,
        max_radius: int = 40
    ) -> List[DetectedComponent]:
        """
        Detecta botones y potenciómetros (componentes circulares).
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)

        circles = cv2.HoughCircles(
            gray,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=20,
            param1=50,
            param2=30,
            minRadius=min_radius,
            maxRadius=max_radius
        )

        components = []
        if circles is not None:
            circles = np.uint16(np.around(circles))
            for i, (x, y, r) in enumerate(circles[0, :]):
                comp_type = 'knob' if r > 20 else 'button'
                components.append(DetectedComponent(
                    id=f"{comp_type}-{i}",
                    type=comp_type,
                    x=int(x - r),
                    y=int(y - r),
                    width=int(r * 2),
                    height=int(r * 2),
                    confidence=0.8
                ))

        return components

    def detect_sliders(self, image: np.ndarray) -> List[DetectedComponent]:
        """
        Detecta sliders/faders (rectángulos verticales alargados).
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Threshold adaptativo
        thresh = cv2.adaptiveThreshold(
            gray, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 2
        )

        # Encontrar contornos
        contours, _ = cv2.findContours(
            thresh,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        sliders = []
        for i, contour in enumerate(contours):
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = h / w if w > 0 else 0

            # Sliders son típicamente 3-8x más altos que anchos
            if 3 < aspect_ratio < 8 and 50 < h < 200 and 10 < w < 50:
                sliders.append(DetectedComponent(
                    id=f"slider-{i}",
                    type='slider',
                    x=x, y=y, width=w, height=h,
                    confidence=0.7
                ))

        return sliders

    def analyze_instrument(self, image_path: str) -> dict:
        """
        Análisis completo de una imagen de instrumento.
        Retorna mapa de componentes detectados.
        """
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"No se pudo cargar imagen: {image_path}")

        results = {
            'image_dimensions': {
                'width': image.shape[1],
                'height': image.shape[0]
            },
            'components': {
                'keys': self.detect_keyboard(image),
                'knobs': [],
                'buttons': [],
                'sliders': self.detect_sliders(image)
            }
        }

        # Separar circulares en knobs y buttons
        circular = self.detect_circular_components(image)
        for comp in circular:
            if comp.type == 'knob':
                results['components']['knobs'].append(comp)
            else:
                results['components']['buttons'].append(comp)

        return results

    def _find_keyboard_region(self, lines, image_shape) -> Tuple[int, int, int, int]:
        """Encuentra la región rectangular que contiene el teclado."""
        if lines is None or len(lines) < 10:
            return None

        # Buscar zona con mayor densidad de líneas verticales
        # ... (implementación detallada)
        return None  # Placeholder

    def _segment_keys(self, gray, region) -> List[DetectedComponent]:
        """Segmenta teclas individuales dentro de la región del teclado."""
        # ... (implementación detallada)
        return []


# API Endpoint
from fastapi import APIRouter, UploadFile, File
import tempfile

router = APIRouter()
detector = InstrumentComponentDetector()

@router.post("/api/detect-components")
async def detect_components(image: UploadFile = File(...)):
    """
    Sube una imagen de instrumento y detecta componentes automáticamente.
    """
    # Guardar temporalmente
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
        content = await image.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        results = detector.analyze_instrument(tmp_path)
        return {
            'success': True,
            'data': results
        }
    finally:
        import os
        os.unlink(tmp_path)
```

---

## 5. Base de Datos de Templates

### 5.1 Estructura de Carpetas

```
/data/instruments/
├── templates/
│   ├── yamaha-dx7/
│   │   ├── front.jpg           # Foto frontal alta resolución
│   │   ├── back.jpg            # Foto trasera (conectores)
│   │   ├── components.json     # Mapa de componentes
│   │   └── thumbnail.jpg       # Miniatura para selector
│   │
│   ├── roland-juno-106/
│   │   ├── front.jpg
│   │   ├── components.json
│   │   └── thumbnail.jpg
│   │
│   ├── korg-ms-20/
│   │   └── ...
│   │
│   └── moog-minimoog/
│       └── ...
│
├── fault-catalog.json          # Catálogo maestro de fallas
└── parts-catalog.json          # Catálogo de repuestos y precios
```

### 5.2 Script para Crear Template

```python
# tools/create_instrument_template.py

"""
Herramienta CLI para crear templates de instrumentos.

Uso:
  python create_instrument_template.py --brand "Yamaha" --model "DX7"

Esto abre un editor visual donde puedes:
1. Cargar la foto del instrumento
2. Dibujar zonas para cada componente
3. Asignar tipo y etiqueta a cada zona
4. Guardar como JSON
"""

import cv2
import json
import argparse
from pathlib import Path

class TemplateCreator:
    def __init__(self, image_path: str):
        self.image = cv2.imread(image_path)
        self.components = []
        self.current_rect = None
        self.drawing = False

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.start_point = (x, y)
        elif event == cv2.EVENT_MOUSEMOVE and self.drawing:
            self.current_rect = (self.start_point, (x, y))
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            if self.current_rect:
                self.add_component(self.current_rect)
                self.current_rect = None

    def add_component(self, rect):
        (x1, y1), (x2, y2) = rect
        comp_type = input("Tipo (key/button/knob/slider/connector): ")
        label = input("Etiqueta: ")

        self.components.append({
            'id': f"{comp_type}-{len(self.components)}",
            'type': comp_type,
            'label': label,
            'zone': {
                'x': min(x1, x2),
                'y': min(y1, y2),
                'width': abs(x2 - x1),
                'height': abs(y2 - y1)
            }
        })
        print(f"Componente agregado: {label}")

    def run(self):
        cv2.namedWindow('Template Creator')
        cv2.setMouseCallback('Template Creator', self.mouse_callback)

        while True:
            display = self.image.copy()

            # Dibujar componentes existentes
            for comp in self.components:
                z = comp['zone']
                color = {
                    'key': (255, 255, 255),
                    'button': (0, 255, 0),
                    'knob': (255, 0, 0),
                    'slider': (0, 255, 255),
                    'connector': (255, 0, 255)
                }.get(comp['type'], (128, 128, 128))

                cv2.rectangle(
                    display,
                    (z['x'], z['y']),
                    (z['x'] + z['width'], z['y'] + z['height']),
                    color, 2
                )

            # Dibujar rectángulo actual
            if self.current_rect:
                cv2.rectangle(display, *self.current_rect, (0, 0, 255), 2)

            cv2.imshow('Template Creator', display)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('s'):  # Guardar
                self.save()
            elif key == ord('q'):  # Salir
                break

        cv2.destroyAllWindows()

    def save(self, output_path: str = 'components.json'):
        with open(output_path, 'w') as f:
            json.dump({'components': self.components}, f, indent=2)
        print(f"Template guardado en {output_path}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--image', required=True, help='Ruta a imagen del instrumento')
    args = parser.parse_args()

    creator = TemplateCreator(args.image)
    creator.run()
```

---

## 6. Flujo de Implementación Recomendado

### Fase 1: MVP (2-3 semanas)
1. ✅ Crear 3-5 templates de instrumentos populares manualmente
2. ✅ Implementar componente Vue de visualización
3. ✅ Sistema de click → agregar falla
4. ✅ Cálculo básico de cotización

### Fase 2: Mejoras (2-4 semanas)
1. 🔄 Backend para guardar diagnósticos
2. 🔄 Generación de PDF de reporte
3. 🔄 Más templates de instrumentos
4. 🔄 Historial de diagnósticos por cliente

### Fase 3: Automatización (1-2 meses)
1. ⏳ Detector Python con OpenCV
2. ⏳ Generación semi-automática de templates
3. ⏳ Sugerencias de fallas basadas en síntomas

### Fase 4: IA Real (3-6 meses - Opcional)
1. 🔮 Entrenamiento de modelo YOLO para instrumentos
2. 🔮 Detección automática de daños visibles
3. 🔮 Clasificación de estado de componentes

---

## 7. Estimación de Trabajo

| Tarea | Tiempo | Prioridad |
|-------|--------|-----------|
| Templates JSON manuales (10 instrumentos) | 1 semana | ALTA |
| Componente Vue Editor | 1-2 semanas | ALTA |
| Backend diagnósticos | 1 semana | ALTA |
| Detector OpenCV básico | 2 semanas | MEDIA |
| Tool crear templates | 3 días | MEDIA |
| Modelo YOLO entrenado | 2-3 meses | BAJA |

---

## 8. Ejemplo de Template: Yamaha DX7

```json
{
  "id": "yamaha-dx7",
  "brand": "Yamaha",
  "model": "DX7",
  "category": "synthesizer",
  "year": 1983,
  "image": "/instruments/yamaha-dx7.jpg",
  "image_dimensions": { "width": 2400, "height": 800 },

  "specs": {
    "keys": 61,
    "octaves": 5,
    "polyphony": 16,
    "key_type": "velocity_sensitive"
  },

  "components": {
    "keyboard": {
      "bounding_box": { "x": 100, "y": 500, "width": 2200, "height": 280 },
      "count": 61,
      "auto_generate": true
    },

    "buttons": [
      { "id": "btn-1", "label": "1", "zone": { "x": 240, "y": 180, "w": 35, "h": 35 }},
      { "id": "btn-2", "label": "2", "zone": { "x": 290, "y": 180, "w": 35, "h": 35 }},
      // ... 32 botones de función
      { "id": "btn-store", "label": "STORE", "zone": { "x": 1800, "y": 120, "w": 50, "h": 35 }}
    ],

    "sliders": [
      { "id": "data-entry", "label": "Data Entry", "zone": { "x": 2100, "y": 100, "w": 40, "h": 180 }}
    ],

    "displays": [
      { "id": "lcd-main", "label": "LCD Principal", "zone": { "x": 1100, "y": 80, "w": 280, "h": 100 }}
    ],

    "connectors": [
      { "id": "out-l", "label": "Output L", "zone": { "x": 2300, "y": 400, "w": 30, "h": 30 }},
      { "id": "out-r", "label": "Output R", "zone": { "x": 2340, "y": 400, "w": 30, "h": 30 }},
      { "id": "midi-in", "label": "MIDI In", "zone": { "x": 2200, "y": 400, "w": 25, "h": 25 }},
      { "id": "midi-out", "label": "MIDI Out", "zone": { "x": 2240, "y": 400, "w": 25, "h": 25 }},
      { "id": "sustain", "label": "Sustain Pedal", "zone": { "x": 2150, "y": 400, "w": 25, "h": 25 }}
    ]
  }
}
```
