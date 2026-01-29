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
        <h2>Selecciona tu instrumento o sube fotos</h2>
        
        <div class="instrument-selector">
          <div class="catalog-search">
            <input 
              v-model="searchQuery"
              type="text"
              placeholder="Busca por marca o modelo..."
              @input="filterInstruments"
            />
            <i class="fas fa-search"></i>
          </div>

          <div v-if="filteredInstruments.length > 0" class="instruments-grid">
            <div 
              v-for="inst in filteredInstruments"
              :key="inst.id"
              class="instrument-card"
              :class="{ selected: selectedInstrument?.id === inst.id }"
              @click="selectInstrument(inst)"
            >
              <img :src="inst.image" :alt="inst.name" />
              <div class="card-info">
                <h4>{{ inst.brand }}</h4>
                <p>{{ inst.model }}</p>
              </div>
            </div>
          </div>
        </div>

        <div class="divider">
          <span>O</span>
        </div>

        <div class="upload-zone" @drop.prevent="handleDrop" @dragover.prevent>
          <input 
            ref="fileInput"
            type="file"
            multiple
            accept="image/*"
            @change="handleFileUpload"
            style="display: none"
          />
          <div class="upload-placeholder" @click="$refs.fileInput.click()">
            <i class="fas fa-cloud-upload-alt"></i>
            <p>Arrastra fotos aquí o haz clic para seleccionar</p>
            <small>Necesitamos: Vista frontal, trasera, y cenital (desde arriba)</small>
          </div>

          <div v-if="uploadedPhotos.length > 0" class="photo-preview-grid">
            <div 
              v-for="(photo, idx) in uploadedPhotos"
              :key="idx"
              class="photo-preview"
            >
              <img :src="photo.url" :alt="`Foto ${idx + 1}`" />
              <button class="remove-btn" @click="removePhoto(idx)">
                <i class="fas fa-times"></i>
              </button>
              <select v-model="photo.view" class="view-selector">
                <option value="front">Frontal</option>
                <option value="back">Trasera</option>
                <option value="top">Cenital</option>
                <option value="detail">Detalle</option>
              </select>
            </div>
          </div>
        </div>

        <button 
          class="btn-primary btn-large"
          :disabled="!canProceed"
          @click="nextStep"
        >
          Continuar <i class="fas fa-arrow-right"></i>
        </button>
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
              @dblclick="addMarker"
              @mousemove="updateCursor"
            ></canvas>
            
            <div 
              v-for="(marker, idx) in currentPhotoMarkers"
              :key="idx"
              class="fault-marker"
              :class="`marker-${marker.type}`"
              :style="{ left: marker.x + 'px', top: marker.y + 'px' }"
              @click="editMarker(marker, idx)"
            >
              <div class="marker-icon">
                <i :class="getFaultIcon(marker.type)"></i>
              </div>
              <div class="marker-label">{{ idx + 1 }}</div>
              <button class="marker-remove" @click.stop="removeMarker(idx)">
                <i class="fas fa-times"></i>
              </button>
            </div>
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
                {{ selectedInstrument.brand }} {{ selectedInstrument.model }}
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

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'

// Steps
const steps = ['Selección', 'Componentes', 'Marcado', 'Cotización']
const currentStep = ref(0)

// Step 1: Instrument Selection
const searchQuery = ref('')
const selectedInstrument = ref(null)
const uploadedPhotos = ref([])
const fileInput = ref(null)

// Mock instrument catalog
const instrumentCatalog = ref([
  { id: 1, brand: 'Moog', model: 'Minimoog Model D', image: '/api/placeholder/300/200' },
  { id: 2, brand: 'Roland', model: 'Jupiter-8', image: '/api/placeholder/300/200' },
  { id: 3, brand: 'Korg', model: 'MS-20', image: '/api/placeholder/300/200' },
  { id: 4, brand: 'Sequential', model: 'Prophet-5', image: '/api/placeholder/300/200' },
  { id: 5, brand: 'Yamaha', model: 'DX7', image: '/api/placeholder/300/200' },
])

const filteredInstruments = ref([...instrumentCatalog.value])

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
  return selectedInstrument.value !== null || uploadedPhotos.value.length >= 2
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
const filterInstruments = () => {
  const query = searchQuery.value.toLowerCase()
  if (!query) {
    filteredInstruments.value = [...instrumentCatalog.value]
  } else {
    filteredInstruments.value = instrumentCatalog.value.filter(inst => 
      inst.brand.toLowerCase().includes(query) || 
      inst.model.toLowerCase().includes(query)
    )
  }
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
  if (!markupCanvas.value || !uploadedPhotos.value[activePhotoIndex.value]) return
  
  const canvas = markupCanvas.value
  const container = canvasContainer.value
  const photo = uploadedPhotos.value[activePhotoIndex.value]
  
  const img = new Image()
  img.onload = () => {
    // Set canvas size to match image
    canvas.width = img.width
    canvas.height = img.height
    
    // Scale to fit container
    const containerWidth = container.clientWidth
    const scale = containerWidth / img.width
    canvas.style.width = containerWidth + 'px'
    canvas.style.height = (img.height * scale) + 'px'
    
    // Draw image
    const ctx = canvas.getContext('2d')
    ctx.drawImage(img, 0, 0)
  }
  img.src = photo.url
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

const updateCursor = (event) => {
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

const editMarker = (marker, index) => {
  // Optional: Open edit modal for marker
}

const focusMarker = (photoIndex, markerIndex) => {
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

onMounted(() => {
  // Initialize
})
</script>

<style lang="scss" scoped>
// Design variables - Bold, technical aesthetic
$primary: #FF6B35;
$secondary: #004E89;
$accent: #F7B32B;
$dark: #1A1A2E;
$danger: #E63946;
$success: #06D6A0;

$bg-light: #F8F9FA;
$bg-card: #FFFFFF;
$border: #E0E0E0;
$text-primary: #2D3436;
$text-secondary: #636E72;

.interactive-diagnostic {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 2rem;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
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
    background: white;
    border-radius: 100px;
    border: 2px solid $border;
    transition: all 0.3s ease;

    &.active {
      border-color: $primary;
      background: linear-gradient(135deg, $primary 0%, darken($primary, 10%) 100%);
      color: white;
      box-shadow: 0 4px 12px rgba($primary, 0.3);

      .step-circle {
        background: white;
        color: $primary;
      }
    }

    &.completed {
      border-color: $success;
      
      .step-circle {
        background: $success;
        color: white;
      }
    }

    .step-circle {
      width: 32px;
      height: 32px;
      border-radius: 50%;
      background: $bg-light;
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
  background: white;
  border-radius: 24px;
  padding: 3rem;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);

  h2 {
    font-size: 2rem;
    font-weight: 700;
    color: $dark;
    margin-bottom: 0.5rem;
  }

  .subtitle {
    color: $text-secondary;
    font-size: 1.125rem;
    margin-bottom: 2rem;
  }
}

// Step 1: Upload Section
.upload-section {
  .catalog-search {
    position: relative;
    margin-bottom: 2rem;

    input {
      width: 100%;
      padding: 1rem 3rem 1rem 1.5rem;
      border: 2px solid $border;
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
      color: $text-secondary;
    }
  }

  .instruments-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;

    .instrument-card {
      border: 2px solid $border;
      border-radius: 16px;
      overflow: hidden;
      cursor: pointer;
      transition: all 0.3s ease;
      background: white;

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
          color: white;
        }
      }

      img {
        width: 100%;
        height: 180px;
        object-fit: cover;
        background: $bg-light;
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

  .divider {
    text-align: center;
    margin: 2rem 0;
    position: relative;

    &::before,
    &::after {
      content: '';
      position: absolute;
      top: 50%;
      width: 45%;
      height: 1px;
      background: $border;
    }

    &::before { left: 0; }
    &::after { right: 0; }

    span {
      background: white;
      padding: 0 1rem;
      color: $text-secondary;
      font-weight: 600;
    }
  }

  .upload-zone {
    .upload-placeholder {
      border: 3px dashed $border;
      border-radius: 16px;
      padding: 3rem;
      text-align: center;
      cursor: pointer;
      transition: all 0.3s ease;
      background: $bg-light;

      &:hover {
        border-color: $primary;
        background: rgba($primary, 0.05);
      }

      i {
        font-size: 3rem;
        color: $primary;
        margin-bottom: 1rem;
      }

      p {
        font-size: 1.125rem;
        font-weight: 600;
        margin: 0.5rem 0;
        color: $text-primary;
      }

      small {
        color: $text-secondary;
      }
    }

    .photo-preview-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
      gap: 1rem;
      margin-top: 1.5rem;

      .photo-preview {
        position: relative;
        border-radius: 12px;
        overflow: hidden;
        border: 2px solid $border;

        img {
          width: 100%;
          height: 150px;
          object-fit: cover;
        }

        .remove-btn {
          position: absolute;
          top: 0.5rem;
          right: 0.5rem;
          width: 32px;
          height: 32px;
          border-radius: 50%;
          border: none;
          background: $danger;
          color: white;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s ease;

          &:hover {
            transform: scale(1.1);
            box-shadow: 0 4px 12px rgba($danger, 0.4);
          }
        }

        .view-selector {
          position: absolute;
          bottom: 0.5rem;
          left: 0.5rem;
          right: 0.5rem;
          padding: 0.5rem;
          border: none;
          border-radius: 8px;
          background: rgba(white, 0.95);
          font-size: 0.75rem;
          font-weight: 600;
        }
      }
    }
  }
}

// Step 2: Components Template
.template-section {
  .components-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    margin-bottom: 2rem;

    .component-category {
      background: $bg-light;
      border-radius: 16px;
      padding: 1.5rem;

      h3 {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        font-size: 1.125rem;
        font-weight: 700;
        color: $dark;
        margin: 0 0 1rem 0;

        i {
          color: $primary;
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
          padding: 0.75rem;
          background: white;
          border-radius: 12px;
          cursor: pointer;
          transition: all 0.2s ease;

          &:hover {
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
          }

          input[type="checkbox"] {
            display: none;

            &:checked + .checkbox-custom {
              background: $primary;
              border-color: $primary;

              &::after {
                opacity: 1;
              }
            }
          }

          .checkbox-custom {
            width: 24px;
            height: 24px;
            border: 2px solid $border;
            border-radius: 6px;
            position: relative;
            transition: all 0.2s ease;
            flex-shrink: 0;

            &::after {
              content: '✓';
              position: absolute;
              top: 50%;
              left: 50%;
              transform: translate(-50%, -50%);
              color: white;
              font-weight: 700;
              opacity: 0;
              transition: opacity 0.2s ease;
            }
          }

          .component-label {
            flex: 1;
            font-weight: 500;
            color: $text-primary;

            small {
              color: $text-secondary;
              margin-left: 0.5rem;
            }
          }

          .quantity-input {
            width: 80px;
            padding: 0.5rem;
            border: 2px solid $border;
            border-radius: 8px;
            font-size: 0.875rem;
            text-align: center;

            &:focus {
              outline: none;
              border-color: $primary;
            }
          }
        }
      }
    }
  }
}

// Step 3: Markup Section
.markup-section {
  .photo-tabs {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1.5rem;
    overflow-x: auto;

    .tab-btn {
      padding: 0.75rem 1.5rem;
      border: 2px solid $border;
      border-radius: 12px;
      background: white;
      cursor: pointer;
      transition: all 0.3s ease;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      font-weight: 600;
      white-space: nowrap;

      &:hover {
        border-color: $primary;
      }

      &.active {
        background: $primary;
        border-color: $primary;
        color: white;
      }

      i {
        font-size: 0.875rem;
      }
    }
  }

  .markup-workspace {
    display: grid;
    grid-template-columns: 1fr 320px;
    gap: 2rem;
    margin-bottom: 2rem;

    @media (max-width: 1024px) {
      grid-template-columns: 1fr;
    }

    .toolbar {
      grid-column: 1 / -1;
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 1rem;
      background: $bg-light;
      border-radius: 12px;
      gap: 1rem;
      flex-wrap: wrap;

      .tool-group {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
      }

      .tool-btn {
        padding: 0.75rem 1rem;
        border: 2px solid $border;
        border-radius: 10px;
        background: white;
        cursor: pointer;
        transition: all 0.2s ease;
        font-size: 0.875rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 0.5rem;

        &:hover {
          border-color: $primary;
          transform: translateY(-2px);
        }

        &.active {
          background: $primary;
          border-color: $primary;
          color: white;
          box-shadow: 0 4px 12px rgba($primary, 0.3);
        }

        &.danger {
          border-color: $danger;
          color: $danger;

          &:hover {
            background: $danger;
            color: white;
          }
        }

        i {
          font-size: 1rem;
        }
      }

      .tool-actions {
        display: flex;
        gap: 0.5rem;
      }
    }

    .canvas-container {
      position: relative;
      background: $bg-light;
      border-radius: 16px;
      overflow: hidden;
      min-height: 400px;
      display: flex;
      align-items: center;
      justify-content: center;

      canvas {
        max-width: 100%;
        height: auto;
        cursor: crosshair;
        display: block;
      }

      .fault-marker {
        position: absolute;
        transform: translate(-50%, -50%);
        z-index: 10;
        animation: markerPulse 2s infinite;

        .marker-icon {
          width: 48px;
          height: 48px;
          border-radius: 50%;
          background: white;
          border: 3px solid;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 1.25rem;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
          transition: all 0.2s ease;

          &:hover {
            transform: scale(1.1);
          }
        }

        .marker-label {
          position: absolute;
          top: -8px;
          right: -8px;
          width: 24px;
          height: 24px;
          border-radius: 50%;
          background: $dark;
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 0.75rem;
          font-weight: 700;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        }

        .marker-remove {
          position: absolute;
          bottom: -8px;
          left: 50%;
          transform: translateX(-50%);
          width: 24px;
          height: 24px;
          border-radius: 50%;
          border: none;
          background: $danger;
          color: white;
          cursor: pointer;
          opacity: 0;
          transition: opacity 0.2s ease;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 0.75rem;
        }

        &:hover .marker-remove {
          opacity: 1;
        }

        &.marker-broken .marker-icon {
          border-color: $danger;
          color: $danger;
        }

        &.marker-missing .marker-icon {
          border-color: #9B59B6;
          color: #9B59B6;
        }

        &.marker-loose .marker-icon {
          border-color: $accent;
          color: $accent;
        }

        &.marker-noisy .marker-icon {
          border-color: $secondary;
          color: $secondary;
        }

        &.marker-stuck .marker-icon {
          border-color: #E67E22;
          color: #E67E22;
        }

        &.marker-oxidized .marker-icon {
          border-color: #16A085;
          color: #16A085;
        }
      }
    }

    .markers-list {
      background: $bg-light;
      border-radius: 16px;
      padding: 1.5rem;
      max-height: 600px;
      overflow-y: auto;

      h4 {
        font-size: 1rem;
        font-weight: 700;
        margin: 0 0 1rem 0;
        color: $dark;
      }

      .marker-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.75rem;
        background: white;
        border-radius: 10px;
        margin-bottom: 0.5rem;
        transition: all 0.2s ease;

        &:hover {
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        }

        .marker-number {
          width: 28px;
          height: 28px;
          border-radius: 50%;
          background: $dark;
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 0.75rem;
          font-weight: 700;
          flex-shrink: 0;
        }

        i {
          font-size: 1rem;
          flex-shrink: 0;
        }

        .marker-description {
          flex: 1;
          font-size: 0.875rem;
          color: $text-primary;
        }

        .btn-icon {
          width: 32px;
          height: 32px;
          border-radius: 8px;
          border: none;
          background: $primary;
          color: white;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s ease;

          &:hover {
            transform: scale(1.1);
          }
        }
      }
    }
  }
}

// Step 4: Review Section
.review-section {
  .disclaimer-box {
    display: flex;
    gap: 1.5rem;
    padding: 2rem;
    background: linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 100%);
    border-left: 4px solid $accent;
    border-radius: 16px;
    margin-bottom: 2rem;

    .disclaimer-icon {
      font-size: 2.5rem;
      color: $accent;
    }

    .disclaimer-content {
      flex: 1;

      h3 {
        font-size: 1.25rem;
        margin: 0 0 1rem 0;
        color: $dark;
      }

      p {
        margin: 0 0 1rem 0;
        color: $text-primary;
      }

      ul {
        margin: 0 0 1rem 0;
        padding-left: 1.5rem;
        color: $text-primary;

        li {
          margin-bottom: 0.5rem;
        }
      }

      .disclaimer-checkbox {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 1rem;
        background: white;
        border-radius: 12px;
        cursor: pointer;
        font-weight: 600;

        input {
          width: 20px;
          height: 20px;
          cursor: pointer;
        }
      }
    }
  }

  .diagnostic-summary {
    display: grid;
    gap: 2rem;

    .summary-card,
    .fault-breakdown,
    .quote-result {
      background: $bg-light;
      border-radius: 16px;
      padding: 2rem;

      h3 {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        font-size: 1.25rem;
        font-weight: 700;
        margin: 0 0 1.5rem 0;
        color: $dark;

        i {
          color: $primary;
        }
      }
    }

    .summary-item {
      display: flex;
      justify-content: space-between;
      padding: 1rem 0;
      border-bottom: 1px solid $border;

      &:last-child {
        border-bottom: none;
      }

      strong {
        color: $text-primary;
      }

      span {
        color: $text-secondary;
        font-weight: 600;
      }
    }

    .fault-group {
      margin-bottom: 1.5rem;

      .fault-group-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 1rem;
        background: white;
        border-radius: 12px;
        margin-bottom: 0.75rem;
        font-weight: 600;

        i {
          font-size: 1.25rem;
        }

        span {
          flex: 1;
        }

        .count-badge {
          width: 28px;
          height: 28px;
          border-radius: 50%;
          background: $primary;
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 0.875rem;
        }
      }

      .fault-list {
        padding-left: 3rem;
        list-style: disc;

        li {
          padding: 0.5rem 0;
          color: $text-secondary;
        }
      }
    }

    .quote-breakdown {
      .quote-row {
        display: flex;
        justify-content: space-between;
        padding: 1rem 0;
        border-bottom: 1px solid $border;
        font-size: 1rem;

        .price {
          font-weight: 600;
          color: $text-primary;
        }

        &.subtotal {
          font-weight: 600;
          font-size: 1.125rem;
        }

        &.total {
          border-bottom: none;
          padding-top: 1.5rem;
          margin-top: 1rem;
          border-top: 2px solid $border;
          font-size: 1.25rem;
          font-weight: 700;

          .price-large {
            font-size: 2rem;
            color: $primary;
          }
        }
      }

      .time-estimate {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 1rem;
        background: rgba($secondary, 0.1);
        border-radius: 12px;
        margin-top: 1.5rem;
        font-weight: 600;
        color: $secondary;

        i {
          font-size: 1.25rem;
        }
      }
    }

    .quote-actions {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1rem;
      margin-top: 2rem;

      @media (max-width: 768px) {
        grid-template-columns: 1fr;
      }
    }
  }
}

// Buttons
.btn-primary,
.btn-secondary {
  padding: 1rem 2rem;
  border: none;
  border-radius: 12px;
  font-weight: 700;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.btn-primary {
  background: linear-gradient(135deg, $primary 0%, darken($primary, 10%) 100%);
  color: white;
  box-shadow: 0 4px 12px rgba($primary, 0.3);

  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba($primary, 0.4);
  }

  &.btn-large {
    width: 100%;
    padding: 1.25rem 2rem;
    font-size: 1.125rem;
  }
}

.btn-secondary {
  background: white;
  color: $dark;
  border: 2px solid $border;

  &:hover {
    border-color: $primary;
    color: $primary;
  }
}

.step-actions {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  margin-top: 2rem;

  @media (max-width: 768px) {
    flex-direction: column;
  }
}

// Modal
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 2rem;
  animation: fadeIn 0.3s ease;
}

.modal-content {
  background: white;
  border-radius: 24px;
  padding: 3rem;
  max-width: 500px;
  width: 100%;
  text-align: center;
  animation: slideUp 0.3s ease;

  &.success-modal {
    .success-icon {
      font-size: 4rem;
      color: $success;
      margin-bottom: 1.5rem;
    }

    h2 {
      font-size: 1.75rem;
      font-weight: 700;
      margin: 0 0 1rem 0;
      color: $dark;
    }

    p {
      color: $text-secondary;
      margin: 0.5rem 0;
    }

    .reference-code {
      margin: 2rem 0;
      padding: 1.5rem;
      background: $bg-light;
      border-radius: 12px;

      strong {
        display: block;
        margin-bottom: 0.5rem;
        color: $text-primary;
      }

      code {
        font-size: 1.5rem;
        font-weight: 700;
        color: $primary;
        font-family: 'Courier New', monospace;
      }
    }

    .btn-primary {
      margin-top: 1rem;
    }
  }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes markerPulse {
  0%, 100% {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  }
  50% {
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
  }
}
</style>
