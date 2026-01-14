<template>
  <div class="cotizador-ia-page">
    <!-- Step 1: Instrument Selection -->
    <div v-if="step === 1" class="step-container">
      <div class="step-header">
        <h1>🎛️ Seleccionar Instrumento</h1>
        <p>Paso 1 de 4 - Busca tu marca y modelo</p>
      </div>

      <InstrumentSelector @selected="onInstrumentSelected" />
    </div>

    <!-- Step 2: Diagnostic Wizard -->
    <div v-if="step === 2" class="step-container">
      <div class="step-header">
        <h1>🔍 Diagnóstico Visual</h1>
        <p>Paso 2 de 4 - Selecciona las fallas que observas</p>
      </div>

      <DiagnosticWizard
        :instrument="selectedInstrument"
        @complete="onDiagnosticComplete"
        @back="step = 1"
      />
    </div>

    <!-- Step 3: Disclaimer Modal -->
    <div v-if="step === 3">
      <DisclaimerModal
        :show="true"
        @accept="onDisclaimerAccepted"
        @cancel="step = 2"
      />
    </div>

    <!-- Step 4: Quotation Result -->
    <div v-if="step === 4" class="step-container">
      <div class="step-header">
        <h1>💰 Tu Cotización</h1>
        <p>Paso 4 de 4 - Resultado de estimación</p>
      </div>

      <QuotationResult
        :quotation="quotation"
        :loading="loading"
        @new-quote="resetAll"
        @schedule="goToSchedule"
      />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useQuotation } from '@/composables/useQuotation'
import { useDiagnostic } from '@/composables/useDiagnostic'
import { useQuotationStore } from '@/stores/quotation'

// Components
import InstrumentSelector from '@/vue/components/quotation/InstrumentSelector.vue'
import DiagnosticWizard from '@/vue/components/articles/DiagnosticWizard.vue'
import DisclaimerModal from '@/vue/components/quotation/DisclaimerModal.vue'
import QuotationResult from '@/vue/components/quotation/QuotationResult.vue'

const router = useRouter()
const quotationStore = useQuotationStore()
const { quotation, loading, estimate, reset } = useQuotation()

// State
const step = ref(1)
const selectedInstrument = ref(null)
const selectedFaults = ref([])

/**
 * Step 1: User selects instrument (brand + model)
 */
const onInstrumentSelected = (instrument) => {
  selectedInstrument.value = instrument
  step.value = 2
}

/**
 * Step 2: User selects faults via diagnostic wizard
 */
const onDiagnosticComplete = (faults) => {
  selectedFaults.value = faults
  quotationStore.setFaults(faults)
  step.value = 3
}

/**
 * Step 3: User accepts disclaimer
 */
const onDisclaimerAccepted = async () => {
  step.value = 4
  try {
    await estimate(selectedInstrument.value.id, selectedFaults.value)
  } catch (err) {
    // Error will be shown in QuotationResult component
    console.error('Error generating quotation:', err)
  }
}

/**
 * Reset all and start over
 */
const resetAll = () => {
  selectedInstrument.value = null
  selectedFaults.value = []
  reset()
  step.value = 1
}

/**
 * Navigate to appointment scheduling
 */
const goToSchedule = () => {
  // TODO: Implement calendar/schedule page
  router.push('/agendar')
}
</script>

<style scoped>
.cotizador-ia-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 2rem 1rem;
}

.step-container {
  max-width: 1000px;
  margin: 0 auto;
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  animation: slideUp 0.4s ease-out;
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

.step-header {
  margin-bottom: 2rem;
  padding-bottom: 2rem;
  border-bottom: 2px solid #e2e8f0;
}

.step-header h1 {
  margin: 0 0 0.5rem 0;
  color: #2d3748;
  font-size: 2rem;
}

.step-header p {
  margin: 0;
  color: #718096;
  font-size: 1rem;
}

@media (max-width: 768px) {
  .cotizador-ia-page {
    padding: 1rem;
  }

  .step-container {
    padding: 1.5rem;
  }

  .step-header h1 {
    font-size: 1.5rem;
  }
}
</style>
