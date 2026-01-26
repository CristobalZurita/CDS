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
@import '@/scss/_core.scss';

.diagnostic-wizard {
  padding: $spacer-xxl $spacer-xl;
  font-size: $text-base;
  line-height: $lh-relaxed;

  .step-container {
    max-width: 800px;
    margin: 0 auto;
    animation: fadeIn 0.3s ease;
  }

  .step-title {
    font-size: $h3-size;
    font-weight: $fw-bold;
    color: $dark;
    margin-bottom: $spacer-xl;
    text-align: center;
  }

  .back-button {
    margin-bottom: $spacer-xl;

    .btn-text {
      background: none;
      border: none;
      color: $primary;
      cursor: pointer;
      font-size: $text-base;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: $spacer-xs;
      transition: $transition-base;

      &:hover {
        color: darken($primary, 15%);
      }
    }
  }

  // Brand Grid
  .brand-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: $spacer-md;
    margin-bottom: $spacer-xl;

    @include media-breakpoint-down(md) {
      grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
      gap: $spacer-sm;
    }
  }

  .brand-select {
    margin-bottom: $spacer-lg;

    select {
      width: 100%;
      padding: $spacer-sm;
      border: 2px solid $light-3;
      border-radius: $border-radius-md;
      font-size: $text-base;
    }
  }

  .model-select {
    margin-bottom: $spacer-lg;

    select {
      width: 100%;
      padding: $spacer-sm;
      border: 2px solid $light-3;
      border-radius: $border-radius-md;
      font-size: $text-base;
      margin-bottom: $spacer-md;
    }

    .model-preview {
      display: flex;
      gap: $spacer-md;
      align-items: center;

      img {
        width: 180px;
        height: auto;
        border-radius: $border-radius-md;
        border: 1px solid $light-2;
        object-fit: contain;
        background: $light-1;
      }

      .model-preview-info {
        flex: 1;
      }
    }
  }

  .brand-card {
    padding: $spacer-lg $spacer-md;
    border: 2px solid $light-3;
    border-radius: $border-radius-md;
    background: white;
    cursor: pointer;
    transition: $transition-base;
    text-align: center;

    &:hover {
      border-color: $primary;
      box-shadow: $shadow-md;
    }

    &.active {
      border-color: $primary;
      background: rgba($primary, 0.05);
      box-shadow: $shadow-lg;
    }

    .brand-tier {
      font-size: $text-2xs;
      text-transform: uppercase;
      font-weight: $fw-bold;
      letter-spacing: $ls-wider;
      padding: $spacer-xs $spacer-sm;
      border-radius: $border-radius-sm;
      display: inline-block;
      margin-bottom: $spacer-xs;

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
      font-size: $text-sm;
      font-weight: $fw-bold;
      color: $dark;
      margin: $spacer-xs 0;
    }

    .brand-year {
      font-size: $text-2xs;
      color: $text-color-muted;
    }
  }

  // Model List
  .model-list {
    display: flex;
    flex-direction: column;
    gap: $spacer-md;
    margin-bottom: $spacer-xl;
  }

  .model-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: $spacer-lg;
    border: 2px solid $light-3;
    border-radius: $border-radius-md;
    background: white;
    cursor: pointer;
    transition: $transition-base;
    text-align: left;

    &:hover {
      border-color: $primary;
      box-shadow: $shadow-md;
    }

    &.active {
      border-color: $primary;
      background: rgba($primary, 0.05);
    }

    .model-info {
      flex: 1;

      h4 {
        margin: 0 0 $spacer-xs 0;
        color: $dark;
        font-size: $h6-size;
      }

      .model-type {
        margin: 0 0 $spacer-xs 0;
        font-size: $text-xs;
        color: $text-color-muted;
      }

      .model-description {
        margin: 0;
        font-size: $text-sm;
        color: $light-6;
      }
    }

    .model-price {
      display: flex;
      flex-direction: column;
      align-items: flex-end;
      gap: $spacer-xs;
      margin-left: $spacer-md;

      .label {
        font-size: $text-2xs;
        color: $text-color-muted;
      }

      .price {
        font-size: $h6-size;
        font-weight: $fw-bold;
        color: $primary;
      }
    }
  }

  // Faults Container
  .faults-container {
    margin-bottom: $spacer-xl;
  }

  .warning-box {
    display: flex;
    align-items: center;
    gap: $spacer-md;
    padding: $spacer-md;
    background: #fff3cd;
    border: 2px solid $color-warning;
    border-radius: $border-radius-md;
    margin-bottom: $spacer-lg;
    font-size: $text-base;
    color: #856404;

    i {
      font-size: $text-xl;
      flex-shrink: 0;
    }
  }

  .fault-item {
    display: flex;
    align-items: flex-start;
    gap: $spacer-md;
    padding: $spacer-md;
    border: 1px solid $light-3;
    border-radius: $border-radius-md;
    margin-bottom: $spacer-md;
    transition: $transition-base;

    &:hover:not(.disabled) {
      border-color: $primary;
      background: rgba($primary, 0.02);
    }

    &.disabled {
      opacity: 0.5;
      pointer-events: none;
    }

    &.critical {
      border-color: $color-warning;
      background: rgba($color-warning, 0.05);
    }

    .fault-checkbox {
      display: flex;
      align-items: center;
      margin-top: $spacer-xs;
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
        border: 2px solid $light-3;
        border-radius: $border-radius-sm;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: $transition-base;

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
        gap: $spacer-xs;
        margin-bottom: $spacer-xs;

        i {
          color: $primary;
          font-size: $h6-size;
        }

        strong {
          color: $dark;
          font-size: $text-base;
        }
      }

      .fault-description {
        margin: 0 0 $spacer-xs 0;
        font-size: $text-sm;
        color: $light-6;
      }

      .fault-price {
        display: inline-block;
        font-size: $text-xs;
        font-weight: $fw-semibold;
        color: $primary;
      }
    }
  }

  // Client Form
  .client-form {
    margin-bottom: $spacer-xl;
  }

  .form-group {
    margin-bottom: $spacer-lg;

    label {
      display: block;
      margin-bottom: $spacer-xs;
      font-weight: $fw-semibold;
      color: $dark;
      font-size: $text-base;
    }

    input {
      width: 100%;
      padding: $spacer-sm;
      border: 2px solid $light-3;
      border-radius: $border-radius-md;
      font-size: $text-base;
      transition: $transition-base;

      &:focus {
        outline: none;
        border-color: $primary;
        box-shadow: 0 0 0 3px rgba($primary, 0.1);
      }

      &::placeholder {
        color: $text-color-muted;
      }

      &:invalid:not(:placeholder-shown) {
        border-color: $color-danger;
      }
    }

    .error-text {
      display: block;
      margin-top: $spacer-xs;
      color: $color-danger;
      font-size: $text-xs;
      font-style: italic;
    }
  }

  // Quote Result
  .quote-result {
    .quote-summary {
      background: white;
      border: 2px solid $light-3;
      border-radius: $border-radius-lg;
      padding: $spacer-xl;
      margin-bottom: $spacer-xl;
    }

    .equipment-info {
      margin-bottom: $spacer-xl;
      padding-bottom: $spacer-xl;
      border-bottom: 2px solid $light-2;

      h4 {
        margin: 0 0 $spacer-xs 0;
        font-size: $h4-size;
        color: $dark;
      }

      .equipment-value {
        margin: 0;
        font-size: $text-sm;
        color: $light-6;
      }
    }

    .faults-summary {
      margin-bottom: $spacer-xl;
      padding-bottom: $spacer-xl;
      border-bottom: 2px solid $light-2;

      h5 {
        margin: 0 0 $spacer-md 0;
        color: $dark;
        font-size: $text-base;
      }

      ul {
        list-style: none;
        padding: 0;
        margin: 0;

        li {
          padding: $spacer-xs 0;
          color: $light-6;
          font-size: $text-sm;
          display: flex;
          justify-content: space-between;

          .fault-base-price {
            font-weight: $fw-semibold;
            color: $primary;
          }
        }
      }
    }

    .pricing-breakdown {
      margin-bottom: $spacer-xl;
      padding: $spacer-lg;
      background: rgba($primary, 0.05);
      border-radius: $border-radius-md;

      .price-row {
        display: flex;
        justify-content: space-between;
        margin-bottom: $spacer-sm;
        font-size: $text-base;
        color: $light-6;

        &.total {
          margin-top: $spacer-md;
          padding-top: $spacer-md;
          border-top: 2px solid rgba($primary, 0.2);
          font-weight: $fw-bold;
          color: $dark;
          font-size: $h6-size;

          .total-price {
            color: $primary;
            font-size: $h4-size;
          }
        }
      }
    }

    .quote-error {
      margin-bottom: $spacer-xl;
      padding: $spacer-lg;
      background: #fff3cd;
      border: 2px solid $color-warning;
      border-radius: $border-radius-md;
      display: flex;
      align-items: center;
      gap: $spacer-md;

      i {
        font-size: $text-2xl;
        color: #ff9800;
      }

      p {
        margin: 0;
        color: $dark;
        font-size: $text-base;
      }
    }

    .client-info-display {
      margin-bottom: $spacer-xl;
      padding: $spacer-md;
      background: $light-1;
      border-radius: $border-radius-md;

      p {
        margin: $spacer-xs 0;
        font-size: $text-sm;

        strong {
          color: $dark;
        }
      }
    }

    .action-buttons {
      display: flex;
      gap: $spacer-md;
      flex-wrap: wrap;

      @include media-breakpoint-down(sm) {
        flex-direction: column;
      }
    }
  }

  // Buttons
  .btn {
    padding: $spacer-sm $spacer-lg;
    border: none;
    border-radius: $border-radius-md;
    font-weight: $fw-semibold;
    cursor: pointer;
    transition: $transition-base;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: $spacer-xs;
    text-transform: uppercase;
    font-size: $text-sm;
    letter-spacing: $ls-wider;

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
        box-shadow: $shadow-md;
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
    padding: $spacer-md;
    background: rgba($primary, 0.05);
    border-left: 4px solid $primary;
    border-radius: $border-radius-sm;
    margin-bottom: $spacer-lg;
    font-size: $text-base;
    color: $dark;
  }

  .empty-state {
    padding: $spacer-xl;
    text-align: center;
    color: $text-color-muted;
    font-size: $text-base;
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
