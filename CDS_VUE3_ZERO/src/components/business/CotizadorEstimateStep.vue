<template>
  <div class="cotizador-card">
    <CotizadorStepHeader badge="Paso 3 de 4" title="Estimación referencial">
      <template #description>
        Basada en los síntomas seleccionados y el perfil del equipo.
      </template>
    </CotizadorStepHeader>

    <CotizadorQuoteSummary
      :quote-result="quoteResult"
      :selected-fault-names="selectedFaultNames"
      :formatted-final-cost="formattedFinalCost"
      :format-clp="formatClp"
    />

    <div class="disclaimer">
      <p>Esta cotización es referencial y no vinculante. El presupuesto formal requiere revisión presencial en taller.</p>
    </div>

    <div class="actions">
      <button class="btn-secondary" @click="emit('back')">← Atrás</button>
      <button class="btn-primary" @click="emit('continue')">Dejar mis datos →</button>
    </div>
  </div>
</template>

<script setup>
import CotizadorQuoteSummary from '@/components/business/CotizadorQuoteSummary.vue'
import CotizadorStepHeader from '@/components/business/CotizadorStepHeader.vue'

defineProps({
  quoteResult: {
    type: Object,
    default: null
  },
  selectedFaultNames: {
    type: Array,
    default: () => []
  },
  formattedFinalCost: {
    type: String,
    required: true
  },
  formatClp: {
    type: Function,
    required: true
  }
})

const emit = defineEmits(['back', 'continue'])
</script>

<style scoped>
@import './cotizadorStepShared.css';

.disclaimer {
  border: 1px solid var(--cds-border-input);
  border-radius: var(--layout-quotation-summary-radius, 0.7rem);
  padding: var(--layout-quotation-disclaimer-padding, 0.75rem);
  background: var(--cds-surface-2);
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
}

.disclaimer p {
  margin: 0;
}
</style>
