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
        <p>Paso 2 de 4 - Responde el flujo guiado y marca lo visible</p>
      </div>

      <InteractiveInstrumentDiagnostic
        :initial-instrument="selectedInstrument"
        @complete="onDiagnosticComplete"
      />
    </div>

    <!-- Step 3: Disclaimer Modal -->
    <div v-if="step === 3">
      <DisclaimerModal
        :show="true"
        @accept="onDisclaimerAccepted"
        @cancel="step = 2"
      />
      <div class="captcha-wrap">
        <TurnstileWidget @verify="onVerify" />
      </div>
    </div>

    <!-- Step 4: Quotation Result -->
    <div v-if="step === 4" class="step-container">
      <div class="step-header">
        <h1>💰 Tu Estimación Referencial</h1>
        <p>Paso 4 de 4 - Resultado orientativo del cotizador</p>
      </div>

      <QuotationResult
        :quotation="quotation"
        :loading="loading"
        :error="error"
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
import { useQuotationStore } from '@/stores/quotation'
import TurnstileWidget from '@/vue/components/widgets/TurnstileWidget.vue'

// Components
import InstrumentSelector from '@/vue/components/quotation/InstrumentSelector.vue'
import InteractiveInstrumentDiagnostic from '@/vue/components/quotation/InteractiveInstrumentDiagnostic.vue'
import DisclaimerModal from '@/vue/components/quotation/DisclaimerModal.vue'
import QuotationResult from '@/vue/components/quotation/QuotationResult.vue'

const router = useRouter()
const quotationStore = useQuotationStore()
const { quotation, loading, error, estimate, reset } = useQuotation()

// State
const step = ref(1)
const selectedInstrument = ref(null)
const diagnosticPayload = ref(null)
const turnstileToken = ref('')

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
const onDiagnosticComplete = (payload) => {
  diagnosticPayload.value = payload
  quotationStore.setFaults(payload?.selected_symptoms || [])
  step.value = 3
}

/**
 * Step 3: User accepts disclaimer
 */
const onDisclaimerAccepted = async () => {
  if (!turnstileToken.value) {
    return
  }
  step.value = 4
  try {
    await estimate(selectedInstrument.value.id, diagnosticPayload.value || [], turnstileToken.value)
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
  diagnosticPayload.value = null
  turnstileToken.value = ''
  reset()
  step.value = 1
}

/**
 * Navigate to appointment scheduling
 */
const goToSchedule = () => {
  router.push('/agendar')
}

const onVerify = (token) => {
  turnstileToken.value = token
}
</script>

<style scoped>
.cotizador-ia-page {
  min-height: 100vh;
  background: linear-gradient(135deg, var(--gray-50) 0%, var(--gray-200) 100%);
  padding: var(--spacer-xl) var(--spacer-md);
}

.step-container {
  max-width: 1000px;
  margin: 0 auto;
  background: var(--color-white);
  border-radius: var(--radius-xl);
  padding: var(--spacer-xl);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  animation: slideUp 0.4s ease-out;
}

.captcha-wrap {
  display: flex;
  justify-content: center;
  margin-top: var(--spacer-md);
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
  margin-bottom: var(--spacer-xl);
  padding-bottom: var(--spacer-xl);
  border-bottom: 2px solid var(--gray-200);
}

.step-header h1 {
  margin: 0 0 var(--spacer-sm) 0;
  color: var(--color-dark);
  font-size: var(--text-2xl);
}

.step-header p {
  margin: 0;
  color: var(--gray-600);
  font-size: var(--text-base);
}

@media (max-width: 768px) {
  .cotizador-ia-page {
    padding: var(--spacer-md);
  }

  .step-container {
    padding: var(--spacer-lg);
  }

  .step-header h1 {
    font-size: var(--text-lg);
  }
}
</style>
