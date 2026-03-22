<template>
  <div v-if="quoteResult" class="result-box">

    <!-- Cabecera: equipo + badge origen -->
    <div class="result-header">
      <strong class="result-equipment-name">
        {{ quoteResult.equipment_info.brand }} {{ quoteResult.equipment_info.model }}
      </strong>
      <span class="result-source-badge" :class="quoteResult.from_db ? 'badge-db' : 'badge-ai'">
        <i :class="quoteResult.from_db ? 'fas fa-database' : 'fas fa-robot'"></i>
        {{ quoteResult.from_db ? 'Catálogo' : 'IA' }}
      </span>
    </div>

    <!-- Fallas seleccionadas -->
    <div v-if="selectedFaultNames.length" class="result-faults">
      <span v-for="name in selectedFaultNames" :key="name" class="fault-tag">{{ name }}</span>
    </div>

    <!-- Datos del catálogo si están disponibles -->
    <div v-if="quoteResult.valor_usd_max" class="result-context-row">
      <span class="context-label">Valor de mercado</span>
      <span class="context-value">
        USD {{ quoteResult.valor_usd_min }}–{{ quoteResult.valor_usd_max }}
      </span>
    </div>
    <div v-if="quoteResult.complexity" class="result-context-row">
      <span class="context-label">Complejidad</span>
      <span class="complexity-badge" :class="`complexity--${quoteResult.complexity}`">
        {{ quoteResult.complexity.replace('_', ' ') }}
      </span>
    </div>
    <div v-if="quoteResult.tiempo_estimado" class="result-context-row">
      <span class="context-label">Tiempo estimado</span>
      <span class="context-value">{{ quoteResult.tiempo_estimado }}</span>
    </div>

    <!-- Total -->
    <div class="result-total">
      <div class="result-total-label">
        <span>Derecho a revisión estimado</span>
        <span v-if="quoteResult.min_price !== quoteResult.max_price" class="result-range">
          {{ formatClp(quoteResult.min_price) }} – {{ formatClp(quoteResult.max_price) }}
        </span>
      </div>
      <strong>{{ formattedFinalCost }}</strong>
    </div>

    <!-- Disclaimer -->
    <p v-if="quoteResult.disclaimer" class="result-disclaimer">
      <i class="fas fa-circle-info"></i> {{ quoteResult.disclaimer }}
    </p>
  </div>
</template>

<script setup>
defineProps({
  quoteResult: { type: Object, default: null },
  selectedFaultNames: { type: Array, default: () => [] },
  formattedFinalCost: { type: String, required: true },
  formatClp: { type: Function, required: true }
})
</script>

<style scoped>
.result-box {
  border: 1px solid var(--cds-border-card);
  border-left: 3px solid var(--cds-primary);
  border-radius: var(--layout-quotation-summary-radius, 0.7rem);
  padding: var(--layout-quotation-summary-padding, 0.9rem);
  display: grid;
  gap: var(--layout-quotation-summary-gap, 0.75rem);
  background: var(--cds-surface-1);
}

/* Cabecera */
.result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.result-equipment-name {
  font-size: var(--cds-text-base);
  font-weight: 700;
}

.result-source-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  font-size: var(--cds-text-xs);
  font-weight: 600;
  padding: 0.15rem 0.5rem;
  border-radius: 99px;
}

.badge-db {
  background: #d4edda;
  color: #1a5c30;
}

.badge-ai {
  background: #e8e0ff;
  color: #4a2080;
}

/* Fallas */
.result-faults {
  display: flex;
  flex-wrap: wrap;
  gap: var(--layout-quotation-tag-gap, 0.4rem);
}

.fault-tag {
  font-size: var(--cds-text-xs);
  padding: 0.2rem 0.55rem;
  background: var(--cds-surface-2);
  border-radius: var(--layout-quotation-chip-radius, 0.35rem);
  color: var(--cds-text-normal);
  border: 1px solid var(--cds-border-soft);
}

/* Datos de contexto */
.result-context-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  font-size: var(--cds-text-sm);
}

.context-label {
  color: var(--cds-text-muted);
  font-size: var(--cds-text-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.context-value {
  font-weight: 600;
  color: var(--cds-text-normal);
}

.complexity-badge {
  font-size: var(--cds-text-xs);
  font-weight: 700;
  padding: 0.15rem 0.5rem;
  border-radius: 99px;
  text-transform: capitalize;
}

.complexity--baja     { background: #d4edda; color: #1a5c30; }
.complexity--media    { background: #fff3cd; color: #7a5a00; }
.complexity--alta     { background: #ffe0c2; color: #7a3000; }
.complexity--muy_alta { background: #f8d7da; color: #7a0010; }

/* Total */
.result-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 2px solid var(--cds-primary);
  padding-top: 0.65rem;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.result-total-label {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  font-size: var(--cds-text-base);
}

.result-range {
  font-size: var(--cds-text-xs);
  color: var(--cds-text-muted);
  font-weight: 500;
}

.result-total strong {
  font-size: var(--cds-text-2xl);
  color: var(--cds-primary);
  white-space: nowrap;
}

/* Disclaimer */
.result-disclaimer {
  font-size: var(--cds-text-xs);
  color: var(--cds-text-muted);
  line-height: 1.5;
  display: flex;
  gap: 0.4rem;
  align-items: flex-start;
  padding: 0.5rem 0.65rem;
  background: var(--cds-surface-2);
  border-radius: var(--cds-radius-sm);
  margin: 0;
}
</style>
