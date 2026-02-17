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
          <select v-model="selectedBrandId" class="form-select" @change="onBrandChange">
            <option value="">-- Selecciona una marca --</option>
            <option v-for="brand in availableBrands" :key="brand.id" :value="brand.id">
              {{ brand.name }}
            </option>
          </select>
        </div>

        <!-- Step 1B: Model Selection (only if brand selected) -->
        <div v-if="selectedBrandId" class="model-selector">
          <label>Modelo</label>
          <select v-model="selectedModelId" class="form-select" @change="onModelChange">
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
          <button class="btn-primary btn-large" @click="nextStep">
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
            <h4>Fallas marcadas ({{ totalMarkers }})</h4>
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

// Steps
const steps = ['Selección', 'Componentes', 'Marcado', 'Cotización']
const currentStep = ref(0)

// Step 1: Instrument Selection
const catalog = useInstrumentsCatalog()
const searchQuery = ref('')
const selectedInstrument = ref(null)
const uploadedPhotos = ref([])
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

// Methods
const onBrandChange = () => {
  // Reset model selection when brand changes
  selectedModelId.value = ''
  selectedInstrument.value = null
  imageVariants.value = []
  selectedPhotoVariant.value = 0
  uploadedPhotos.value = []
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
      
      // Clear uploads if model exists in DB
      if (instrumentFoundInDB.value) {
        uploadedPhotos.value = []
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
  files.forEach((file, index) => {
    if (file.type.startsWith('image/')) {
      const reader = new FileReader()
      reader.onload = (e) => {
        const photoIndex = uploadedPhotos.value.length
        uploadedPhotos.value.push({
          url: e.target.result,
          view: index === 0 ? 'front' : index === 1 ? 'back' : index === 2 ? 'top' : 'detail',
          file: file
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
  uploadedPhotos.value = []
  selectedComponents.value = []
  photoMarkers.value = []
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

<style lang="scss" scoped>
@import '@/scss/_core.scss';

.interactive-diagnostic {
  min-height: 100vh;
  background: linear-gradient(135deg, $color-slate-50-legacy 0%, $color-slate-200-legacy 100%);
  padding: $spacer-xl;
}

.diagnostic-header {
  max-width: 1400px;
  margin: 0 auto 3rem;
  text-align: center;

  h1 {
    font-size: 2.5rem;
    font-weight: 800;
    color: $dark;
    margin-bottom: 2rem;
    letter-spacing: -0.02em;
  }
}

.progress-tracker {
  display: flex;
  justify-content: center;
  gap: 1rem;
  flex-wrap: wrap;

  .progress-step {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1.5rem;
    background: $color-white;
    border-radius: 100px;
    border: 2px solid $light-3;
    transition: all 0.3s ease;

    &.active {
      border-color: $primary;
      background: linear-gradient(135deg, $primary 0%, darken($primary, 10%) 100%);
      color: $color-white;
      box-shadow: 0 4px 12px rgba($primary, 0.3);

      .step-circle {
        background: $color-white;
        color: $primary;
      }
    }

    &.completed {
      border-color: $color-success;
      
      .step-circle {
        background: $color-success;
        color: $color-white;
      }
    }

    .step-circle {
      width: 32px;
      height: 32px;
      border-radius: 50%;
      background: $light-1;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      font-size: 0.875rem;
    }

    .step-label {
      font-weight: 600;
      font-size: 0.875rem;
    }
  }
}

.step-content {
  max-width: 1400px;
  margin: 0 auto;
  background: $color-white;
  border-radius: 24px;
  padding: $spacer-xxl;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);

  h2 {
    font-size: 2rem;
    font-weight: 700;
    color: $dark;
    margin-bottom: 0.5rem;
  }

  .subtitle {
    color: $text-color-muted;
    font-size: 1.125rem;
    margin-bottom: 2rem;
  }
}

.upload-section {
  .upload-area {
    margin-bottom: 3rem;
  }

  .upload-zone {
    border: 3px dashed $primary;
    border-radius: 16px;
    padding: 3rem 2rem;
    background: rgba($primary, 0.05);
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;

    &:hover {
      border-color: darken($primary, 10%);
      background: rgba($primary, 0.1);
    }

    .upload-content {
      i {
        font-size: 3rem;
        color: $primary;
        margin-bottom: 1rem;
        display: block;
      }

      p {
        margin: 0.5rem 0;
        font-size: 1rem;

        &.subtitle {
          color: $text-color-muted;
          font-size: 0.875rem;
        }
      }

      .btn-primary {
        margin-top: 1rem;
      }
    }
  }

  .photos-count {
    margin-top: 1.5rem;
    padding: 1rem;
    background: rgba($color-success, 0.1);
    border: 2px solid $color-success;
    border-radius: 12px;
    text-align: center;

    p {
      margin: 0;
      color: $color-success;
      font-weight: 600;
      font-size: 1rem;
    }
  }

  .instrument-selector {
    margin-top: 2rem;
    padding-top: 2rem;
    border-top: 2px solid $light-2;

    h3 {
      font-size: 1.1rem;
      margin-bottom: 0.5rem;
    }

    p.subtitle {
      color: $text-color-muted;
      font-size: 0.875rem;
      margin-bottom: 1.5rem;
    }
  }

  .catalog-search {
    position: relative;
    margin-bottom: 2rem;

    input {
      width: 100%;
      padding: 1rem 3rem 1rem 1.5rem;
      border: 2px solid $light-3;
      border-radius: 16px;
      font-size: 1rem;
      transition: all 0.3s ease;

      &:focus {
        outline: none;
        border-color: $primary;
        box-shadow: 0 0 0 4px rgba($primary, 0.1);
      }
    }

    i {
      position: absolute;
      right: 1.5rem;
      top: 50%;
      transform: translateY(-50%);
      color: $text-color-muted;
    }
  }

  .instruments-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
  }

  .instrument-card {
    border: 2px solid $light-3;
    border-radius: 16px;
    overflow: hidden;
    cursor: pointer;
    transition: all 0.3s ease;
    background: $color-white;

    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
      border-color: $primary;
    }

    &.selected {
      border-color: $primary;
      box-shadow: 0 0 0 4px rgba($primary, 0.2);

      .card-info {
        background: $primary;
        color: $color-white;
      }
    }

    .card-image {
      width: 100%;
      height: 120px;
      background: $light-1;
      display: flex;
      align-items: center;
      justify-content: center;

      i {
        font-size: 2.5rem;
        color: $primary;
      }
    }

    .card-info {
      padding: 1rem;
      transition: all 0.3s ease;

      h4 {
        font-size: 1rem;
        font-weight: 700;
        margin: 0 0 0.25rem 0;
      }

      p {
        margin: 0;
        font-size: 0.875rem;
        opacity: 0.8;
      }
    }
  }

}

.components-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;

  .component-category {
    background: $light-1;
    padding: 1.5rem;
    border-radius: 16px;

    h3 {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      margin-bottom: 1rem;
      color: $dark;
    }
  }

  .component-checkboxes {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;

    .component-checkbox {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      cursor: pointer;

      input[type="checkbox"] {
        display: none;
      }

      .checkbox-custom {
        width: 20px;
        height: 20px;
        border: 2px solid $light-3;
        border-radius: 4px;
        position: relative;

        &::after {
          content: '';
          position: absolute;
          top: 2px;
          left: 6px;
          width: 4px;
          height: 8px;
          border: solid $color-white;
          border-width: 0 2px 2px 0;
          transform: rotate(45deg);
          opacity: 0;
        }
      }

      input:checked + .checkbox-custom {
        background: $primary;
        border-color: $primary;

        &::after {
          opacity: 1;
        }
      }

      .component-label {
        flex: 1;
        font-weight: 500;
      }

      .quantity-input {
        width: 80px;
        padding: 0.25rem;
        border: 1px solid $light-3;
        border-radius: 6px;
        font-size: 0.875rem;
      }
    }
  }
}

.markup-workspace {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 2rem;

  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
  }
}

.toolbar {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  gap: 0.5rem;

  .tool-group {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
  }

  .tool-btn {
    padding: 0.5rem 1rem;
    border: 2px solid $light-3;
    border-radius: 8px;
    background: $color-white;
    cursor: pointer;
    transition: all 0.2s ease;
    font-size: 0.875rem;

    &:hover {
      border-color: $primary;
      color: $primary;
    }

    &.active {
      background: $primary;
      color: $color-white;
      border-color: $primary;
    }

    &.danger {
      color: $color-danger;
      
      &:hover {
        border-color: $color-danger;
      }
    }
  }
}

.canvas-container {
  position: relative;
  border: 2px solid $light-3;
  border-radius: 12px;
  overflow: hidden;
  background: $light-1;
}

.markup-canvas {
  display: block;
  width: 100%;
  height: auto;
}

.markers-overlay {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.fault-marker-svg {
  pointer-events: all;
  cursor: pointer;

  .marker-dot {
    fill: $color-danger;
    stroke: rgba($color-black, 0.28);
    stroke-width: 1.4;
  }

  .marker-index {
    fill: $color-white;
    font-size: 9px;
    font-weight: 700;
    text-anchor: middle;
    dominant-baseline: middle;
    pointer-events: none;
  }

  .marker-remove-control {
    cursor: pointer;
  }

  .marker-remove-dot {
    fill: $color-danger;
    stroke: $color-white;
    stroke-width: 1.2;
  }

  .marker-remove-x {
    fill: $color-white;
    font-size: 8px;
    font-weight: 700;
    text-anchor: middle;
    dominant-baseline: middle;
    pointer-events: none;
  }
}

.markers-list {
  background: $light-1;
  padding: 1.5rem;
  border-radius: 12px;

  h4 {
    margin-bottom: 1rem;
    color: $dark;
  }

  .marker-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem;
    background: $color-white;
    border-radius: 8px;
    margin-bottom: 0.5rem;

    .marker-number {
      width: 24px;
      height: 24px;
      background: $primary;
      color: $color-white;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.75rem;
      font-weight: 700;
    }

    .marker-description {
      flex: 1;
      font-size: 0.875rem;
    }

    .btn-icon {
      background: none;
      border: none;
      cursor: pointer;
      color: $color-primary-dark;
    }
  }
}

.photo-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;

  .tab-btn {
    padding: 0.5rem 1rem;
    border: 2px solid $light-3;
    border-radius: 8px;
    background: $color-white;
    cursor: pointer;
    transition: all 0.2s ease;

    &.active {
      background: $primary;
      color: $color-white;
      border-color: $primary;
    }
  }
}

.disclaimer-box {
  display: flex;
  gap: 1rem;
  padding: 1.5rem;
  background: $color-warning-bg-legacy;
  border: 2px solid $color-warning-accent-legacy;
  border-radius: 12px;
  margin-bottom: 2rem;

  .disclaimer-icon {
    font-size: 2rem;
    color: $color-warning-accent-legacy;
  }
}

.disclaimer-checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1rem;
  font-weight: 600;
}

.diagnostic-summary {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;

  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
  }
}

.summary-card {
  background: $light-1;
  padding: 1.5rem;
  border-radius: 12px;

  .summary-item {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.5rem;
  }
}

.fault-breakdown {
  background: $light-1;
  padding: 1.5rem;
  border-radius: 12px;

  .fault-group {
    margin-bottom: 1rem;
  }

  .fault-group-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
  }

  .count-badge {
    background: $primary;
    color: $color-white;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 0.75rem;
  }
}

.quote-result {
  background: $light-1;
  padding: 1.5rem;
  border-radius: 12px;
  margin-top: 2rem;
  grid-column: 1 / -1;

  .quote-breakdown {
    margin-top: 1rem;
  }

  .quote-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.5rem;

    &.total {
      font-weight: 700;
      font-size: 1.25rem;
      border-top: 2px solid $light-3;
      padding-top: 0.5rem;
      margin-top: 1rem;
    }
  }

  .price {
    font-weight: 600;
    color: $primary;
  }

  .price-large {
    font-size: 1.5rem;
    color: $primary;
    font-weight: 800;
  }

  .time-estimate {
    margin-top: 1rem;
    color: $text-color-muted;
  }
}

.step-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 2rem;

  .btn-primary,
  .btn-secondary {
    padding: 0.75rem 2rem;
    border: none;
    border-radius: 12px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .btn-primary {
    background: $primary;
    color: $color-white;
  }

  .btn-secondary {
    background: $color-primary-dark;
    color: $color-white;
  }
}

.btn-large {
  padding: 1rem 2.5rem !important;
  font-size: 1rem;
}

.btn-primary {
  background: $primary;
  color: $color-white;
  border: none;
  border-radius: 12px;
  padding: 0.75rem 2rem;
  font-weight: 600;
  cursor: pointer;
}

.btn-secondary {
  background: $color-primary-dark;
  color: $color-white;
  border: none;
  border-radius: 12px;
  padding: 0.75rem 2rem;
  font-weight: 600;
  cursor: pointer;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.modal-content {
  background: $color-white;
  padding: 2rem;
  border-radius: 16px;
  text-align: center;
  max-width: 400px;
}

.success-icon {
  font-size: 3rem;
  color: $color-success;
  margin-bottom: 1rem;
}

.reference-code {
  margin-top: 1rem;
  background: $light-1;
  padding: 0.75rem;
  border-radius: 8px;
}

// Hide broken/missing images to prevent clutter
img:broken,
img[src=""]:not([alt]),
img[src*="undefined"] {
  display: none !important;
}

// Also hide images with 404 errors via onerror attribute
img.img-broken {
  display: none !important;
}

// Product Preview Section - Centrado y contenido
.product-preview {
  background: $color-white;
  border-radius: 16px;
  padding: $spacer-lg;
  margin: $spacer-lg 0;
  max-width: 920px;
  margin-left: auto;
  margin-right: auto;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);

  .product-header {
    display: flex;
    align-items: center;
    gap: $spacer-md;
    margin-bottom: $spacer-lg;
    padding-bottom: $spacer-md;
    border-bottom: 2px solid $light-2;

    .brand-logo {
      flex-shrink: 0;
      width: 80px;
      height: 80px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: $light-1;
      border-radius: 12px;
      padding: $spacer-sm;

      img {
        max-width: 100%;
        max-height: 100%;
        object-fit: contain;
      }
    }

    h3 {
      margin: 0;
      font-size: 1.25rem;
      font-weight: 600;
      color: $dark;
      flex: 1;
    }
  }

  .product-carousel {
    width: 100%;
    margin-bottom: $spacer-md;
    display: flex;
    justify-content: center;
    max-height: none;
  }

  .product-image {
    width: 100%;
    max-height: 600px;
    border-radius: 12px;
    background: $light-1;
    margin-bottom: $spacer-md;

    img {
      width: 100%;
      height: 100%;
      object-fit: contain;
      display: block;
      border-radius: 12px;
    }
  }

  .product-image-placeholder {
    width: 100%;
    height: 250px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: $light-1;
    border-radius: 12px;
    border: 2px dashed $light-3;
    margin-bottom: $spacer-md;
    color: $text-color-muted;

    i {
      font-size: 2.5rem;
      margin-bottom: $spacer-sm;
      color: $light-4;
    }

    p {
      margin: 0;
      font-size: 0.875rem;
    }
  }

  .product-variants {
    margin-top: $spacer-lg;
    padding-top: $spacer-lg;
    border-top: 2px solid $light-2;

    .variants-label {
      font-size: 0.875rem;
      font-weight: 600;
      color: $text-color-muted;
      margin-bottom: $spacer-md;
    }

    .variants-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
      gap: $spacer-sm;

      .variant-thumb {
        aspect-ratio: 1;
        border: 2px solid $light-3;
        border-radius: 8px;
        overflow: hidden;
        cursor: pointer;
        transition: all 0.2s ease;
        background: $light-1;

        img {
          width: 100%;
          height: 100%;
          object-fit: contain;
          display: block;
        }

        &:hover {
          border-color: $primary;
          transform: scale(1.05);
        }

        &.active {
          border-color: $primary;
          box-shadow: 0 0 0 3px rgba($primary, 0.1);
        }
      }
    }
  }
}
</style>
