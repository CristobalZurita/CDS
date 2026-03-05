<template>
  <div class="interactive-diagnostic">
    <!-- Header with Progress -->
    <div class="diagnostic-header">
      <h1>🎹 Diagnóstico Visual Interactivo</h1>
      <div class="progress-tracker">
        <div 
          v-for="(step, idx) in steps" 
          :key="idx"
          class="progress-step"
          :class="{ active: currentStep === idx, completed: currentStep > idx }"
        >
          <div class="step-circle">{{ idx + 1 }}</div>
          <span class="step-label">{{ step }}</span>
        </div>
      </div>
    </div>

    <!-- Step 1: Select/Upload Instrument -->
    <div v-if="currentStep === 0" class="step-content">
      <div class="upload-section">
        <h2>🔍 Busca tu instrumento</h2>
        <p class="subtitle">Selecciona marca y modelo para cargar desde nuestros registros</p>
        
        <!-- Step 1A: Brand Selection -->
        <div class="brand-selector">
          <label>Marca</label>
          <select
            v-model="selectedBrandId"
            class="form-select"
            data-testid="diagnostic-brand-select"
            @change="onBrandChange"
          >
            <option value="">-- Selecciona una marca --</option>
            <option v-for="brand in availableBrands" :key="brand.id" :value="brand.id">
              {{ brand.name }}
            </option>
          </select>
        </div>

        <!-- Step 1B: Model Selection (only if brand selected) -->
        <div v-if="selectedBrandId" class="model-selector">
          <label>Modelo</label>
          <select
            v-model="selectedModelId"
            class="form-select"
            data-testid="diagnostic-model-select"
            @change="onModelChange"
          >
            <option value="">-- Selecciona un modelo --</option>
            <option v-for="model in availableModels" :key="model.id" :value="model.id">
              {{ model.model }}
            </option>
          </select>
        </div>

        <!-- Step 1C: Product Photo (only if model selected) -->
        <div v-if="selectedInstrument" class="product-preview">
          <div class="product-header">
            <div v-if="selectedInstrument.brandLogo" class="brand-logo">
              <img :src="selectedInstrument.brandLogo" :alt="selectedInstrument.brandLabel" />
            </div>
            <h3>{{ selectedInstrument.brandLabel }} - {{ selectedInstrument.model }}</h3>
          </div>

          <!-- Carousel for multi-photo instruments or single image -->
          <div v-if="selectedInstrumentForCarousel" class="product-carousel">
            <InstrumentCarousel 
              :instrument="selectedInstrumentForCarousel"
              :show-photo-label="false"
            />
          </div>

          <!-- No image placeholder -->
          <div v-else class="product-image-placeholder">
            <i class="fas fa-keyboard"></i>
            <p>Sin imagen en la base de datos</p>
          </div>
        </div>

        <!-- Step 1D: Upload photos (only if product NOT found) -->
        <div v-if="selectedBrandId && selectedModelId && !instrumentFoundInDB" class="upload-area">
          <p class="warning-text">⚠️ Este instrumento no existe en nuestra base de datos</p>
          <p class="info-text">Sube al menos 2 fotos para continuar (frontal y trasera)</p>
          
          <div 
            class="upload-zone"
            @drop.prevent="handleDrop"
            @dragover.prevent
          >
            <div class="upload-content">
              <i class="fas fa-cloud-upload-alt"></i>
              <p><strong>Arrastra fotos aquí</strong> o haz clic para seleccionar</p>
              <p class="subtitle">Necesitamos: frontal, trasera y cenital</p>
              <input 
                ref="fileInput"
                type="file"
                multiple
                accept="image/*"
                class="hidden"
                @change="handleFileUpload"
              />
              <button class="btn-primary" @click="fileInput?.click()">
                <i class="fas fa-image me-2"></i>
                Seleccionar fotos
              </button>
            </div>
          </div>

          <!-- Show count of uploaded photos -->
          <div v-if="uploadedPhotos.length > 0" class="photos-count">
            <p>✅ {{ uploadedPhotos.length }} foto(s) cargada(s)</p>
          </div>
        </div>

        <div class="step-actions">
          <button 
            class="btn-primary btn-large"
            :disabled="!canProceed"
            data-testid="diagnostic-step0-continue"
            @click="nextStep"
          >
            Continuar <i class="fas fa-arrow-right"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Step 2: Guided Troubleshooting -->
    <div v-if="currentStep === 1" class="step-content">
      <div class="template-section">
        <h2>Describe el problema principal</h2>
        <p class="subtitle">
          Responde en cascada sólo lo visible o lo que recuerdas del funcionamiento del equipo.
        </p>

        <div class="guided-form-grid">
          <div class="guided-card">
            <label for="diagnostic-power" class="guided-label">¿El equipo enciende?</label>
            <select
              id="diagnostic-power"
              v-model="guidedAnswers.power"
              class="form-select"
              data-testid="diagnostic-power-select"
            >
              <option value="">Selecciona una opción</option>
              <option value="no_power">No enciende</option>
              <option value="intermittent_power">Prende y se apaga / enciende intermitente</option>
              <option value="powers_on">Sí, enciende</option>
            </select>
            <p class="guided-help">
              Si no enciende, el sistema corta las ramas posteriores y prioriza esa falla como principal.
            </p>
          </div>

          <div class="guided-card" :class="{ 'guided-card--disabled': branchesBlockedByPower }">
            <label for="diagnostic-audio" class="guided-label">¿Cómo responde el audio?</label>
            <select
              id="diagnostic-audio"
              v-model="guidedAnswers.audio"
              class="form-select"
              data-testid="diagnostic-audio-select"
              :disabled="branchesBlockedByPower"
            >
              <option value="none">Sin novedad</option>
              <option value="no_audio">No suena</option>
              <option value="one_side">Suena por un solo lado</option>
              <option value="distorted">Suena distorsionado</option>
              <option value="weak">Suena muy bajo</option>
            </select>
          </div>

          <div
            v-if="instrumentMetrics.hasKeyboard"
            class="guided-card"
            :class="{ 'guided-card--disabled': branchesBlockedByPower }"
          >
            <label for="diagnostic-keyboard" class="guided-label">¿Cómo responde el teclado?</label>
            <select
              id="diagnostic-keyboard"
              v-model="guidedAnswers.keyboard"
              class="form-select"
              data-testid="diagnostic-keyboard-select"
              :disabled="branchesBlockedByPower"
            >
              <option value="none">Sin novedad</option>
              <option value="single_key">Una tecla no suena</option>
              <option value="multiple_keys">Varias teclas fallan</option>
              <option value="stuck_keys">Hay teclas pegadas o duras</option>
            </select>
          </div>

          <div
            v-if="instrumentMetrics.controlsCount > 0"
            class="guided-card"
            :class="{ 'guided-card--disabled': branchesBlockedByPower }"
          >
            <label for="diagnostic-controls" class="guided-label">¿Qué pasa con botones, sliders o perillas?</label>
            <select
              id="diagnostic-controls"
              v-model="guidedAnswers.controls"
              class="form-select"
              data-testid="diagnostic-controls-select"
              :disabled="branchesBlockedByPower"
            >
              <option value="none">Sin novedad</option>
              <option value="single_button">Un botón falla</option>
              <option value="single_slider">Un slider/fader falla</option>
              <option value="single_knob">Una perilla/encoder falla</option>
              <option value="multiple_controls">Hay varios controles con problemas</option>
            </select>
          </div>

          <div
            v-if="instrumentMetrics.hasDisplay"
            class="guided-card"
            :class="{ 'guided-card--disabled': branchesBlockedByPower }"
          >
            <label for="diagnostic-display" class="guided-label">¿Cómo está la pantalla o display?</label>
            <select
              id="diagnostic-display"
              v-model="guidedAnswers.display"
              class="form-select"
              data-testid="diagnostic-display-select"
              :disabled="branchesBlockedByPower"
            >
              <option value="none">Sin novedad</option>
              <option value="no_display">No muestra nada</option>
              <option value="low_contrast">Se ve muy tenue</option>
              <option value="broken_display">Está dañada o quebrada</option>
            </select>
          </div>

          <div
            v-if="instrumentMetrics.hasConnectivity"
            class="guided-card"
            :class="{ 'guided-card--disabled': branchesBlockedByPower }"
          >
            <label for="diagnostic-connectivity" class="guided-label">¿Hay problemas de conexión?</label>
            <select
              id="diagnostic-connectivity"
              v-model="guidedAnswers.connectivity"
              class="form-select"
              data-testid="diagnostic-connectivity-select"
              :disabled="branchesBlockedByPower"
            >
              <option value="none">Sin novedad</option>
              <option value="midi_issue">MIDI no responde</option>
              <option value="usb_issue">USB no se conecta</option>
              <option value="audio_jack_issue">Un conector o jack está fallando</option>
            </select>
          </div>

          <div class="guided-card">
            <label for="diagnostic-cosmetic" class="guided-label">¿Hay daños visibles?</label>
            <select
              id="diagnostic-cosmetic"
              v-model="guidedAnswers.cosmetic"
              class="form-select"
              data-testid="diagnostic-cosmetic-select"
            >
              <option value="none">Sin daños visibles relevantes</option>
              <option value="cosmetic_damage">Golpes, piezas sueltas o faltantes</option>
              <option value="oxidation">Óxido o corrosión visible</option>
              <option value="water_damage">Señales de humedad o derrame</option>
              <option value="heavy_damage">Daño visible importante</option>
            </select>
          </div>
        </div>

        <div v-if="branchesBlockedByPower" class="guided-warning" data-testid="diagnostic-branch-warning">
          El equipo quedó marcado como <strong>no enciende</strong>. Las ramas posteriores se consideran secundarias.
          Si recuerdas fallas previas, descríbelas en el texto libre.
        </div>

        <div class="guided-notes">
          <label for="diagnostic-customer-notes" class="guided-label">
            Explica con tus palabras qué pasaba antes y qué problema te preocupa más
          </label>
          <textarea
            id="diagnostic-customer-notes"
            v-model.trim="customerNotes"
            rows="5"
            class="form-control"
            data-testid="diagnostic-customer-notes"
            placeholder="Ejemplo: antes de dejar de encender, el botón SHIFT fallaba y el audio sonaba por un solo lado."
          ></textarea>
        </div>

        <div class="step-actions">
          <button class="btn-secondary" @click="previousStep">
            <i class="fas fa-arrow-left"></i> Atrás
          </button>
          <button
            class="btn-primary btn-large"
            data-testid="diagnostic-step1-continue"
            :disabled="!canProceedFromSymptoms"
            @click="nextStep"
          >
            Continuar <i class="fas fa-arrow-right"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Step 3: Interactive Photo Markup -->
    <div v-if="currentStep === 2" class="step-content">
      <div class="markup-section">
        <h2>Marca daños visibles o zonas con problema</h2>
        <p class="subtitle">Este paso es opcional, pero ayuda a orientar mejor la estimación visual</p>

        <div class="photo-tabs">
          <button 
            v-for="(photo, idx) in uploadedPhotos"
            :key="idx"
            class="tab-btn"
            data-testid="diagnostic-photo-tab"
            :class="{ active: activePhotoIndex === idx }"
            @click="activePhotoIndex = idx"
          >
            <i class="fas fa-image"></i>
            {{ photo.view === 'front' ? 'Frontal' : 
               photo.view === 'back' ? 'Trasera' : 
               photo.view === 'top' ? 'Cenital' : 'Detalle' }}
          </button>
        </div>

        <div class="markup-workspace">
          <div class="toolbar">
            <div class="tool-group">
              <button 
                v-for="fault in commonFaults"
                :key="fault.id"
                class="tool-btn"
                :class="{ active: selectedFaultType === fault.id }"
                @click="selectedFaultType = fault.id"
                :title="fault.description"
              >
                <i :class="fault.icon"></i>
                {{ fault.name }}
              </button>
            </div>
            <div class="tool-actions">
              <button class="tool-btn danger" @click="clearMarkers" title="Limpiar marcas">
                <i class="fas fa-eraser"></i>
              </button>
              <button class="tool-btn" @click="undoLastMarker" title="Deshacer">
                <i class="fas fa-undo"></i>
              </button>
            </div>
          </div>

          <div class="canvas-container" ref="canvasContainer">
            <canvas 
              ref="markupCanvas"
              class="markup-canvas"
              data-testid="diagnostic-markup-canvas"
              @dblclick="addMarker"
              @mousemove="updateCursor"
            ></canvas>

            <svg
              v-if="canvasDimensions.width > 0 && canvasDimensions.height > 0"
              class="markers-overlay"
              :viewBox="`0 0 ${canvasDimensions.width} ${canvasDimensions.height}`"
              preserveAspectRatio="none"
              aria-hidden="true"
            >
              <g
                v-for="(marker, idx) in currentPhotoMarkers"
                :key="idx"
                class="fault-marker-svg"
                :class="`marker-${marker.type}`"
                :transform="`translate(${getMarkerCanvasX(marker)} ${getMarkerCanvasY(marker)})`"
                @click="editMarker(marker, idx)"
              >
                <circle class="marker-dot" r="13" />
                <text class="marker-index" y="4">{{ idx + 1 }}</text>
                <g class="marker-remove-control" transform="translate(15 -15)" @click.stop="removeMarker(idx)">
                  <circle class="marker-remove-dot" r="7.5" />
                  <text class="marker-remove-x" y="3">x</text>
                </g>
              </g>
            </svg>
          </div>

          <div class="markers-list">
            <h4 data-testid="diagnostic-marker-count">Fallas marcadas ({{ totalMarkers }})</h4>
            <div 
              v-for="(marker, idx) in allMarkers"
              :key="`${marker.photoIndex}-${idx}`"
              class="marker-item"
            >
              <span class="marker-number">{{ idx + 1 }}</span>
              <i :class="getFaultIcon(marker.type)"></i>
              <span class="marker-description">
                {{ getFaultName(marker.type) }} - 
                {{ getPhotoViewName(marker.photoIndex) }}
              </span>
              <button 
                class="btn-icon"
                @click="focusMarker(marker.photoIndex, marker.markerIndex)"
              >
                <i class="fas fa-crosshairs"></i>
              </button>
            </div>
          </div>
        </div>

        <div class="step-actions">
          <button class="btn-secondary" @click="previousStep">
            <i class="fas fa-arrow-left"></i> Atrás
          </button>
          <button
            class="btn-primary btn-large"
            data-testid="diagnostic-step2-continue"
            @click="nextStep"
          >
            Continuar <i class="fas fa-arrow-right"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Step 4: Review & Range -->
    <div v-if="currentStep === 3" class="step-content">
      <div class="review-section">
        <h2>Resumen previo a la estimación</h2>

        <!-- Summary -->
        <div class="diagnostic-summary">
          <div class="summary-card">
            <h3>
              <i class="fas fa-tools"></i>
              Resumen del diagnóstico
            </h3>
            
            <div class="summary-item">
              <strong>Instrumento:</strong>
              <span v-if="selectedInstrument">
                {{ selectedInstrument.brandLabel }} {{ selectedInstrument.model }}
              </span>
              <span v-else>Instrumento personalizado</span>
            </div>

            <div class="summary-item">
              <strong>Perfil del equipo:</strong>
              <span>{{ instrumentMetrics.sizeLabel }}</span>
            </div>

            <div class="summary-item">
              <strong>Síntomas guiados:</strong>
              <span>{{ effectiveSymptoms.length }}</span>
            </div>

            <div class="summary-item">
              <strong>Daños visibles marcados:</strong>
              <span>{{ totalMarkers }}</span>
            </div>

            <div class="summary-item">
              <strong>Notas del cliente:</strong>
              <span>{{ customerNotes ? 'Sí' : 'No' }}</span>
            </div>
          </div>

          <!-- Symptom Breakdown -->
          <div class="fault-breakdown">
            <h3>
              <i class="fas fa-sitemap"></i>
              Árbol de síntomas considerado
            </h3>

            <div class="fault-group">
              <div class="fault-group-header">
                <i class="fas fa-bolt"></i>
                <span>{{ mainIssueLabel }}</span>
              </div>
              <ul class="fault-list">
                <li v-for="symptom in symptomSummaryItems" :key="symptom.id">
                  {{ symptom.label }}
                </li>
                <li v-if="totalMarkers > 0">
                  {{ totalMarkers }} marca(s) visibles agregadas en fotos
                </li>
                <li v-if="customerNotes">
                  Observaciones del cliente incluidas para revisión
                </li>
              </ul>
            </div>

            <div class="guided-warning guided-warning--soft">
              Se mostrará un rango referencial entre <strong>{{ formatPrice(40000) }}</strong> y
              <strong>{{ formatPrice(150000) }}</strong>, sujeto a aceptación previa del aviso legal.
            </div>
          </div>
        </div>

        <div class="step-actions">
          <button class="btn-secondary" @click="previousStep">
            <i class="fas fa-arrow-left"></i> Atrás
          </button>
          <button
            class="btn-primary btn-large"
            data-testid="diagnostic-step3-continue"
            @click="submitDiagnostic"
          >
            Ver estimación referencial <i class="fas fa-arrow-right"></i>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, reactive } from 'vue'
import { useInstrumentsCatalog } from '@/composables/useInstrumentsCatalog'
import InstrumentCarousel from '@/components/InstrumentCarousel.vue'

const props = defineProps({
  initialInstrument: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['complete'])

type DiagnosticPhotoView = 'front' | 'back' | 'top' | 'detail'

type DiagnosticPhoto = {
  url: string
  view: DiagnosticPhotoView
  file?: File
  source: 'catalog' | 'upload'
}

// Steps
const steps = ['Selección', 'Síntomas', 'Marcado', 'Resumen']
const currentStep = ref(0)

// Step 1: Instrument Selection
const catalog = useInstrumentsCatalog()
const selectedInstrument = ref(null)
const uploadedPhotos = ref<DiagnosticPhoto[]>([])
const fileInput = ref(null)

// Brand/Model selection
const selectedBrandId = ref('')
const selectedModelId = ref('')
const imageVariants = ref<string[]>([])
const isLoadingVariants = ref(false)
const availableBrands = computed(() => catalog.getAllBrands(true))
const availableModels = computed(() => {
  if (!selectedBrandId.value) return []
  return catalog.getInstrumentsByBrand(selectedBrandId.value)
})
const selectedInstrumentForCarousel = computed(() => {
  if (!selectedInstrument.value) return null

  const foto_principal = selectedInstrument.value.foto_principal || selectedInstrument.value.photo_key
  if (!foto_principal) return null

  const fotos_adicionales = Array.isArray(selectedInstrument.value.fotos_adicionales)
    ? selectedInstrument.value.fotos_adicionales
    : []

  return {
    id: selectedInstrument.value.id,
    marca: selectedInstrument.value.marca || selectedInstrument.value.brandLabel || selectedInstrument.value.brand || '',
    modelo: selectedInstrument.value.modelo || selectedInstrument.value.model || '',
    foto_principal,
    fotos_adicionales
  }
})

const instrumentFoundInDB = computed(() => selectedInstrumentForCarousel.value !== null)

// Step 2: Guided troubleshooting
const guidedAnswers = reactive({
  power: '',
  audio: 'none',
  keyboard: 'none',
  controls: 'none',
  display: 'none',
  connectivity: 'none',
  cosmetic: 'none',
})
const customerNotes = ref('')

const symptomCatalog = {
  no_power: 'El equipo no enciende',
  intermittent_power: 'El encendido es intermitente',
  no_audio: 'No sale audio',
  one_side: 'El audio sale por un solo lado',
  distorted: 'El audio sale distorsionado',
  weak: 'El audio sale débil',
  single_key: 'Una tecla no responde',
  multiple_keys: 'Varias teclas fallan',
  stuck_keys: 'Hay teclas pegadas o duras',
  single_button: 'Un botón falla',
  single_slider: 'Un slider o fader falla',
  single_knob: 'Una perilla o encoder falla',
  multiple_controls: 'Hay varios controles con problemas',
  no_display: 'La pantalla no muestra nada',
  low_contrast: 'La pantalla se ve tenue',
  broken_display: 'La pantalla está dañada',
  midi_issue: 'La conexión MIDI falla',
  usb_issue: 'La conexión USB falla',
  audio_jack_issue: 'Hay un conector o jack fallando',
  cosmetic_damage: 'Se observan golpes o piezas faltantes',
  oxidation: 'Se ve óxido o corrosión',
  water_damage: 'Hay señales de humedad o derrame',
  heavy_damage: 'Hay daño visible importante',
}

// Step 3: Photo Markup
const activePhotoIndex = ref(0)
const selectedFaultType = ref('broken')
const markupCanvas = ref(null)
const canvasContainer = ref(null)
const canvasDimensions = ref({ width: 0, height: 0 })
const photoMarkers = ref([])

const commonFaults = ref([
  { id: 'broken', name: 'Golpe o daño visible', icon: 'fas fa-triangle-exclamation', description: 'Zona quebrada, golpeada o rota' },
  { id: 'missing', name: 'Pieza faltante', icon: 'fas fa-minus-circle', description: 'Falta un botón, tapa o parte visible' },
  { id: 'button_damage', name: 'Tecla o botón dañado', icon: 'fas fa-keyboard', description: 'Elemento externo visible con desgaste o daño' },
  { id: 'connector_damage', name: 'Conector dañado', icon: 'fas fa-plug-circle-exclamation', description: 'Jack, puerto o conector visible dañado' },
  { id: 'display_damage', name: 'Pantalla dañada', icon: 'fas fa-display', description: 'Display quebrado o visible con daño' },
  { id: 'oxidized', name: 'Óxido o corrosión', icon: 'fas fa-flask', description: 'Corrosión visible' },
])

// Computed
const canProceed = computed(() => {
  if (selectedInstrument.value !== null && instrumentFoundInDB.value) {
    return true
  }
  if (selectedInstrument.value !== null && !instrumentFoundInDB.value && uploadedPhotos.value.length >= 2) {
    return true
  }
  return false
})

const instrumentMetrics = computed(() => {
  const instrument = selectedInstrument.value || {}
  const modelText = `${instrument.model || instrument.modelo || ''} ${instrument.type || ''}`.toLowerCase()
  const components = instrument.components || {}
  const keyboardless = ['rack', 'module', 'desktop', 'expander'].some((term) => modelText.includes(term))
  const keyMatch = modelText.match(/\b(25|32|37|49|61|73|76|88)\b/)
  const keyCount = keyboardless ? 0 : Number(keyMatch?.[1] || 61)
  const controlsCount =
    Number(components.botones || 0) +
    Number(components.faders || 0) +
    Number(components.encoders_rotativos || 0)

  let sizeLabel = 'sin teclado'
  if (!keyboardless && keyCount <= 37) sizeLabel = 'teclado chico'
  else if (!keyboardless && keyCount <= 61) sizeLabel = 'teclado mediano'
  else if (!keyboardless) sizeLabel = 'teclado grande'

  return {
    hasKeyboard: !keyboardless,
    keyCount,
    controlsCount,
    hasDisplay: Boolean(components.lcd),
    hasConnectivity: Boolean(components.usb || components.midi_din || components.salidas_audio),
    sizeLabel,
  }
})

const branchesBlockedByPower = computed(() => guidedAnswers.power === 'no_power')

const effectiveSymptoms = computed(() => {
  const symptoms = []

  if (guidedAnswers.power === 'no_power') {
    symptoms.push('no_power')
  } else if (guidedAnswers.power === 'intermittent_power') {
    symptoms.push('intermittent_power')
  }

  if (!branchesBlockedByPower.value) {
    ;['audio', 'keyboard', 'controls', 'display', 'connectivity'].forEach((field) => {
      const value = String(guidedAnswers[field] || '')
      if (value && value !== 'none') {
        symptoms.push(value)
      }
    })
  }

  if (guidedAnswers.cosmetic && guidedAnswers.cosmetic !== 'none') {
    symptoms.push(guidedAnswers.cosmetic)
  }

  return symptoms
})

const canProceedFromSymptoms = computed(() => {
  if (!guidedAnswers.power) return false
  return effectiveSymptoms.value.length > 0 || Boolean(customerNotes.value.trim())
})

const currentPhotoMarkers = computed(() => {
  return photoMarkers.value[activePhotoIndex.value] || []
})

const allMarkers = computed(() => {
  const markers = []
  photoMarkers.value.forEach((photoMarkersArray, photoIndex) => {
    if (!Array.isArray(photoMarkersArray)) return
    photoMarkersArray.forEach((marker, markerIndex) => {
      markers.push({ ...marker, photoIndex, markerIndex })
    })
  })
  return markers
})

const totalMarkers = computed(() => {
  return allMarkers.value.length
})

const mainIssueLabel = computed(() => {
  if (!effectiveSymptoms.value.length) {
    return 'Revisión general'
  }
  return symptomCatalog[effectiveSymptoms.value[0]] || 'Revisión general'
})

const symptomSummaryItems = computed(() => {
  return effectiveSymptoms.value.map((symptomId) => ({
    id: symptomId,
    label: symptomCatalog[symptomId] || symptomId,
  }))
})

const getPhotoViewByIndex = (index: number): DiagnosticPhotoView => {
  if (index === 0) return 'front'
  if (index === 1) return 'back'
  if (index === 2) return 'top'
  return 'detail'
}

const replaceDiagnosticPhotos = (photos: DiagnosticPhoto[]) => {
  uploadedPhotos.value = photos
  photoMarkers.value = photos.map(() => [])
  activePhotoIndex.value = 0
}

const buildCatalogPhotos = (urls: string[]): DiagnosticPhoto[] =>
  urls
    .filter(Boolean)
    .map((url, index) => ({
      url,
      view: getPhotoViewByIndex(index),
      source: 'catalog' as const,
    }))

// Methods
const onBrandChange = () => {
  selectedModelId.value = ''
  selectedInstrument.value = null
  imageVariants.value = []
  replaceDiagnosticPhotos([])
}

const applySelectedInstrument = async (model) => {
  if (!model) return

  selectedInstrument.value = model
  selectedBrandId.value = model.brand || ''
  selectedModelId.value = model.id || ''

  isLoadingVariants.value = true
  try {
    imageVariants.value = await catalog.getInstrumentImageVariants(model)
  } catch (error) {
    console.warn('Error loading image variants:', error)
    imageVariants.value = []
  } finally {
    isLoadingVariants.value = false
  }

  if (instrumentFoundInDB.value) {
    const fallbackImage = catalog.getInstrumentImage(model)
    const catalogPhotos = buildCatalogPhotos(
      imageVariants.value.length > 0 ? imageVariants.value : [fallbackImage]
    )
    replaceDiagnosticPhotos(catalogPhotos)
  }
}

const onModelChange = async () => {
  if (!selectedModelId.value || availableModels.value.length === 0) return
  const model = availableModels.value.find(m => m.id === selectedModelId.value)
  if (model) {
    await applySelectedInstrument(model)
  }
}

const handleFileUpload = (event) => {
  const files = Array.from(event.target.files)
  processFiles(files)
}

const handleDrop = (event) => {
  const files = Array.from(event.dataTransfer.files)
  processFiles(files)
}

const processFiles = (files) => {
  files.forEach((file) => {
    if (file.type.startsWith('image/')) {
      const reader = new FileReader()
      reader.onload = (e) => {
        const photoIndex = uploadedPhotos.value.length
        const result = typeof e.target?.result === 'string' ? e.target.result : ''
        uploadedPhotos.value.push({
          url: result,
          view: getPhotoViewByIndex(photoIndex),
          file,
          source: 'upload'
        })
        photoMarkers.value[photoIndex] = []
      }
      reader.readAsDataURL(file)
    }
  })
}

const initCanvas = () => {
  if (!markupCanvas.value || !canvasContainer.value || !uploadedPhotos.value[activePhotoIndex.value]) return
  
  const canvas = markupCanvas.value
  const photo = uploadedPhotos.value[activePhotoIndex.value]
  
  const img = new Image()
  img.onload = () => {
    // Set canvas size to match image
    canvas.width = img.width
    canvas.height = img.height
    canvasDimensions.value = { width: img.width, height: img.height }
    
    // Draw image
    const ctx = canvas.getContext('2d')
    ctx.drawImage(img, 0, 0)
  }
  img.src = photo.url
}

const getCanvasScaleX = () => {
  const canvas = markupCanvas.value
  if (!canvas || !canvas.clientWidth) return 1
  return canvas.width / canvas.clientWidth
}

const getCanvasScaleY = () => {
  const canvas = markupCanvas.value
  if (!canvas || !canvas.clientHeight) return 1
  return canvas.height / canvas.clientHeight
}

const getMarkerCanvasX = (marker) => {
  if (Number.isFinite(marker.actualX)) return marker.actualX
  return Number(marker.x || 0) * getCanvasScaleX()
}

const getMarkerCanvasY = (marker) => {
  if (Number.isFinite(marker.actualY)) return marker.actualY
  return Number(marker.y || 0) * getCanvasScaleY()
}

const addMarker = (event) => {
  if (!selectedFaultType.value) return
  
  const canvas = markupCanvas.value
  const rect = canvas.getBoundingClientRect()
  const scaleX = canvas.width / rect.width
  const scaleY = canvas.height / rect.height
  
  const x = (event.clientX - rect.left) * scaleX
  const y = (event.clientY - rect.top) * scaleY
  
  const marker = {
    x: event.clientX - rect.left,
    y: event.clientY - rect.top,
    actualX: x,
    actualY: y,
    type: selectedFaultType.value,
    timestamp: Date.now()
  }
  
  if (!photoMarkers.value[activePhotoIndex.value]) {
    photoMarkers.value[activePhotoIndex.value] = []
  }
  photoMarkers.value[activePhotoIndex.value].push(marker)
}

const updateCursor = () => {
}

const removeMarker = (index) => {
  photoMarkers.value[activePhotoIndex.value].splice(index, 1)
}

const clearMarkers = () => {
  if (confirm('¿Limpiar todas las marcas de esta foto?')) {
    photoMarkers.value[activePhotoIndex.value] = []
  }
}

const undoLastMarker = () => {
  if (currentPhotoMarkers.value.length > 0) {
    photoMarkers.value[activePhotoIndex.value].pop()
  }
}

const editMarker = () => {}

const focusMarker = (photoIndex) => {
  activePhotoIndex.value = photoIndex
}

const getFaultIcon = (type) => {
  const fault = commonFaults.value.find(f => f.id === type)
  return fault ? fault.icon : 'fas fa-question'
}

const getFaultName = (type) => {
  const fault = commonFaults.value.find(f => f.id === type)
  return fault ? fault.name : 'Desconocido'
}

const getPhotoViewName = (index) => {
  const photo = uploadedPhotos.value[index]
  if (!photo) return 'Foto'
  const viewNames = {
    front: 'Frontal',
    back: 'Trasera',
    top: 'Cenital',
    detail: 'Detalle'
  }
  return viewNames[photo.view] || 'Foto'
}

const formatPrice = (price) => {
  return new Intl.NumberFormat('es-CL', {
    style: 'currency',
    currency: 'CLP',
    minimumFractionDigits: 0
  }).format(price)
}

const nextStep = () => {
  if (currentStep.value < steps.length - 1) {
    currentStep.value++
    if (currentStep.value === 2) {
      nextTick(() => initCanvas())
    }
  }
}

const previousStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

const submitDiagnostic = async () => {
  const diagnosticData = {
    instrument: selectedInstrument.value,
    instrument_id: selectedInstrument.value?.id || '',
    selected_symptoms: effectiveSymptoms.value,
    guided_answers: { ...guidedAnswers },
    customer_notes: customerNotes.value.trim(),
    visual_issue_count: totalMarkers.value,
    marked_faults: allMarkers.value.map((marker) => marker.type),
    photos: uploadedPhotos.value.map((photo, index) => ({
      view: photo.view,
      markers: photoMarkers.value[index] || [],
    })),
    summary: {
      main_issue: mainIssueLabel.value,
      size_label: instrumentMetrics.value.sizeLabel,
      key_count: instrumentMetrics.value.keyCount,
      controls_count: instrumentMetrics.value.controlsCount,
      symptom_count: effectiveSymptoms.value.length,
      notes_present: Boolean(customerNotes.value.trim()),
    },
    timestamp: new Date().toISOString(),
  }

  emit('complete', diagnosticData)
}

// Watch for photo changes to reinitialize canvas
watch(activePhotoIndex, () => {
  if (currentStep.value === 2) {
    nextTick(() => initCanvas())
  }
})

watch(
  () => guidedAnswers.power,
  (value) => {
    if (value === 'no_power') {
      guidedAnswers.audio = 'none'
      guidedAnswers.keyboard = 'none'
      guidedAnswers.controls = 'none'
      guidedAnswers.display = 'none'
      guidedAnswers.connectivity = 'none'
    }
  }
)

watch(
  () => props.initialInstrument,
  async (instrument) => {
    if (!instrument) return
    await applySelectedInstrument(instrument)
    currentStep.value = 1
  },
  { immediate: true }
)
</script>
