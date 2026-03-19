<template>
  <div class="cotizador-page">

    <!-- Indicador de progreso -->
    <div class="progress-bar" aria-hidden="true">
      <div class="progress-fill"></div>
    </div>

    <!-- Error global -->
    <p v-if="error" class="alert-error" role="alert">{{ error }}</p>

    <!-- ── Paso 1: Selección de equipo ───────────────────────────── -->
    <CotizadorInstrumentStep
      v-if="step === 1"
      :not-found-mode="notFoundMode"
      :loading="loading"
      :brands="brands"
      :selected-brand="selectedBrand"
      :models="models"
      :selected-model="selectedModel"
      :manual-brand="manualBrand"
      :manual-model="manualModel"
      :can-continue-step1="canContinueStep1"
      @brand-select="onBrandSelect"
      @model-select="onModelSelect"
      @update:manual-brand="manualBrand = $event"
      @update:manual-model="manualModel = $event"
      @activate-not-found-mode="activateNotFoundMode"
      @deactivate-not-found-mode="deactivateNotFoundMode"
      @continue="notFoundMode ? goToLeadStep() : (step = 2)"
    />

    <!-- ── Paso 2: Selección de fallas ──────────────────────────── -->
    <CotizadorFaultsStep
      v-if="step === 2"
      :loading="loading"
      :selected-brand-name="selectedBrandName"
      :selected-model-name="selectedModelName"
      :faults="faults"
      :selected-fault-ids="selectedFaultIds"
      :quote-turnstile-render-key="quoteTurnstileRenderKey"
      :can-continue-step2="canContinueStep2"
      @toggle-fault="toggleFault"
      @quote-verify="onQuoteVerify"
      @back="step = 1"
      @continue="calculateQuote"
    />

    <!-- ── Paso 3: Resultado del cálculo ────────────────────────── -->
    <CotizadorEstimateStep
      v-if="step === 3"
      :quote-result="quoteResult"
      :selected-fault-names="selectedFaultNames"
      :formatted-final-cost="formattedFinalCost"
      :format-clp="formatCLP"
      @back="step = 2"
      @continue="goToLeadStep"
    />

    <!-- ── Paso 4: Formulario de contacto ────────────────────────── -->
    <CotizadorLeadStep
      v-if="step === 4"
      :lead-submitted="leadSubmitted"
      :not-found-mode="notFoundMode"
      :lead-form="leadForm"
      :accepted-disclaimer="acceptedDisclaimer"
      :lead-turnstile-render-key="leadTurnstileRenderKey"
      :can-submit-lead="canSubmitLead"
      :loading="loading"
      :selected-brand-name="selectedBrandName"
      :selected-model-name="selectedModelName"
      :formatted-final-cost="formattedFinalCost"
      @update-lead-field="updateLeadField"
      @update:accepted-disclaimer="acceptedDisclaimer = $event"
      @lead-verify="onLeadVerify"
      @back="notFoundMode ? (step = 1) : (step = 3)"
      @submit="submitLead"
      @reset="resetAll"
      @schedule="goToSchedule"
    />

  </div>
</template>

<script setup>
import { computed } from 'vue'
import CotizadorEstimateStep from '@/components/business/CotizadorEstimateStep.vue'
import CotizadorFaultsStep from '@/components/business/CotizadorFaultsStep.vue'
import CotizadorInstrumentStep from '@/components/business/CotizadorInstrumentStep.vue'
import CotizadorLeadStep from '@/components/business/CotizadorLeadStep.vue'
import { useCotizadorIAPage } from '@/composables/useCotizadorIAPage'

const {
  step,
  loading,
  error,
  brands,
  selectedBrand,
  models,
  selectedModel,
  faults,
  selectedFaultIds,
  quoteResult,
  leadForm,
  acceptedDisclaimer,
  leadSubmitted,
  notFoundMode,
  manualBrand,
  manualModel,
  canContinueStep1,
  canContinueStep2,
  canSubmitLead,
  formattedFinalCost,
  selectedBrandName,
  selectedModelName,
  selectedFaultNames,
  quoteTurnstileRenderKey,
  leadTurnstileRenderKey,
  onBrandSelect,
  onModelSelect,
  toggleFault,
  calculateQuote,
  submitLead,
  onQuoteVerify,
  onLeadVerify,
  goToLeadStep,
  goToSchedule,
  resetAll,
  activateNotFoundMode,
  deactivateNotFoundMode,
} = useCotizadorIAPage()

const progressScale = computed(() => {
  const currentStep = Number(step.value || 1)
  if (notFoundMode.value) {
    return currentStep === 1 ? '0.5' : '1'
  }
  const normalized = Math.min(Math.max(currentStep / 4, 0), 1)
  return String(normalized)
})

function formatCLP(value) {
  return new Intl.NumberFormat('es-CL', {
    style: 'currency',
    currency: 'CLP',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(Number(value || 0))
}

function updateLeadField({ field, value }) {
  if (!field) return
  leadForm.value[field] = value
}
</script>

<style scoped>
@import '@/components/business/cotizadorStepShared.css';

.cotizador-page {
  padding: var(--layout-quotation-page-padding, 0.5rem 1rem 2rem);
  display: grid;
  gap: var(--layout-quotation-page-gap, 1rem);
}

/* Barra de progreso */
.progress-bar {
  height: var(--layout-quotation-progress-height, 4px);
  background: color-mix(in srgb, var(--cds-light) 60%, white);
  border-radius: var(--layout-quotation-progress-radius, 4px);
  overflow: hidden;
  max-width: var(--layout-quotation-shell-max, 920px);
  margin: 0 auto;
  width: 100%;
}

.progress-fill {
  height: 100%;
  background: var(--cds-primary);
  transform: scaleX(v-bind(progressScale));
  transform-origin: left center;
  transition: transform 0.35s ease;
}

/* Alerta de error */
.alert-error {
  max-width: var(--layout-quotation-shell-max, 920px);
  margin: 0 auto;
  width: 100%;
  padding: var(--layout-quotation-alert-padding-block, 0.75rem) var(--layout-quotation-alert-padding-inline, 1rem);
  background: color-mix(in srgb, var(--cds-primary) 10%, white);
  border: 1px solid color-mix(in srgb, var(--cds-primary) 35%, white);
  border-radius: var(--cds-radius-sm);
  color: var(--cds-primary);
  font-size: var(--cds-text-sm);
}

@media (min-width: 640px) {
  .cotizador-page {
    padding: var(--layout-quotation-page-padding-md, 1rem 1.5rem 2.5rem);
  }
}
</style>
