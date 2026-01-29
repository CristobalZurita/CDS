<template>
  <div class="technician-dashboard">
    <div class="dashboard-header">
      <h1>🔧 Panel de Técnico</h1>
      <div class="stats-row">
        <div class="stat-card">
          <i class="fas fa-inbox"></i>
          <div class="stat-info">
            <span class="stat-value">{{ pendingCount }}</span>
            <span class="stat-label">Pendientes</span>
          </div>
        </div>
        <div class="stat-card">
          <i class="fas fa-clock"></i>
          <div class="stat-info">
            <span class="stat-value">{{ inProgressCount }}</span>
            <span class="stat-label">En proceso</span>
          </div>
        </div>
        <div class="stat-card">
          <i class="fas fa-check-circle"></i>
          <div class="stat-info">
            <span class="stat-value">{{ completedCount }}</span>
            <span class="stat-label">Completados</span>
          </div>
        </div>
      </div>
    </div>

    <div class="dashboard-tabs">
      <button 
        class="tab-btn"
        :class="{ active: activeTab === 'diagnostics' }"
        @click="activeTab = 'diagnostics'"
      >
        <i class="fas fa-list"></i>
        Diagnósticos
      </button>
      <button 
        class="tab-btn"
        :class="{ active: activeTab === 'templates' }"
        @click="activeTab = 'templates'"
      >
        <i class="fas fa-layer-group"></i>
        Templates
      </button>
      <button 
        class="tab-btn"
        :class="{ active: activeTab === 'new-template' }"
        @click="activeTab = 'new-template'"
      >
        <i class="fas fa-plus"></i>
        Nuevo Template
      </button>
    </div>

    <!-- Diagnostics List -->
    <div v-if="activeTab === 'diagnostics'" class="tab-content">
      <div class="diagnostics-header">
        <h2>Diagnósticos recibidos</h2>
        <div class="filters">
          <select v-model="filterStatus" class="filter-select">
            <option value="all">Todos los estados</option>
            <option value="pending">Pendientes</option>
            <option value="reviewed">Revisados</option>
            <option value="approved">Aprobados</option>
            <option value="completed">Completados</option>
          </select>
          <input 
            v-model="searchQuery"
            type="text"
            placeholder="Buscar por código..."
            class="search-input"
          />
        </div>
      </div>

      <div class="diagnostics-grid">
        <div 
          v-for="diag in filteredDiagnostics"
          :key="diag.id"
          class="diagnostic-card"
          @click="selectDiagnostic(diag)"
        >
          <div class="card-header">
            <span class="reference-code">{{ diag.reference_code }}</span>
            <span class="status-badge" :class="`status-${diag.status}`">
              {{ getStatusLabel(diag.status) }}
            </span>
          </div>

          <div class="card-body">
            <div class="instrument-info">
              <i class="fas fa-keyboard"></i>
              <span v-if="diag.instrument">
                {{ diag.instrument.brand }} {{ diag.instrument.model }}
              </span>
              <span v-else class="custom">Instrumento personalizado</span>
            </div>

            <div class="diagnostic-summary">
              <div class="summary-item">
                <i class="fas fa-camera"></i>
                <span>{{ diag.photos?.length || 0 }} fotos</span>
              </div>
              <div class="summary-item">
                <i class="fas fa-exclamation-triangle"></i>
                <span>{{ getTotalMarkers(diag) }} fallas</span>
              </div>
              <div class="summary-item">
                <i class="fas fa-calendar"></i>
                <span>{{ formatDate(diag.created_at) }}</span>
              </div>
            </div>

            <div v-if="diag.quote" class="quote-preview">
              <strong>Total:</strong>
              <span class="price">{{ formatPrice(diag.quote.total) }}</span>
            </div>
          </div>

          <div class="card-actions">
            <button class="btn-icon" @click.stop="viewDiagnostic(diag)">
              <i class="fas fa-eye"></i>
            </button>
            <button class="btn-icon" @click.stop="editQuote(diag)">
              <i class="fas fa-edit"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Templates Manager -->
    <div v-if="activeTab === 'templates'" class="tab-content">
      <div class="templates-header">
        <h2>Gestión de Templates</h2>
        <input 
          v-model="templateSearch"
          type="text"
          placeholder="Buscar template..."
          class="search-input"
        />
      </div>

      <div class="templates-grid">
        <div 
          v-for="template in filteredTemplates"
          :key="template.id"
          class="template-card"
        >
          <div class="template-image">
            <img 
              :src="template.front_photo_url || '/placeholder.jpg'"
              :alt="template.model"
            />
          </div>

          <div class="template-info">
            <h3>{{ template.brand }} {{ template.model }}</h3>
            <div class="template-meta">
              <span class="tier-badge" :class="`tier-${template.complexity_tier}`">
                {{ template.complexity_tier }}
              </span>
              <span class="year">{{ template.year || 'N/A' }}</span>
            </div>

            <div class="template-components">
              <div 
                v-for="(count, comp) in template.template_json"
                :key="comp"
                class="component-tag"
              >
                {{ comp }}: {{ count }}
              </div>
            </div>

            <div class="template-actions">
              <button class="btn-secondary" @click="editTemplate(template)">
                <i class="fas fa-edit"></i>
                Editar
              </button>
              <button class="btn-secondary" @click="viewTemplatePhotos(template)">
                <i class="fas fa-images"></i>
                Fotos
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- New Template Creator -->
    <div v-if="activeTab === 'new-template'" class="tab-content">
      <div class="template-creator">
        <h2>Crear Nuevo Template</h2>

        <form @submit.prevent="saveTemplate" class="template-form">
          <div class="form-section">
            <h3>Información Básica</h3>
            
            <div class="form-row">
              <div class="form-group">
                <label>Marca *</label>
                <input 
                  v-model="newTemplate.brand"
                  type="text"
                  required
                  placeholder="Ej: Moog, Roland, Korg..."
                />
              </div>

              <div class="form-group">
                <label>Modelo *</label>
                <input 
                  v-model="newTemplate.model"
                  type="text"
                  required
                  placeholder="Ej: Minimoog Model D"
                />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>Año</label>
                <input 
                  v-model.number="newTemplate.year"
                  type="number"
                  min="1900"
                  max="2025"
                />
              </div>

              <div class="form-group">
                <label>Tipo</label>
                <select v-model="newTemplate.type">
                  <option value="">Seleccionar...</option>
                  <option value="Analog Synthesizer">Sintetizador Analógico</option>
                  <option value="Digital Synthesizer">Sintetizador Digital</option>
                  <option value="Drum Machine">Caja de Ritmos</option>
                  <option value="Sampler">Sampler</option>
                  <option value="Workstation">Workstation</option>
                  <option value="Modular">Modular</option>
                </select>
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>Valor Estimado (CLP)</label>
                <input 
                  v-model.number="newTemplate.estimated_value"
                  type="number"
                  step="10000"
                />
              </div>

              <div class="form-group">
                <label>Nivel de Complejidad</label>
                <select v-model="newTemplate.complexity_tier" required>
                  <option value="simple">Simple</option>
                  <option value="standard">Estándar</option>
                  <option value="complex">Complejo</option>
                  <option value="vintage">Vintage</option>
                </select>
              </div>
            </div>
          </div>

          <div class="form-section">
            <h3>Fotos de Referencia</h3>
            
            <div class="photo-upload-grid">
              <div class="photo-upload-item">
                <label>Vista Frontal</label>
                <input 
                  ref="frontPhotoInput"
                  type="file"
                  accept="image/*"
                  @change="handlePhotoUpload($event, 'front')"
                  style="display: none"
                />
                <div 
                  class="upload-box"
                  :class="{ 'has-image': newTemplate.frontPhoto }"
                  @click="$refs.frontPhotoInput.click()"
                >
                  <img v-if="newTemplate.frontPhoto" :src="newTemplate.frontPhoto" />
                  <div v-else class="upload-placeholder">
                    <i class="fas fa-upload"></i>
                    <span>Subir foto</span>
                  </div>
                </div>
                <button 
                  v-if="newTemplate.frontPhoto"
                  type="button"
                  class="detect-btn"
                  @click="detectControls('front')"
                >
                  <i class="fas fa-magic"></i>
                  Detectar controles
                </button>
              </div>

              <div class="photo-upload-item">
                <label>Vista Trasera</label>
                <input 
                  ref="backPhotoInput"
                  type="file"
                  accept="image/*"
                  @change="handlePhotoUpload($event, 'back')"
                  style="display: none"
                />
                <div 
                  class="upload-box"
                  :class="{ 'has-image': newTemplate.backPhoto }"
                  @click="$refs.backPhotoInput.click()"
                >
                  <img v-if="newTemplate.backPhoto" :src="newTemplate.backPhoto" />
                  <div v-else class="upload-placeholder">
                    <i class="fas fa-upload"></i>
                    <span>Subir foto</span>
                  </div>
                </div>
              </div>

              <div class="photo-upload-item">
                <label>Vista Cenital</label>
                <input 
                  ref="topPhotoInput"
                  type="file"
                  accept="image/*"
                  @change="handlePhotoUpload($event, 'top')"
                  style="display: none"
                />
                <div 
                  class="upload-box"
                  :class="{ 'has-image': newTemplate.topPhoto }"
                  @click="$refs.topPhotoInput.click()"
                >
                  <img v-if="newTemplate.topPhoto" :src="newTemplate.topPhoto" />
                  <div v-else class="upload-placeholder">
                    <i class="fas fa-upload"></i>
                    <span>Subir foto</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="form-section">
            <h3>Mapa de Componentes</h3>
            <p class="help-text">
              Ingresa la cantidad de cada tipo de componente que tiene el instrumento
            </p>

            <div class="components-editor">
              <div 
                v-for="category in componentCategories"
                :key="category.name"
                class="component-category-editor"
              >
                <h4>{{ category.name }}</h4>
                <div class="component-inputs">
                  <div 
                    v-for="comp in category.components"
                    :key="comp.id"
                    class="component-input"
                  >
                    <label>{{ comp.name }}</label>
                    <input 
                      v-model.number="newTemplate.components[comp.id]"
                      type="number"
                      min="0"
                      max="200"
                      placeholder="0"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="form-actions">
            <button type="button" class="btn-secondary" @click="resetTemplate">
              <i class="fas fa-times"></i>
              Cancelar
            </button>
            <button type="submit" class="btn-primary">
              <i class="fas fa-save"></i>
              Guardar Template
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Diagnostic Detail Modal -->
    <div v-if="selectedDiagnostic" class="modal-overlay" @click="selectedDiagnostic = null">
      <div class="modal-content diagnostic-detail" @click.stop>
        <button class="modal-close" @click="selectedDiagnostic = null">
          <i class="fas fa-times"></i>
        </button>

        <div class="detail-header">
          <h2>{{ selectedDiagnostic.reference_code }}</h2>
          <select v-model="selectedDiagnostic.status" @change="updateStatus" class="status-select">
            <option value="pending">Pendiente</option>
            <option value="reviewed">Revisado</option>
            <option value="approved">Aprobado</option>
            <option value="completed">Completado</option>
          </select>
        </div>

        <div class="detail-sections">
          <div class="detail-section">
            <h3>Cliente</h3>
            <div class="info-grid">
              <div class="info-item">
                <strong>Nombre:</strong>
                <span>{{ selectedDiagnostic.customer_name || 'N/A' }}</span>
              </div>
              <div class="info-item">
                <strong>Email:</strong>
                <span>{{ selectedDiagnostic.customer_email || 'N/A' }}</span>
              </div>
              <div class="info-item">
                <strong>Teléfono:</strong>
                <span>{{ selectedDiagnostic.customer_phone || 'N/A' }}</span>
              </div>
            </div>
          </div>

          <div class="detail-section">
            <h3>Instrumento</h3>
            <div v-if="selectedDiagnostic.instrument" class="instrument-detail">
              <p>
                <strong>{{ selectedDiagnostic.instrument.brand }} {{ selectedDiagnostic.instrument.model }}</strong>
              </p>
              <p>Año: {{ selectedDiagnostic.instrument.year }}</p>
              <p>Tipo: {{ selectedDiagnostic.instrument.type }}</p>
            </div>
            <div v-else>
              <p>{{ selectedDiagnostic.custom_instrument_description || 'Instrumento personalizado' }}</p>
            </div>
          </div>

          <div class="detail-section">
            <h3>Fotos con Marcadores</h3>
            <div class="photo-gallery">
              <div 
                v-for="(photo, idx) in selectedDiagnostic.photos"
                :key="idx"
                class="photo-item"
              >
                <img :src="photo.photo_url" :alt="`Vista ${photo.view_type}`" />
                <div class="photo-overlay">
                  <span class="view-label">{{ photo.view_type }}</span>
                  <span class="markers-count">{{ photo.markers?.length || 0 }} marcas</span>
                </div>
              </div>
            </div>
          </div>

          <div class="detail-section">
            <h3>Cotización</h3>
            <div v-if="selectedDiagnostic.quote" class="quote-detail">
              <div class="quote-row">
                <span>Diagnóstico base:</span>
                <span>{{ formatPrice(selectedDiagnostic.quote.base_diagnostic_fee) }}</span>
              </div>
              <div class="quote-row">
                <span>Reparaciones:</span>
                <span>{{ formatPrice(selectedDiagnostic.quote.repair_cost) }}</span>
              </div>
              <div class="quote-row">
                <span>Ajuste complejidad:</span>
                <span>{{ formatPrice(selectedDiagnostic.quote.complexity_adjustment) }}</span>
              </div>
              <div class="quote-row total">
                <strong>Total:</strong>
                <strong>{{ formatPrice(selectedDiagnostic.quote.total) }}</strong>
              </div>
              <div class="time-estimate">
                <i class="fas fa-clock"></i>
                Tiempo estimado: {{ selectedDiagnostic.quote.estimated_days }} días
              </div>
            </div>
            
            <div class="quote-actions">
              <button class="btn-primary" @click="adjustQuote">
                <i class="fas fa-edit"></i>
                Ajustar cotización
              </button>
              <button class="btn-secondary" @click="sendQuoteToCustomer">
                <i class="fas fa-paper-plane"></i>
                Enviar al cliente
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// State
const activeTab = ref('diagnostics')
const diagnostics = ref([])
const templates = ref([])
const selectedDiagnostic = ref(null)
const filterStatus = ref('all')
const searchQuery = ref('')
const templateSearch = ref('')

// New template state
const newTemplate = ref({
  brand: '',
  model: '',
  year: null,
  type: '',
  estimated_value: null,
  complexity_tier: 'standard',
  frontPhoto: null,
  backPhoto: null,
  topPhoto: null,
  components: {}
})

const componentCategories = [
  {
    name: 'Teclas',
    components: [
      { id: 'keys', name: 'Número de teclas' },
      { id: 'keybed', name: 'Lecho de teclas' },
      { id: 'aftertouch', name: 'Aftertouch' },
    ]
  },
  {
    name: 'Controles',
    components: [
      { id: 'knobs', name: 'Perillas' },
      { id: 'sliders', name: 'Deslizantes' },
      { id: 'buttons', name: 'Botones' },
      { id: 'switches', name: 'Interruptores' },
    ]
  },
  {
    name: 'Conectividad',
    components: [
      { id: 'audio_out', name: 'Salidas audio' },
      { id: 'audio_in', name: 'Entradas audio' },
      { id: 'midi', name: 'MIDI' },
      { id: 'cv_gate', name: 'CV/Gate' },
      { id: 'usb', name: 'USB' },
    ]
  },
  {
    name: 'Otros',
    components: [
      { id: 'display', name: 'Display' },
      { id: 'power', name: 'Fuente poder' },
      { id: 'pedals', name: 'Pedales' },
      { id: 'wheels', name: 'Ruedas' },
    ]
  }
]

// Computed
const pendingCount = computed(() => {
  return diagnostics.value.filter(d => d.status === 'pending').length
})

const inProgressCount = computed(() => {
  return diagnostics.value.filter(d => ['reviewed', 'approved'].includes(d.status)).length
})

const completedCount = computed(() => {
  return diagnostics.value.filter(d => d.status === 'completed').length
})

const filteredDiagnostics = computed(() => {
  let filtered = diagnostics.value

  if (filterStatus.value !== 'all') {
    filtered = filtered.filter(d => d.status === filterStatus.value)
  }

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(d => 
      d.reference_code.toLowerCase().includes(query)
    )
  }

  return filtered
})

const filteredTemplates = computed(() => {
  if (!templateSearch.value) return templates.value

  const query = templateSearch.value.toLowerCase()
  return templates.value.filter(t => 
    t.brand.toLowerCase().includes(query) ||
    t.model.toLowerCase().includes(query)
  )
})

// Methods
const loadDiagnostics = async () => {
  // Mock data - replace with API call
  diagnostics.value = [
    {
      id: 1,
      reference_code: 'DIAG-ABC123',
      status: 'pending',
      instrument: {
        brand: 'Moog',
        model: 'Minimoog Model D',
        year: 1970,
        type: 'Analog Synthesizer'
      },
      customer_name: 'Juan Pérez',
      customer_email: 'juan@email.com',
      customer_phone: '+56912345678',
      photos: [
        { photo_url: '/placeholder.jpg', view_type: 'front', markers: [{}, {}, {}] },
        { photo_url: '/placeholder.jpg', view_type: 'back', markers: [{}] }
      ],
      quote: {
        base_diagnostic_fee: 25000,
        repair_cost: 45000,
        complexity_adjustment: 15000,
        total: 85000,
        estimated_days: 5
      },
      created_at: new Date().toISOString()
    }
  ]
}

const loadTemplates = async () => {
  // Mock data - replace with API call
  templates.value = [
    {
      id: 1,
      brand: 'Moog',
      model: 'Minimoog Model D',
      year: 1970,
      complexity_tier: 'vintage',
      front_photo_url: '/placeholder.jpg',
      template_json: {
        keys: 44,
        knobs: 24,
        switches: 18,
        wheels: 2
      }
    }
  ]
}

const selectDiagnostic = (diag) => {
  selectedDiagnostic.value = diag
}

const getTotalMarkers = (diag) => {
  if (!diag.photos) return 0
  return diag.photos.reduce((sum, photo) => sum + (photo.markers?.length || 0), 0)
}

const getStatusLabel = (status) => {
  const labels = {
    pending: 'Pendiente',
    reviewed: 'Revisado',
    approved: 'Aprobado',
    completed: 'Completado'
  }
  return labels[status] || status
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('es-CL')
}

const formatPrice = (price) => {
  return new Intl.NumberFormat('es-CL', {
    style: 'currency',
    currency: 'CLP',
    minimumFractionDigits: 0
  }).format(price)
}

const viewDiagnostic = (diag) => {
  selectedDiagnostic.value = diag
}

const editQuote = (diag) => {
  selectedDiagnostic.value = diag
  // Focus on quote section
}

const updateStatus = async () => {
  // API call to update status
  console.log('Updating status:', selectedDiagnostic.value.status)
}

const adjustQuote = () => {
  // Open quote editor
  alert('Abriendo editor de cotización...')
}

const sendQuoteToCustomer = () => {
  // Send email to customer
  alert('Enviando cotización al cliente...')
}

const editTemplate = (template) => {
  // Load template for editing
  console.log('Editing template:', template)
}

const viewTemplatePhotos = (template) => {
  // Show photo gallery
  console.log('Viewing photos:', template)
}

const handlePhotoUpload = (event, view) => {
  const file = event.target.files[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = (e) => {
      if (view === 'front') newTemplate.value.frontPhoto = e.target.result
      if (view === 'back') newTemplate.value.backPhoto = e.target.result
      if (view === 'top') newTemplate.value.topPhoto = e.target.result
    }
    reader.readAsDataURL(file)
  }
}

const detectControls = async (view) => {
  // Call OpenCV detection API
  alert('Detectando controles con OpenCV... (funcionalidad simulada)')
  // API call would return detected controls
}

const saveTemplate = async () => {
  // Validate and save
  console.log('Saving template:', newTemplate.value)
  alert('Template guardado exitosamente')
  resetTemplate()
  activeTab.value = 'templates'
}

const resetTemplate = () => {
  newTemplate.value = {
    brand: '',
    model: '',
    year: null,
    type: '',
    estimated_value: null,
    complexity_tier: 'standard',
    frontPhoto: null,
    backPhoto: null,
    topPhoto: null,
    components: {}
  }
}

onMounted(() => {
  loadDiagnostics()
  loadTemplates()
})
</script>

<style lang="scss" scoped>
$primary: #FF6B35;
$secondary: #004E89;
$success: #06D6A0;
$warning: #F7B32B;
$danger: #E63946;
$dark: #1A1A2E;
$bg: #F8F9FA;

.technician-dashboard {
  min-height: 100vh;
  background: $bg;
  padding: 2rem;
}

.dashboard-header {
  margin-bottom: 2rem;

  h1 {
    font-size: 2.5rem;
    font-weight: 800;
    color: $dark;
    margin-bottom: 1.5rem;
  }
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;

  .stat-card {
    background: white;
    padding: 1.5rem;
    border-radius: 16px;
    display: flex;
    align-items: center;
    gap: 1rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);

    i {
      font-size: 2rem;
      color: $primary;
    }

    .stat-info {
      display: flex;
      flex-direction: column;

      .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: $dark;
      }

      .stat-label {
        font-size: 0.875rem;
        color: #6C757D;
      }
    }
  }
}

.dashboard-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;

  .tab-btn {
    padding: 1rem 1.5rem;
    border: none;
    background: white;
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-weight: 600;

    &:hover {
      background: rgba($primary, 0.1);
    }

    &.active {
      background: $primary;
      color: white;
    }
  }
}

.tab-content {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.diagnostics-header,
.templates-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;

  h2 {
    font-size: 1.5rem;
    font-weight: 700;
    color: $dark;
  }

  .filters {
    display: flex;
    gap: 1rem;

    .filter-select,
    .search-input {
      padding: 0.75rem 1rem;
      border: 2px solid #E0E0E0;
      border-radius: 10px;
      font-size: 0.875rem;

      &:focus {
        outline: none;
        border-color: $primary;
      }
    }

    .search-input {
      min-width: 250px;
    }
  }
}

.diagnostics-grid,
.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.diagnostic-card {
  border: 2px solid #E0E0E0;
  border-radius: 12px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    border-color: $primary;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;

    .reference-code {
      font-weight: 700;
      font-size: 1.125rem;
      color: $dark;
    }

    .status-badge {
      padding: 0.5rem 1rem;
      border-radius: 100px;
      font-size: 0.75rem;
      font-weight: 600;

      &.status-pending {
        background: rgba($warning, 0.2);
        color: darken($warning, 20%);
      }

      &.status-reviewed {
        background: rgba($secondary, 0.2);
        color: $secondary;
      }

      &.status-approved {
        background: rgba($success, 0.2);
        color: darken($success, 20%);
      }

      &.status-completed {
        background: rgba(#6C757D, 0.2);
        color: #6C757D;
      }
    }
  }

  .card-body {
    .instrument-info {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      margin-bottom: 1rem;
      font-weight: 600;

      i {
        color: $primary;
      }

      .custom {
        font-style: italic;
        color: #6C757D;
      }
    }

    .diagnostic-summary {
      display: flex;
      flex-wrap: wrap;
      gap: 1rem;
      margin-bottom: 1rem;

      .summary-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.875rem;
        color: #6C757D;

        i {
          color: $primary;
        }
      }
    }

    .quote-preview {
      display: flex;
      justify-content: space-between;
      padding: 1rem;
      background: rgba($primary, 0.1);
      border-radius: 8px;

      .price {
        font-size: 1.25rem;
        font-weight: 700;
        color: $primary;
      }
    }
  }

  .card-actions {
    display: flex;
    gap: 0.5rem;
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid #E0E0E0;

    .btn-icon {
      width: 40px;
      height: 40px;
      border: none;
      border-radius: 8px;
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

.template-card {
  border: 2px solid #E0E0E0;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;

  &:hover {
    border-color: $primary;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }

  .template-image {
    height: 200px;
    background: $bg;

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
  }

  .template-info {
    padding: 1.5rem;

    h3 {
      font-size: 1.125rem;
      font-weight: 700;
      margin-bottom: 0.5rem;
    }

    .template-meta {
      display: flex;
      gap: 0.5rem;
      margin-bottom: 1rem;

      .tier-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 100px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;

        &.tier-simple {
          background: rgba($success, 0.2);
          color: darken($success, 20%);
        }

        &.tier-standard {
          background: rgba($secondary, 0.2);
          color: $secondary;
        }

        &.tier-complex {
          background: rgba($warning, 0.2);
          color: darken($warning, 20%);
        }

        &.tier-vintage {
          background: rgba($danger, 0.2);
          color: $danger;
        }
      }

      .year {
        color: #6C757D;
        font-size: 0.875rem;
      }
    }

    .template-components {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
      margin-bottom: 1rem;

      .component-tag {
        padding: 0.5rem 0.75rem;
        background: $bg;
        border-radius: 8px;
        font-size: 0.75rem;
        font-weight: 600;
      }
    }

    .template-actions {
      display: flex;
      gap: 0.5rem;
    }
  }
}

// Template Creator
.template-creator {
  max-width: 1200px;
  margin: 0 auto;

  h2 {
    font-size: 1.75rem;
    font-weight: 700;
    margin-bottom: 2rem;
  }

  .form-section {
    margin-bottom: 2rem;

    h3 {
      font-size: 1.25rem;
      font-weight: 700;
      margin-bottom: 1.5rem;
      color: $dark;
    }

    .help-text {
      color: #6C757D;
      margin-bottom: 1rem;
    }
  }

  .form-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    margin-bottom: 1.5rem;
  }

  .form-group {
    label {
      display: block;
      font-weight: 600;
      margin-bottom: 0.5rem;
      color: $dark;
    }

    input,
    select {
      width: 100%;
      padding: 0.75rem 1rem;
      border: 2px solid #E0E0E0;
      border-radius: 10px;
      font-size: 1rem;

      &:focus {
        outline: none;
        border-color: $primary;
      }
    }
  }

  .photo-upload-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;

    .photo-upload-item {
      label {
        display: block;
        font-weight: 600;
        margin-bottom: 0.5rem;
      }

      .upload-box {
        height: 200px;
        border: 2px dashed #E0E0E0;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.3s ease;
        overflow: hidden;

        &:hover {
          border-color: $primary;
        }

        &.has-image {
          border-style: solid;
        }

        img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }

        .upload-placeholder {
          text-align: center;

          i {
            font-size: 2rem;
            color: #6C757D;
            margin-bottom: 0.5rem;
          }

          span {
            display: block;
            color: #6C757D;
          }
        }
      }

      .detect-btn {
        margin-top: 0.5rem;
        width: 100%;
        padding: 0.75rem;
        border: none;
        background: $secondary;
        color: white;
        border-radius: 8px;
        cursor: pointer;
        font-weight: 600;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;

        &:hover {
          background: darken($secondary, 10%);
        }
      }
    }
  }

  .components-editor {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;

    .component-category-editor {
      background: $bg;
      padding: 1.5rem;
      border-radius: 12px;

      h4 {
        font-size: 1rem;
        font-weight: 700;
        margin-bottom: 1rem;
      }

      .component-inputs {
        display: flex;
        flex-direction: column;
        gap: 1rem;

        .component-input {
          label {
            display: block;
            font-size: 0.875rem;
            margin-bottom: 0.25rem;
            color: #6C757D;
          }

          input {
            width: 100%;
            padding: 0.5rem;
            border: 2px solid #E0E0E0;
            border-radius: 8px;

            &:focus {
              outline: none;
              border-color: $primary;
            }
          }
        }
      }
    }
  }

  .form-actions {
    display: flex;
    gap: 1rem;
    justify-content: flex-end;
    margin-top: 2rem;
  }
}

// Buttons
.btn-primary,
.btn-secondary {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
}

.btn-primary {
  background: $primary;
  color: white;

  &:hover {
    background: darken($primary, 10%);
  }
}

.btn-secondary {
  background: white;
  color: $dark;
  border: 2px solid #E0E0E0;

  &:hover {
    border-color: $primary;
    color: $primary;
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
  overflow-y: auto;
}

.modal-content {
  background: white;
  border-radius: 24px;
  padding: 2rem;
  max-width: 1200px;
  width: 100%;
  position: relative;
  max-height: 90vh;
  overflow-y: auto;

  .modal-close {
    position: absolute;
    top: 1rem;
    right: 1rem;
    width: 40px;
    height: 40px;
    border: none;
    border-radius: 50%;
    background: $danger;
    color: white;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;

    &:hover {
      transform: scale(1.1);
    }
  }

  .detail-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 2px solid #E0E0E0;

    h2 {
      font-size: 1.75rem;
      font-weight: 700;
    }

    .status-select {
      padding: 0.5rem 1rem;
      border: 2px solid $primary;
      border-radius: 8px;
      font-weight: 600;
      color: $primary;
      cursor: pointer;
    }
  }

  .detail-sections {
    display: grid;
    gap: 2rem;

    .detail-section {
      h3 {
        font-size: 1.25rem;
        font-weight: 700;
        margin-bottom: 1rem;
      }

      .info-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;

        .info-item {
          display: flex;
          flex-direction: column;
          gap: 0.25rem;

          strong {
            color: #6C757D;
            font-size: 0.875rem;
          }

          span {
            font-size: 1rem;
            color: $dark;
          }
        }
      }

      .photo-gallery {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 1rem;

        .photo-item {
          position: relative;
          border-radius: 12px;
          overflow: hidden;
          border: 2px solid #E0E0E0;

          img {
            width: 100%;
            height: 150px;
            object-fit: cover;
          }

          .photo-overlay {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            padding: 0.75rem;
            background: linear-gradient(to top, rgba(0, 0, 0, 0.8), transparent);
            color: white;
            display: flex;
            justify-content: space-between;
            font-size: 0.875rem;
            font-weight: 600;
          }
        }
      }

      .quote-detail {
        background: $bg;
        padding: 1.5rem;
        border-radius: 12px;

        .quote-row {
          display: flex;
          justify-content: space-between;
          padding: 0.75rem 0;
          border-bottom: 1px solid #E0E0E0;

          &.total {
            margin-top: 1rem;
            padding-top: 1rem;
            border-top: 2px solid #E0E0E0;
            border-bottom: none;
            font-size: 1.25rem;
          }
        }

        .time-estimate {
          margin-top: 1rem;
          padding: 1rem;
          background: rgba($secondary, 0.1);
          border-radius: 8px;
          display: flex;
          align-items: center;
          gap: 0.5rem;
          color: $secondary;
          font-weight: 600;
        }
      }

      .quote-actions {
        display: flex;
        gap: 1rem;
        margin-top: 1rem;
      }
    }
  }
}
</style>
