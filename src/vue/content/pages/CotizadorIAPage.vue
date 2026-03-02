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
