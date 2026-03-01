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

      <InteractiveInstrumentDiagnostic
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
import { useQuotationStore } from '@/stores/quotation'
import TurnstileWidget from '@/vue/components/widgets/TurnstileWidget.vue'

// Components
import InstrumentSelector from '@/vue/components/quotation/InstrumentSelector.vue'
import InteractiveInstrumentDiagnostic from '@/vue/components/quotation/InteractiveInstrumentDiagnostic.vue'
import DisclaimerModal from '@/vue/components/quotation/DisclaimerModal.vue'
import QuotationResult from '@/vue/components/quotation/QuotationResult.vue'

const router = useRouter()
const quotationStore = useQuotationStore()
const { quotation, loading, estimate, reset } = useQuotation()

// State
const step = ref(1)
const selectedInstrument = ref(null)
const selectedFaults = ref([])
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
const onDiagnosticComplete = (faults) => {
  selectedFaults.value = faults
  quotationStore.setFaults(faults)
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
    await estimate(selectedInstrument.value.id, selectedFaults.value, turnstileToken.value)
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
  router.push('/agendar')
}

const onVerify = (token) => {
  turnstileToken.value = token
}
</script>

<style lang="scss" scoped>
@use "@/scss/_core.scss" as *;

.cotizador-ia-page {
  min-height: 100vh;
  background: linear-gradient(135deg, $color-slate-50-legacy 0%, $color-slate-200-legacy 100%);
  padding: $spacer-xl $spacer-md;
}

.step-container {
  max-width: 1000px;
  margin: 0 auto;
  background: $color-white;
  border-radius: $border-radius-xl;
  padding: $spacer-xl;
  box-shadow: 0 8px 32px rgba($color-black, 0.1);
  animation: slideUp 0.4s ease-out;
}

.captcha-wrap {
  display: flex;
  justify-content: center;
  margin-top: $spacer-md;
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
  margin-bottom: $spacer-xl;
  padding-bottom: $spacer-xl;
  border-bottom: 2px solid $color-border-light-legacy;
}

.step-header h1 {
  margin: 0 0 $spacer-sm 0;
  color: $color-text-dark-legacy;
  font-size: $h2-size;
}

.step-header p {
  margin: 0;
  color: $color-text-medium-legacy;
  font-size: $text-base;
}

@media (max-width: 768px) {
  .cotizador-ia-page {
    padding: $spacer-md;
  }

  .step-container {
    padding: $spacer-lg;
  }

  .step-header h1 {
    font-size: $h4-size;
  }
}
</style>
