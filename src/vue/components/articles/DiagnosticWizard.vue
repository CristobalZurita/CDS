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
import { ref, computed } from 'vue'
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

const _currentBrand = computed(() => {
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

const _formatPrice = (price) => {
  if (!price) return '0'
  return new Intl.NumberFormat('es-CL', {
    style: 'currency',
    currency: 'CLP',
    minimumFractionDigits: 0
  }).format(price).replace(/\s/g, '')
}

const _selectBrand = (brandId) => {
  diagnostic.selectedBrand.value = brandId
  diagnostic.selectedModel.value = null
  diagnostic.clearFaults()
}

const _selectModel = (instrumentId) => {
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
  const quote = data?.diagnostics?.quote
  
  if (!data || !data.client || !quote) {
    alert('Error: No hay datos de cotización para descargar')
    return
  }

  // Generate simple CSV for now (TODO: Generate PDF)
  const csv = `
COTIZACIÓN - CIRUJANO DE SINTETIZADORES
========================================

CLIENTE:
Nombre: ${data.client.name}
Email: ${data.client.email}
Teléfono: ${data.client.phone || 'No proporcionado'}

EQUIPO:
Marca: ${quote.brand?.name || data.equipment.brand}
Modelo: ${quote.instrument?.model || data.equipment.model}

PROBLEMAS DETECTADOS:
${quote.faults.map(f => `- ${f.name}: $${f.basePrice}`).join('\n')}

COTIZACIÓN:
Subtotal: $${quote.baseCost}
Factor complejidad (${quote.brand?.tier || 'standard'}): ${quote.complexityFactor}x
Factor valor equipo: ${quote.valueFactor}x
TOTAL: $${quote.finalCost}

Válida por: 30 días
Fecha: ${new Date().toLocaleDateString('es-CL')}
  `.trim()

  // Download as text file
  const blob = new Blob([csv], { type: 'text/plain' })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `cotizacion-${data.client.name.replace(/\s+/g, '-')}.txt`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)

  console.log('Quote downloaded:', data)
}
</script>
