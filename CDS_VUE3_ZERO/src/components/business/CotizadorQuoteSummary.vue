<template>
  <div v-if="quoteResult" class="result-box">
    <div class="result-equipment">
      <strong>{{ quoteResult.equipment_info.brand }} {{ quoteResult.equipment_info.model }}</strong>
    </div>

    <div class="result-faults">
      <span v-for="name in selectedFaultNames" :key="name" class="fault-tag">{{ name }}</span>
    </div>

    <div class="result-breakdown">
      <div class="breakdown-row">
        <span>Costo base de diagnóstico</span>
        <span>{{ formatClp(quoteResult.base_cost) }}</span>
      </div>
      <div class="breakdown-row" v-if="quoteResult.complexity_factor !== 1">
        <span>Factor complejidad (marca)</span>
        <span>× {{ quoteResult.complexity_factor }}</span>
      </div>
      <div class="breakdown-row" v-if="quoteResult.value_factor !== 1">
        <span>Factor valor estimado</span>
        <span>× {{ quoteResult.value_factor }}</span>
      </div>
    </div>

    <div class="result-total">
      <span>Estimación total</span>
      <strong>{{ formattedFinalCost }}</strong>
    </div>
  </div>
</template>

<script setup>
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
</script>

<style scoped>
.result-box {
  border: 1px solid var(--cds-border-card);
  border-radius: var(--layout-quotation-summary-radius, 0.7rem);
  padding: var(--layout-quotation-summary-padding, 0.9rem);
  display: grid;
  gap: var(--layout-quotation-summary-gap, 0.75rem);
}

.result-equipment {
  font-size: var(--cds-text-base);
}

.result-faults {
  display: flex;
  flex-wrap: wrap;
  gap: var(--layout-quotation-tag-gap, 0.4rem);
}

.fault-tag {
  font-size: var(--cds-text-xs);
  padding: var(--layout-quotation-tag-pad-block, 0.2rem) var(--layout-quotation-tag-pad-inline, 0.5rem);
  background: var(--cds-surface-2);
  border-radius: var(--layout-quotation-chip-radius, 0.35rem);
  color: var(--cds-text-normal);
}

.result-breakdown {
  display: grid;
  gap: 0.3rem;
  border-top: 1px solid var(--cds-border-soft);
  padding-top: var(--layout-quotation-summary-divider-padding-top, 0.65rem);
}

.breakdown-row {
  display: flex;
  justify-content: space-between;
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
}

.result-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 2px solid var(--cds-primary);
  padding-top: var(--layout-quotation-summary-divider-padding-top, 0.65rem);
  font-size: var(--cds-text-base);
}

.result-total strong {
  font-size: var(--cds-text-2xl);
  color: var(--cds-primary);
}
</style>
