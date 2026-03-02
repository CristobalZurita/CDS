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

    <!-- Step 2: Component Template (Checkbox Form) -->
    <div v-if="currentStep === 1" class="step-content">
      <div class="template-section">
        <h2>Completa la planilla de componentes</h2>
        <p class="subtitle">Marca todos los elementos que tiene tu instrumento</p>

        <div class="components-grid">
          <div 
            v-for="category in componentCategories"
            :key="category.name"
            class="component-category"
          >
            <h3>
              <i :class="category.icon"></i>
              {{ category.name }}
            </h3>
            
            <div class="component-checkboxes">
              <label 
                v-for="comp in category.components"
                :key="comp.id"
                class="component-checkbox"
              >
                <input 
                  type="checkbox"
                  :value="comp.id"
                  v-model="selectedComponents"
                />
                <span class="checkbox-custom"></span>
                <span class="component-label">
                  {{ comp.name }}
                  <small v-if="comp.count">× {{ comp.count }}</small>
                </span>
                <input 
                  v-if="comp.hasQuantity && selectedComponents.includes(comp.id)"
                  type="number"
                  v-model.number="componentQuantities[comp.id]"
                  min="1"
                  max="100"
                  class="quantity-input"
                  placeholder="Cantidad"
                />
              </label>
            </div>
          </div>
        </div>

        <div class="step-actions">
          <button class="btn-secondary" @click="previousStep">
            <i class="fas fa-arrow-left"></i> Atrás
          </button>
          <button class="btn-primary btn-large" data-testid="diagnostic-step1-continue" @click="nextStep">
            Continuar <i class="fas fa-arrow-right"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Step 3: Interactive Photo Markup -->
    <div v-if="currentStep === 2" class="step-content">
      <div class="markup-section">
        <h2>Marca las fallas en las fotos</h2>
        <p class="subtitle">Haz doble clic sobre cada problema para marcarlo</p>

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
            :disabled="totalMarkers === 0"
            data-testid="diagnostic-step2-continue"
            @click="nextStep"
          >
            Continuar <i class="fas fa-arrow-right"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Step 4: Review & Quote -->
    <div v-if="currentStep === 3" class="step-content">
      <div class="review-section">
        <h2>Revisión y cotización</h2>
        
        <!-- Disclaimer Modal -->
        <div class="disclaimer-box">
          <div class="disclaimer-icon">
            <i class="fas fa-exclamation-triangle"></i>
          </div>
          <div class="disclaimer-content">
            <h3>⚠️ Importante: Cotización Preliminar</h3>
            <p>
              Esta es una <strong>estimación preliminar automatizada</strong> basada en 
              el diagnóstico visual. El costo final puede variar después de la 
              inspección física en taller.
            </p>
            <ul>
              <li>La revisión física puede revelar fallas adicionales</li>
              <li>Algunos componentes pueden requerir repuestos especiales</li>
              <li>Los tiempos de reparación son aproximados</li>
            </ul>
            <label class="disclaimer-checkbox">
              <input type="checkbox" v-model="disclaimerAccepted" />
              <span>He leído y acepto que esta es una cotización preliminar</span>
            </label>
          </div>
        </div>

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
              <strong>Componentes identificados:</strong>
              <span>{{ selectedComponents.length }}</span>
            </div>

            <div class="summary-item">
              <strong>Fallas detectadas:</strong>
              <span>{{ totalMarkers }}</span>
            </div>

            <div class="summary-item">
              <strong>Fotos del diagnóstico:</strong>
              <span>{{ uploadedPhotos.length }}</span>
            </div>
          </div>

          <!-- Fault Breakdown -->
          <div class="fault-breakdown">
            <h3>
              <i class="fas fa-list-check"></i>
              Desglose de fallas
            </h3>
            
            <div 
              v-for="(group, type) in groupedFaults"
              :key="type"
              class="fault-group"
            >
              <div class="fault-group-header">
                <i :class="getFaultIcon(type)"></i>
                <span>{{ getFaultName(type) }}</span>
                <span class="count-badge">{{ group.length }}</span>
              </div>
              <ul class="fault-list">
                <li v-for="(fault, idx) in group" :key="idx">
                  Componente #{{ fault.markerIndex + 1 }} 
                  ({{ getPhotoViewName(fault.photoIndex) }})
                </li>
              </ul>
            </div>
          </div>

          <!-- Quote Result -->
          <div class="quote-result">
            <h3>
              <i class="fas fa-calculator"></i>
              Cotización estimada
            </h3>
            
            <div v-if="quoteCalculation" class="quote-breakdown">
              <div class="quote-row">
                <span>Diagnóstico base:</span>
                <span class="price">{{ formatPrice(quoteCalculation.baseDiagnostic) }}</span>
              </div>
              
              <div class="quote-row">
                <span>Reparaciones estimadas:</span>
                <span class="price">{{ formatPrice(quoteCalculation.repairCost) }}</span>
              </div>
              
              <div class="quote-row">
                <span>Complejidad ({{ quoteCalculation.complexityFactor }}×):</span>
                <span class="price">{{ formatPrice(quoteCalculation.complexityAdjustment) }}</span>
              </div>
              
              <div class="quote-row subtotal">
                <span>Subtotal:</span>
                <span class="price">{{ formatPrice(quoteCalculation.subtotal) }}</span>
              </div>
              
              <div class="quote-row total">
                <span>Total estimado:</span>
                <span class="price-large">{{ formatPrice(quoteCalculation.total) }}</span>
              </div>
              
              <div class="time-estimate">
                <i class="fas fa-clock"></i>
                Tiempo estimado: {{ quoteCalculation.estimatedDays }} días hábiles
              </div>
            </div>

            <div class="quote-actions">
              <button 
                class="btn-primary btn-large"
                :disabled="!disclaimerAccepted"
                @click="submitDiagnostic"
              >
                <i class="fas fa-paper-plane"></i>
                Enviar diagnóstico
              </button>
              <button class="btn-secondary" @click="downloadReport">
                <i class="fas fa-download"></i>
                Descargar PDF
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Success Modal -->
    <div v-if="showSuccessModal" class="modal-overlay" @click="closeSuccessModal">
      <div class="modal-content success-modal" @click.stop>
        <div class="success-icon">
          <i class="fas fa-check-circle"></i>
        </div>
        <h2>¡Diagnóstico enviado!</h2>
        <p>Hemos recibido tu solicitud de diagnóstico.</p>
        <p>Te contactaremos pronto para coordinar la revisión en taller.</p>
        <div class="reference-code">
          <strong>Código de referencia:</strong>
          <code>{{ referenceCode }}</code>
        </div>
        <button class="btn-primary" @click="closeSuccessModal">
          Entendido
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { useInstrumentsCatalog } from '@/composables/useInstrumentsCatalog'
import InstrumentCarousel from '@/components/InstrumentCarousel.vue'

const emit = defineEmits(['complete'])

type DiagnosticPhotoView = 'front' | 'back' | 'top' | 'detail'

type DiagnosticPhoto = {
  url: string
  view: DiagnosticPhotoView
  file?: File
  source: 'catalog' | 'upload'
}

// Steps
const steps = ['Selección', 'Componentes', 'Marcado', 'Cotización']
const currentStep = ref(0)

// Step 1: Instrument Selection
const catalog = useInstrumentsCatalog()
const searchQuery = ref('')
const selectedInstrument = ref(null)
const uploadedPhotos = ref<DiagnosticPhoto[]>([])
const fileInput = ref(null)

// Brand/Model selection (NEW - ADITIVO)
const selectedBrandId = ref('')
const selectedModelId = ref('')
const selectedPhotoVariant = ref(0)
const imageVariants = ref<string[]>([]) // Loaded dynamically
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

const filteredInstruments = ref([])
const allInstruments = computed(() => {
  const brands = catalog.getAllBrands(true)
  const list = []
  brands.forEach(b => {
    list.push(...catalog.getInstrumentsByBrand(b.id))
  })
  return list
})

// Step 2: Component Template
const componentCategories = ref([
  {
    name: 'Teclas',
    icon: 'fas fa-keyboard',
    components: [
      { id: 'keys', name: 'Teclas', hasQuantity: true },
      { id: 'keybed', name: 'Lecho de teclas', hasQuantity: false },
      { id: 'aftertouch', name: 'Aftertouch', hasQuantity: false },
    ]
  },
  {
    name: 'Controles',
    icon: 'fas fa-sliders-h',
    components: [
      { id: 'knobs', name: 'Perillas rotatorias', hasQuantity: true },
      { id: 'sliders', name: 'Deslizantes/Faders', hasQuantity: true },
      { id: 'buttons', name: 'Botones', hasQuantity: true },
      { id: 'switches', name: 'Interruptores', hasQuantity: true },
    ]
  },
  {
    name: 'Conectividad',
    icon: 'fas fa-plug',
    components: [
      { id: 'audio_out', name: 'Salidas de audio', hasQuantity: true },
      { id: 'audio_in', name: 'Entradas de audio', hasQuantity: true },
      { id: 'midi', name: 'Puertos MIDI', hasQuantity: false },
      { id: 'cv_gate', name: 'CV/Gate', hasQuantity: true },
      { id: 'usb', name: 'USB', hasQuantity: false },
    ]
  },
  {
    name: 'Otros',
    icon: 'fas fa-cog',
    components: [
      { id: 'display', name: 'Pantalla/Display', hasQuantity: false },
      { id: 'power', name: 'Fuente de poder', hasQuantity: false },
      { id: 'pedals', name: 'Pedales', hasQuantity: true },
      { id: 'wheels', name: 'Ruedas (pitch/mod)', hasQuantity: false },
    ]
  }
])

const selectedComponents = ref([])
const componentQuantities = ref({})

// Step 3: Photo Markup
const activePhotoIndex = ref(0)
const selectedFaultType = ref('broken')
const markupCanvas = ref(null)
const canvasContainer = ref(null)
const canvasDimensions = ref({ width: 0, height: 0 })
const photoMarkers = ref([]) // Array of arrays, one per photo

const commonFaults = ref([
  { id: 'broken', name: 'Roto', icon: 'fas fa-wrench', description: 'Componente roto o dañado', basePrice: 15000 },
  { id: 'missing', name: 'Faltante', icon: 'fas fa-minus-circle', description: 'Componente faltante', basePrice: 20000 },
  { id: 'loose', name: 'Suelto', icon: 'fas fa-compress-arrows-alt', description: 'Componente flojo o inestable', basePrice: 8000 },
  { id: 'noisy', name: 'Ruidoso', icon: 'fas fa-volume-up', description: 'Ruido o estática', basePrice: 12000 },
  { id: 'stuck', name: 'Atascado', icon: 'fas fa-lock', description: 'Componente atascado', basePrice: 10000 },
  { id: 'oxidized', name: 'Oxidado', icon: 'fas fa-flask', description: 'Oxidación o corrosión', basePrice: 18000 },
])

// Step 4: Review
const disclaimerAccepted = ref(false)
const showSuccessModal = ref(false)
const referenceCode = ref('')

// Computed
const canProceed = computed(() => {
  // If instrument found in DB, can proceed
  if (selectedInstrument.value !== null && instrumentFoundInDB.value) {
    return true
  }
  // If instrument NOT in DB, need at least 2 uploaded photos
  if (selectedInstrument.value !== null && !instrumentFoundInDB.value && uploadedPhotos.value.length >= 2) {
    return true
  }
  return false
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

const groupedFaults = computed(() => {
  const grouped = {}
  allMarkers.value.forEach(marker => {
    if (!grouped[marker.type]) {
      grouped[marker.type] = []
    }
    grouped[marker.type].push(marker)
  })
  return grouped
})

const quoteCalculation = computed(() => {
  if (totalMarkers.value === 0) return null

  const baseDiagnostic = 25000 // Base diagnostic fee
  
  // Calculate repair cost based on marked faults
  let repairCost = 0
  allMarkers.value.forEach(marker => {
    const fault = commonFaults.value.find(f => f.id === marker.type)
    if (fault) {
      repairCost += fault.basePrice
    }
  })

  // Complexity factor based on number of faults and components
  const complexityFactor = 1 + (totalMarkers.value * 0.05) + (selectedComponents.value.length * 0.02)
  const complexityAdjustment = repairCost * (complexityFactor - 1)
  
  const subtotal = baseDiagnostic + repairCost + complexityAdjustment
  const total = Math.round(subtotal)

  // Estimate days based on complexity
  const estimatedDays = Math.max(3, Math.min(15, Math.ceil(totalMarkers.value * 0.5 + selectedComponents.value.length * 0.3)))

  return {
    baseDiagnostic,
    repairCost,
    complexityFactor: complexityFactor.toFixed(2),
    complexityAdjustment,
    subtotal,
    total,
    estimatedDays
  }
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
  // Reset model selection when brand changes
  selectedModelId.value = ''
  selectedInstrument.value = null
  imageVariants.value = []
  selectedPhotoVariant.value = 0
  replaceDiagnosticPhotos([])
}

const onModelChange = async () => {
  // Select the instrument when model is chosen
  if (selectedModelId.value && availableModels.value.length > 0) {
    const model = availableModels.value.find(m => m.id === selectedModelId.value)
    if (model) {
      selectedInstrument.value = model
      selectedPhotoVariant.value = 0
      
      // Load image variants asynchronously
      isLoadingVariants.value = true
      try {
        imageVariants.value = await catalog.getInstrumentImageVariants(model)
      } catch (error) {
        console.warn('Error loading image variants:', error)
        imageVariants.value = []
      } finally {
        isLoadingVariants.value = false
      }
      
      // Reuse catalog photos directly when the instrument already exists.
      if (instrumentFoundInDB.value) {
        const fallbackImage = catalog.getInstrumentImage(model)
        const catalogPhotos = buildCatalogPhotos(
          imageVariants.value.length > 0 ? imageVariants.value : [fallbackImage]
        )
        replaceDiagnosticPhotos(catalogPhotos)
      }
    }
  }
}

const filterInstruments = () => {
  const query = searchQuery.value.toLowerCase()
  if (!query || query.trim() === '') {
    filteredInstruments.value = allInstruments.value
    return
  }
  filteredInstruments.value = catalog.searchInstruments(query)
}

const selectInstrument = (instrument) => {
  selectedInstrument.value = instrument
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

const removePhoto = (index) => {
  uploadedPhotos.value.splice(index, 1)
  photoMarkers.value.splice(index, 1)
  if (activePhotoIndex.value >= uploadedPhotos.value.length) {
    activePhotoIndex.value = Math.max(0, uploadedPhotos.value.length - 1)
  }
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
  // Optional: Show preview of marker on hover
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

const editMarker = () => {
  // Optional: Open edit modal for marker
}

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
  // Generate reference code
  referenceCode.value = 'DIAG-' + Date.now().toString(36).toUpperCase()
  
  // Here you would send data to backend
  const diagnosticData = {
    instrument: selectedInstrument.value,
    components: selectedComponents.value,
    quantities: componentQuantities.value,
    photos: uploadedPhotos.value.map(p => ({
      view: p.view,
      markers: photoMarkers.value[uploadedPhotos.value.indexOf(p)]
    })),
    quote: quoteCalculation.value,
    referenceCode: referenceCode.value,
    timestamp: new Date().toISOString()
  }
  
  const faultTypes = Array.from(new Set(allMarkers.value.map(m => m.type)))
  emit('complete', faultTypes)
  console.log('Submitting diagnostic:', diagnosticData)
  
  // Show success modal
  showSuccessModal.value = true
}

const downloadReport = () => {
  // Generate PDF report (would use library like jsPDF)
  alert('Descargando reporte PDF...')
}

const closeSuccessModal = () => {
  showSuccessModal.value = false
  // Reset form
  currentStep.value = 0
  selectedInstrument.value = null
  replaceDiagnosticPhotos([])
  selectedComponents.value = []
  disclaimerAccepted.value = false
}

// Watch for photo changes to reinitialize canvas
watch(activePhotoIndex, () => {
  if (currentStep.value === 2) {
    nextTick(() => initCanvas())
  }
})

filteredInstruments.value = allInstruments.value
</script>
