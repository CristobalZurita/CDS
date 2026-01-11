<template>
  <div class="diagnostic-wizard">
    <!-- Step 1: Brand Selection (Dropdown A→Z) -->
    <div v-if="currentStep === 1" class="step-container">
      <h3 class="step-title">Paso 1: Selecciona la marca</h3>

      <div class="brand-select">
        <select v-model="selectedBrandLocal" @change="onBrandChange">
          <option value="">-- Selecciona una marca --</option>
          <option v-for="brand in allBrands" :key="brand.id" :value="brand.id">
            {{ brand.name }}
          </option>
        </select>
      </div>

      <button
        @click="nextStep"
        :disabled="!selectedBrandLocal"
        class="btn btn-next"
      >
        Continuar <i class="fas fa-arrow-right"></i>
      </button>
    </div>

    <!-- Step 2: Model Selection -->
    <div v-if="currentStep === 2" class="step-container">
      <h3 class="step-title">Paso 2: Selecciona el modelo</h3>
      <div class="back-button">
        <button @click="previousStep" class="btn-text">
          <i class="fas fa-arrow-left"></i> Volver
        </button>
      </div>

      <div v-if="allModels.length > 0" class="model-select">
        <select v-model="selectedModelLocal" @change="onModelChange">
          <option value="">-- Selecciona un modelo --</option>
          <option v-for="m in allModels" :key="m.id" :value="m.id">{{ m.model }}</option>
        </select>

        <div v-if="instrumentPreview" class="model-preview">
          <ImageView :src="instrumentPreview"
                     :alt="currentInstrument?.model || 'Instrument image'"
                     class="model-preview-image"
                     :spinner-enabled="true" />
          <div class="model-preview-info">
            <h4>{{ currentInstrument?.model || 'Cargando...' }}</h4>
            <p v-if="currentInstrument?.type">{{ currentInstrument.type }} ({{ currentInstrument?.year }})</p>
            <p v-if="currentInstrument?.description">{{ currentInstrument.description }}</p>
            <p><!-- Price display intentionally removed from UI --></p>
          </div>
        </div>
      </div>

      <div v-else class="empty-state">
        <p>No hay modelos registrados para esta marca aún.</p>
      </div>

      <button
        @click="nextStep"
        :disabled="!diagnostic.selectedModel.value"
        class="btn btn-next"
      >
        Continuar <i class="fas fa-arrow-right"></i>
      </button>
    </div>

    <!-- Step 3: Fault Selection -->
    <div v-if="currentStep === 3" class="step-container">
      <h3 class="step-title">Paso 3: Describe los problemas</h3>
      <div class="back-button">
        <button @click="previousStep" class="btn-text">
          <i class="fas fa-arrow-left"></i> Volver
        </button>
      </div>

      <div class="current-selection">
        <strong>{{ selectedBrandLocal ? catalog.getBrandById(selectedBrandLocal)?.name : 'Marca' }}</strong> →
        <strong>{{ currentInstrument?.model || 'Modelo' }}</strong>
      </div>

      <div v-if="availableFaults.length > 0" class="faults-container">
        <div class="warning-box" v-if="hasPrecedenceFault">
          <i class="fas fa-exclamation-circle"></i>
          <span>Se detectó una falla crítica. Las demás opciones serán ignoradas.</span>
        </div>

        <div
          v-for="fault in availableFaults"
          :key="fault.id"
          class="fault-item"
          :class="{
            disabled: hasPrecedenceFault && !isSelected(fault.id),
            critical: fault.category === 'critical'
          }"
        >
          <label class="fault-checkbox">
            <input
              type="checkbox"
              :value="fault.id"
              :checked="isSelected(fault.id)"
              @change="toggleFault(fault.id)"
              :disabled="hasPrecedenceFault && !isSelected(fault.id)"
            />
            <span class="checkmark"></span>
          </label>

          <div class="fault-info">
            <div class="fault-header">
              <i :class="`fas ${fault.icon}`"></i>
              <strong>{{ fault.name }}</strong>
            </div>
            <p class="fault-description">{{ fault.description }}</p>
              <p><!-- Price display removed for faults --></p>
          </div>
        </div>
      </div>

      <div v-else class="empty-state">
        <p>No hay fallas registradas para este modelo.</p>
      </div>

      <button
        @click="nextStep"
        :disabled="diagnostic.selectedFaults.value.length === 0"
        class="btn btn-next"
      >
        Continuar <i class="fas fa-arrow-right"></i>
      </button>
    </div>

    <!-- Step 4: Client Info -->
    <div v-if="currentStep === 4" class="step-container">
      <h3 class="step-title">Paso 4: Información de contacto</h3>
      <div class="back-button">
        <button @click="previousStep" class="btn-text">
          <i class="fas fa-arrow-left"></i> Volver
        </button>
      </div>

      <form @submit.prevent="nextStep" class="client-form">
        <div class="form-group">
          <label for="clientName">Nombre *</label>
          <input
            v-model="diagnostic.clientName.value"
            type="text"
            id="clientName"
            placeholder="Tu nombre completo"
            pattern="[A-Za-zÀ-ÿ\s]{2,50}"
            title="Solo letras y espacios, mínimo 2 caracteres"
            required
          />
          <small v-if="diagnostic.clientName.value && !diagnostic.validateName(diagnostic.clientName.value)" class="error-text">
            Solo se permiten letras y espacios (mínimo 2 caracteres)
          </small>
        </div>

        <div class="form-group">
          <label for="clientEmail">Email *</label>
          <input
            v-model="diagnostic.clientEmail.value"
            type="email"
            id="clientEmail"
            placeholder="tu@email.com"
            title="Ingresa un email válido"
            required
          />
          <small v-if="diagnostic.clientEmail.value && !diagnostic.validateEmail(diagnostic.clientEmail.value)" class="error-text">
            Email inválido (ej: usuario@dominio.com)
          </small>
        </div>

        <div class="form-group">
          <label for="clientPhone">Teléfono</label>
          <input
            v-model="diagnostic.clientPhone.value"
            type="tel"
            id="clientPhone"
            placeholder="+56912345678"
            pattern="^\+?[0-9]{8,15}$"
            title="Teléfono válido (8-15 dígitos, opcional +)"
          />
          <small v-if="diagnostic.clientPhone.value && !diagnostic.validatePhone(diagnostic.clientPhone.value)" class="error-text">
            Teléfono inválido (8-15 dígitos)
          </small>
        </div>

        <button type="submit" class="btn btn-next">
          Ver Cotización <i class="fas fa-arrow-right"></i>
        </button>
      </form>
    </div>

    <!-- Step 5: Quote Result -->
    <div v-if="currentStep === 5" class="step-container quote-result">
      <h3 class="step-title">Tu Cotización</h3>

      <div class="quote-summary">
        <div class="equipment-info">
          <h4>{{ catalog.getBrandById(selectedBrandLocal)?.name }} {{ currentInstrument?.model }}</h4>
            <p><!-- Price hidden by policy --></p>
        </div>

        <div class="faults-summary">
          <h5>Problemas detectados:</h5>
          <ul>
            <li v-for="faultId in diagnostic.getEffectiveFaults()" :key="faultId">
              {{ diagnostic.faults.value[faultId]?.name }}
                <p><!-- Price display removed for faults --></p>
            </li>
          </ul>
        </div>

        <div v-if="quoteData" class="pricing-breakdown">
            <p class="muted">Los detalles de coste no se muestran en esta interfaz. Consulta en taller para una cotización detallada.</p>
        </div>
        <div v-else class="quote-error">
          <i class="fas fa-exclamation-triangle"></i>
          <p>No se pudo calcular la cotización. Por favor, selecciona un modelo y al menos un problema.</p>
        </div>

        <div class="client-info-display">
          <p><strong>Nombre:</strong> {{ diagnostic.clientName.value }}</p>
          <p><strong>Email:</strong> {{ diagnostic.clientEmail.value }}</p>
          <p v-if="diagnostic.clientPhone.value">
            <strong>Teléfono:</strong> {{ diagnostic.clientPhone.value }}
          </p>
        </div>

        <div class="action-buttons">
          <button @click="submitQuote" class="btn btn-primary">
            <i class="fas fa-paper-plane"></i> Enviar Cotización
          </button>
          <button @click="downloadQuote" class="btn btn-secondary">
            <i class="fas fa-download"></i> Descargar PDF
          </button>
          <button @click="startOver" class="btn btn-outline">
            <i class="fas fa-redo"></i> Nueva Cotización
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import ImageView from "@/vue/components/generic/ImageView.vue"
import { useDiagnostic } from '@/composables/useDiagnostic'
import { useInstrumentsCatalog } from '@/composables/useInstrumentsCatalog'

const diagnostic = useDiagnostic()
const catalog = useInstrumentsCatalog()
const currentStep = ref(1)

// Local UI state
const selectedBrandLocal = ref('')
const selectedModelLocal = ref('')
const instrumentPreview = ref(null)
const currentInstrument = ref(null)

// Use catalog directly
const allBrands = computed(() => catalog.getAllBrands(true))

const allModels = computed(() => {
  return selectedBrandLocal.value 
    ? catalog.getInstrumentsByBrand(selectedBrandLocal.value)
    : []
})

const currentBrand = computed(() => {
  return catalog.getBrandById(selectedBrandLocal.value)
})

const availableFaults = computed(() => {
  return diagnostic.getAvailableFaults()
})

const hasPrecedenceFault = computed(() => {
  return diagnostic.selectedFaults.value.some(id => diagnostic.faults.value[id]?.isPrecedence)
})

const quoteData = computed(() => {
  return diagnostic.calculateQuote()
})

const formatPrice = (price) => {
  if (!price) return '0'
  return new Intl.NumberFormat('es-CL', {
    style: 'currency',
    currency: 'CLP',
    minimumFractionDigits: 0
  }).format(price).replace(/\s/g, '')
}

const selectBrand = (brandId) => {
  diagnostic.selectedBrand.value = brandId
  diagnostic.selectedModel.value = null
  diagnostic.clearFaults()
}

const selectModel = (instrumentId) => {
  diagnostic.selectedModel.value = instrumentId
  diagnostic.clearFaults()
}

const onBrandChange = () => {
  const bid = selectedBrandLocal.value
  diagnostic.selectedBrand.value = bid
  diagnostic.selectedModel.value = null
  selectedModelLocal.value = ''
  instrumentPreview.value = null
  currentInstrument.value = null
}

const onModelChange = async () => {
  const mid = selectedModelLocal.value
  if (!mid) {
    instrumentPreview.value = null
    currentInstrument.value = null
    return
  }
  
  // Get from catalog (no API call)
  const inst = catalog.getInstrumentById(mid)
  if (inst) {
    diagnostic.selectedModel.value = mid
    instrumentPreview.value = inst.imagePath
    currentInstrument.value = inst
  }
}

const isSelected = (faultId) => {
  return diagnostic.selectedFaults.value.includes(faultId)
}

const toggleFault = (faultId) => {
  if (isSelected(faultId)) {
    diagnostic.removeFault(faultId)
  } else {
    diagnostic.addFault(faultId)
  }
}

const nextStep = () => {
  // Validar datos en paso 4 antes de ir a 5
  if (currentStep.value === 4) {
    if (!diagnostic.validateName(diagnostic.clientName.value)) {
      alert('Por favor, ingresa un nombre válido (solo letras, mínimo 2 caracteres)')
      return
    }
    if (!diagnostic.validateEmail(diagnostic.clientEmail.value)) {
      alert('Por favor, ingresa un email válido')
      return
    }
    if (!diagnostic.validatePhone(diagnostic.clientPhone.value)) {
      alert('Por favor, ingresa un teléfono válido (opcional, pero si lo colocas debe ser válido)')
      return
    }
  }

  if (currentStep.value < 5) {
    currentStep.value++
  }
}

const previousStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

const startOver = () => {
  diagnostic.reset()
  currentStep.value = 1
}

const submitQuote = () => {
  const data = diagnostic.getQuoteData()
  
  if (!data || !data.client) {
    alert('Error: No hay datos de cotización válidos')
    return
  }

  // Simulate API call
  alert(`✓ Cotización enviada a ${data.client.email}\n\nNos pondremos en contacto pronto.`)
  console.log('Quote submitted:', data)
  
  // Optional: Reset form or show success message
  // diagnostic.reset()
  // currentStep.value = 1
}

const downloadQuote = () => {
  const data = diagnostic.getQuoteData()
  
  if (!data || !data.client) {
    alert('Error: No hay datos de cotización para descargar')
    return
  }

  // Generate simple CSV for now (TODO: Generate PDF)
  const csv = `
COTIZACIÓN - CIRUJANO DE SINTETIZADORES
========================================

CLIENTE:
Nombre: ${data.client.clientName}
Email: ${data.client.clientEmail}
Teléfono: ${data.client.clientPhone || 'No proporcionado'}

EQUIPO:
Marca: ${data.quote.brand.name}
Modelo: ${data.quote.instrument.model}

PROBLEMAS DETECTADOS:
${data.quote.faults.map(f => `- ${f.name}: $${f.basePrice}`).join('\n')}

COTIZACIÓN:
Subtotal: $${data.quote.baseCost}
Factor complejidad (${data.quote.brand.tier}): ${data.quote.complexityFactor}x
Factor valor equipo: ${data.quote.valueFactor}x
TOTAL: $${data.quote.finalCost}

Válida por: 30 días
Fecha: ${new Date().toLocaleDateString('es-CL')}
  `.trim()

  // Download as text file
  const blob = new Blob([csv], { type: 'text/plain' })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `cotizacion-${data.client.clientName.replace(/\\s+/g, '-')}.txt`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)

  console.log('Quote downloaded:', data)
}
</script>

<style scoped lang="scss">
@import '@/scss/variables';

.diagnostic-wizard {
  padding: 3rem 2rem;

  .step-container {
    max-width: 800px;
    margin: 0 auto;
    animation: fadeIn 0.3s ease;
  }

  .step-title {
    font-size: $text-4;
    font-weight: 700;
    color: $dark;
    margin-bottom: 2rem;
    text-align: center;
  }

  .back-button {
    margin-bottom: 2rem;

    .btn-text {
      background: none;
      border: none;
      color: $primary;
      cursor: pointer;
      font-size: 0.95rem;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      transition: color 0.3s ease;

      &:hover {
        color: darken($primary, 15%);
      }
    }
  }

  // Brand Grid
  .brand-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;

    @media (max-width: 768px) {
      grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
      gap: 0.75rem;
    }
  }

  .brand-select {
    margin-bottom: 1.5rem;

    select {
      width: 100%;
      padding: 0.75rem;
      border: 2px solid #ddd;
      border-radius: 6px;
      font-size: 0.95rem;
    }
  }

  .model-select {
    margin-bottom: 1.5rem;

    select {
      width: 100%;
      padding: 0.75rem;
      border: 2px solid #ddd;
      border-radius: 6px;
      font-size: 0.95rem;
      margin-bottom: 1rem;
    }

    .model-preview {
      display: flex;
      gap: 1rem;
      align-items: center;

      img {
        width: 180px;
        height: auto;
        border-radius: 8px;
        border: 1px solid #eee;
        object-fit: contain;
        background: #fafafa;
      }

      .model-preview-info {
        flex: 1;
      }
    }
  }

  .brand-card {
    padding: 1.5rem 1rem;
    border: 2px solid #ddd;
    border-radius: 8px;
    background: white;
    cursor: pointer;
    transition: all 0.3s ease;
    text-align: center;

    &:hover {
      border-color: $primary;
      box-shadow: 0 4px 12px rgba($primary, 0.2);
    }

    &.active {
      border-color: $primary;
      background: rgba($primary, 0.05);
      box-shadow: 0 4px 16px rgba($primary, 0.3);
    }

    .brand-tier {
      font-size: 0.7rem;
      text-transform: uppercase;
      font-weight: 700;
      letter-spacing: 0.5px;
      padding: 0.25rem 0.5rem;
      border-radius: 4px;
      display: inline-block;
      margin-bottom: 0.5rem;

      &[data-tier='legendary'] {
        background: #ffd700;
        color: #333;
      }

      &[data-tier='professional'] {
        background: #c0c0c0;
        color: #333;
      }

      &[data-tier='standard'] {
        background: #cd7f32;
        color: white;
      }

      &[data-tier='specialized'] {
        background: $primary;
        color: white;
      }

      &[data-tier='boutique'] {
        background: $dark;
        color: white;
      }

      &[data-tier='historic'] {
        background: #666;
        color: white;
      }
    }

    .brand-name {
      font-size: 0.9rem;
      font-weight: 700;
      color: $dark;
      margin: 0.5rem 0;
    }

    .brand-year {
      font-size: 0.75rem;
      color: #999;
    }
  }

  // Model List
  .model-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin-bottom: 2rem;
  }

  .model-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem;
    border: 2px solid #ddd;
    border-radius: 8px;
    background: white;
    cursor: pointer;
    transition: all 0.3s ease;
    text-align: left;

    &:hover {
      border-color: $primary;
      box-shadow: 0 4px 12px rgba($primary, 0.2);
    }

    &.active {
      border-color: $primary;
      background: rgba($primary, 0.05);
    }

    .model-info {
      flex: 1;

      h4 {
        margin: 0 0 0.25rem 0;
        color: $dark;
        font-size: 1.1rem;
      }

      .model-type {
        margin: 0 0 0.5rem 0;
        font-size: 0.85rem;
        color: #999;
      }

      .model-description {
        margin: 0;
        font-size: 0.9rem;
        color: #666;
      }
    }

    .model-price {
      display: flex;
      flex-direction: column;
      align-items: flex-end;
      gap: 0.25rem;
      margin-left: 1rem;

      .label {
        font-size: 0.75rem;
        color: #999;
      }

      .price {
        font-size: 1.1rem;
        font-weight: 700;
        color: $primary;
      }
    }
  }

  // Faults Container
  .faults-container {
    margin-bottom: 2rem;
  }

  .warning-box {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    background: #fff3cd;
    border: 2px solid #ffc107;
    border-radius: 6px;
    margin-bottom: 1.5rem;
    font-size: 0.95rem;
    color: #856404;

    i {
      font-size: 1.3rem;
      flex-shrink: 0;
    }
  }

  .fault-item {
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    padding: 1rem;
    border: 1px solid #ddd;
    border-radius: 6px;
    margin-bottom: 1rem;
    transition: all 0.3s ease;

    &:hover:not(.disabled) {
      border-color: $primary;
      background: rgba($primary, 0.02);
    }

    &.disabled {
      opacity: 0.5;
      pointer-events: none;
    }

    &.critical {
      border-color: #ffc107;
      background: rgba(#ffc107, 0.05);
    }

    .fault-checkbox {
      display: flex;
      align-items: center;
      margin-top: 0.25rem;
      cursor: pointer;
      position: relative;

      input {
        display: none;

        &:checked ~ .checkmark {
          background: $primary;
          border-color: $primary;

          &::after {
            display: block;
          }
        }
      }

      .checkmark {
        width: 20px;
        height: 20px;
        border: 2px solid #ddd;
        border-radius: 4px;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s ease;

        &::after {
          content: '';
          display: none;
          width: 4px;
          height: 8px;
          border: solid white;
          border-width: 0 2px 2px 0;
          transform: rotate(45deg);
        }
      }
    }

    .fault-info {
      flex: 1;

      .fault-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.5rem;

        i {
          color: $primary;
          font-size: 1.1rem;
        }

        strong {
          color: $dark;
          font-size: 0.95rem;
        }
      }

      .fault-description {
        margin: 0 0 0.5rem 0;
        font-size: 0.9rem;
        color: #666;
      }

      .fault-price {
        display: inline-block;
        font-size: 0.85rem;
        font-weight: 600;
        color: $primary;
      }
    }
  }

  // Client Form
  .client-form {
    margin-bottom: 2rem;
  }

  .form-group {
    margin-bottom: 1.5rem;

    label {
      display: block;
      margin-bottom: 0.5rem;
      font-weight: 600;
      color: $dark;
      font-size: 0.95rem;
    }

    input {
      width: 100%;
      padding: 0.75rem;
      border: 2px solid #ddd;
      border-radius: 6px;
      font-size: 0.95rem;
      transition: border-color 0.3s ease;

      &:focus {
        outline: none;
        border-color: $primary;
        box-shadow: 0 0 0 3px rgba($primary, 0.1);
      }

      &::placeholder {
        color: #999;
      }

      &:invalid:not(:placeholder-shown) {
        border-color: #dc3545;
      }
    }

    .error-text {
      display: block;
      margin-top: 0.25rem;
      color: #dc3545;
      font-size: 0.85rem;
      font-style: italic;
    }
  }

  // Quote Result
  .quote-result {
    .quote-summary {
      background: white;
      border: 2px solid #ddd;
      border-radius: 12px;
      padding: 2rem;
      margin-bottom: 2rem;
    }

    .equipment-info {
      margin-bottom: 2rem;
      padding-bottom: 2rem;
      border-bottom: 2px solid #eee;

      h4 {
        margin: 0 0 0.5rem 0;
        font-size: 1.3rem;
        color: $dark;
      }

      .equipment-value {
        margin: 0;
        font-size: 0.9rem;
        color: #666;
      }
    }

    .faults-summary {
      margin-bottom: 2rem;
      padding-bottom: 2rem;
      border-bottom: 2px solid #eee;

      h5 {
        margin: 0 0 1rem 0;
        color: $dark;
        font-size: 0.95rem;
      }

      ul {
        list-style: none;
        padding: 0;
        margin: 0;

        li {
          padding: 0.5rem 0;
          color: #666;
          font-size: 0.9rem;
          display: flex;
          justify-content: space-between;

          .fault-base-price {
            font-weight: 600;
            color: $primary;
          }
        }
      }
    }

    .pricing-breakdown {
      margin-bottom: 2rem;
      padding: 1.5rem;
      background: rgba($primary, 0.05);
      border-radius: 8px;

      .price-row {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.75rem;
        font-size: 0.95rem;
        color: #666;

        &.total {
          margin-top: 1rem;
          padding-top: 1rem;
          border-top: 2px solid rgba($primary, 0.2);
          font-weight: 700;
          color: $dark;
          font-size: 1.1rem;

          .total-price {
            color: $primary;
            font-size: 1.3rem;
          }
        }
      }
    }

    .quote-error {
      margin-bottom: 2rem;
      padding: 1.5rem;
      background: #fff3cd;
      border: 2px solid #ffc107;
      border-radius: 8px;
      display: flex;
      align-items: center;
      gap: 1rem;

      i {
        font-size: 1.5rem;
        color: #ff9800;
      }

      p {
        margin: 0;
        color: #333;
        font-size: 0.95rem;
      }
    }

    .client-info-display {
      margin-bottom: 2rem;
      padding: 1rem;
      background: #f5f5f5;
      border-radius: 6px;

      p {
        margin: 0.5rem 0;
        font-size: 0.9rem;

        strong {
          color: $dark;
        }
      }
    }

    .action-buttons {
      display: flex;
      gap: 1rem;
      flex-wrap: wrap;

      @media (max-width: 600px) {
        flex-direction: column;
      }
    }
  }

  // Buttons
  .btn {
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 6px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    text-transform: uppercase;
    font-size: 0.9rem;
    letter-spacing: 0.5px;

    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    &.btn-next {
      background: $primary;
      color: white;
      width: 100%;

      &:hover:not(:disabled) {
        background: darken($primary, 10%);
        box-shadow: 0 4px 12px rgba($primary, 0.3);
      }
    }

    &.btn-primary {
      background: $primary;
      color: white;
      flex: 1;

      &:hover {
        background: darken($primary, 10%);
      }
    }

    &.btn-secondary {
      background: $dark;
      color: white;
      flex: 1;

      &:hover {
        background: darken($dark, 10%);
      }
    }

    &.btn-outline {
      background: white;
      color: $primary;
      border: 2px solid $primary;
      flex: 1;

      &:hover {
        background: rgba($primary, 0.05);
      }
    }
  }

  .current-selection {
    padding: 1rem;
    background: rgba($primary, 0.05);
    border-left: 4px solid $primary;
    border-radius: 4px;
    margin-bottom: 1.5rem;
    font-size: 0.95rem;
    color: $dark;
  }

  .empty-state {
    padding: 2rem;
    text-align: center;
    color: #999;
    font-size: 1rem;
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
