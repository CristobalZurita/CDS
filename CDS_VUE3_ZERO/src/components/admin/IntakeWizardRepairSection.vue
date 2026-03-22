<template>
  <section id="ot" class="form-section">
    <div class="section-header">
      <h2>3. Orden de Trabajo</h2>
    </div>

    <div class="field-group">
      <FormField
        v-model="repair.problem_reported"
        type="textarea"
        label="Problema reportado"
        placeholder="Describa detalladamente el problema que presenta el equipo..."
        :error="errors['repair.problem_reported']"
        required
        :rows="4"
        @blur="$emit('validate-field', 'repair.problem_reported', repair.problem_reported)"
      />
    </div>

    <!-- Asistente IA -->
    <div class="ai-assist-wrap">
      <button
        type="button"
        class="ai-btn"
        :disabled="!canConsultarIA || aiLoading"
        @click="onConsultarIA"
      >
        <span v-if="aiLoading" class="ai-spinner"></span>
        <i v-else class="fas fa-wand-magic-sparkles"></i>
        {{ aiLoading ? 'Consultando IA…' : 'Sugerencia IA' }}
      </button>
      <span v-if="!canConsultarIA" class="ai-hint">Completa marca y modelo en la sección anterior</span>
      <span v-if="aiError" class="ai-error">{{ aiError }}</span>
    </div>

    <!-- Panel de sugerencia IA -->
    <div v-if="aiSuggestion" class="ai-panel">
      <div class="ai-panel-header">
        <span class="ai-panel-title">
          <i class="fas fa-robot"></i> Sugerencia para {{ deviceBrand }} {{ deviceModel }}
        </span>
        <button type="button" class="ai-panel-close" @click="$emit('clear-ai')">
          <i class="fas fa-xmark"></i>
        </button>
      </div>

      <!-- Valor de mercado -->
      <div class="ai-row">
        <span class="ai-label">Valor de mercado estimado</span>
        <span class="ai-value">
          USD {{ aiSuggestion.valor_usd_min }}–{{ aiSuggestion.valor_usd_max }}
        </span>
      </div>

      <!-- Complejidad y tiempo -->
      <div class="ai-row">
        <span class="ai-label">Complejidad</span>
        <span class="ai-badge" :class="`ai-badge--${aiSuggestion.complejidad}`">
          {{ aiSuggestion.complejidad.replace('_', ' ') }}
        </span>
      </div>
      <div class="ai-row">
        <span class="ai-label">Tiempo estimado (técnico solo)</span>
        <span class="ai-value">{{ aiSuggestion.tiempo_estimado }}</span>
      </div>

      <!-- Fallas conocidas -->
      <div v-if="aiSuggestion.fallas_conocidas?.length" class="ai-fallas">
        <span class="ai-label">Fallas conocidas para este modelo</span>
        <div class="ai-fallas-list">
          <button
            v-for="falla in aiSuggestion.fallas_conocidas"
            :key="falla"
            type="button"
            class="ai-falla-pill"
            :title="`Añadir: ${falla}`"
            @click="appendFalla(falla)"
          >{{ falla }}</button>
        </div>
      </div>

      <!-- Derecho a revisión — opciones -->
      <div class="ai-cobro">
        <span class="ai-label">Derecho a revisión sugerido (CLP)</span>
        <div class="ai-cobro-options">
          <label
            v-for="monto in aiSuggestion.opciones_cobro"
            :key="monto"
            class="ai-cobro-option"
            :class="{ 'is-selected': repair.paid_amount === monto }"
          >
            <input
              type="radio"
              name="ai-cobro"
              :value="monto"
              :checked="repair.paid_amount === monto"
              @change="$emit('set-cobro', monto)"
            />
            {{ formatCLP(monto) }}
          </label>
        </div>
      </div>

      <!-- Notas -->
      <div v-if="aiSuggestion.notas" class="ai-notas">
        <i class="fas fa-circle-info"></i> {{ aiSuggestion.notas }}
      </div>
    </div>

    <div class="field-group">
      <FormField
        v-model="repair.diagnosis"
        type="textarea"
        label="Diagnóstico inicial (opcional)"
        placeholder="Si ya tiene una idea del problema..."
        :rows="3"
      />
    </div>

    <div class="field-grid cols-3">
      <FormField
        v-model="repair.priority"
        type="select"
        label="Prioridad"
        :options="[
          { value: 1, label: 'Alta' },
          { value: 2, label: 'Normal' },
          { value: 3, label: 'Baja' }
        ]"
        required
      />

      <FormField
        v-model="repair.paid_amount"
        type="number"
        label="Abono / Derecho revisión (CLP)"
        :min="0"
        :step="1000"
        :error="errors['repair.paid_amount']"
        required
      />

      <FormField
        v-model="repair.payment_method"
        type="select"
        label="Método de pago"
        :options="[
          { value: 'cash', label: 'Efectivo' },
          { value: 'transfer', label: 'Transferencia' },
          { value: 'web', label: 'Web' }
        ]"
        required
      />
    </div>

    <div class="field-group">
      <FormField
        v-model="repair.warranty_days"
        type="number"
        label="Días de garantía"
        :min="0"
        :max="365"
      />
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { FormField } from '@/components/composite'

const props = defineProps({
  repair: {
    type: Object,
    required: true
  },
  errors: {
    type: Object,
    required: true
  },
  deviceBrand: {
    type: String,
    default: ''
  },
  deviceModel: {
    type: String,
    default: ''
  },
  aiLoading: {
    type: Boolean,
    default: false
  },
  aiError: {
    type: String,
    default: ''
  },
  aiSuggestion: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['validate-field', 'consultar-ia', 'clear-ai', 'set-cobro'])

const canConsultarIA = computed(() =>
  props.deviceBrand?.trim() && props.deviceModel?.trim()
)

function onConsultarIA() {
  emit('consultar-ia', props.deviceBrand, props.deviceModel, props.repair.problem_reported)
}

function appendFalla(falla) {
  const current = props.repair.problem_reported?.trim() || ''
  props.repair.problem_reported = current ? `${current}\n- ${falla}` : `- ${falla}`
}

function formatCLP(n) {
  return `$${n.toLocaleString('es-CL')}`
}
</script>

<style scoped>
@import './intakeWizardSection.css';

/* ── AI assist trigger ─────────────────────────────────────────── */
.ai-assist-wrap {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
  margin-bottom: var(--intake-field-gap, 1rem);
}

.ai-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.45rem 1rem;
  background: var(--cds-primary);
  color: var(--cds-white);
  border: none;
  border-radius: var(--cds-radius-sm);
  font-size: var(--cds-text-sm);
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.15s;
}

.ai-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.ai-btn:not(:disabled):hover {
  opacity: 0.88;
}

.ai-spinner {
  width: 0.9rem;
  height: 0.9rem;
  border: 2px solid rgba(255,255,255,0.35);
  border-top-color: #fff;
  border-radius: 50%;
  animation: ai-spin 0.7s linear infinite;
  flex-shrink: 0;
}

@keyframes ai-spin {
  to { transform: rotate(360deg); }
}

.ai-hint {
  font-size: var(--cds-text-xs);
  color: var(--cds-text-muted);
}

.ai-error {
  font-size: var(--cds-text-xs);
  color: var(--cds-danger, #c0392b);
}

/* ── AI panel ─────────────────────────────────────────────────── */
.ai-panel {
  border: 1px solid var(--cds-border-card);
  border-left: 3px solid var(--cds-primary);
  border-radius: var(--cds-radius-md);
  background: var(--cds-light-1, #f7f5ee);
  padding: var(--cds-space-md);
  margin-bottom: var(--intake-field-gap, 1rem);
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.ai-panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.ai-panel-title {
  font-size: var(--cds-text-sm);
  font-weight: 700;
  color: var(--cds-primary);
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.ai-panel-close {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--cds-text-muted);
  font-size: var(--cds-text-sm);
  padding: 0.2rem 0.4rem;
  border-radius: var(--cds-radius-sm);
  line-height: 1;
}

.ai-panel-close:hover {
  color: var(--cds-text-normal);
  background: var(--cds-light-2, #ece9df);
}

.ai-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  font-size: var(--cds-text-sm);
}

.ai-label {
  color: var(--cds-text-muted);
  font-size: var(--cds-text-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.ai-value {
  font-weight: 700;
  color: var(--cds-text-normal);
}

/* Complejidad badges */
.ai-badge {
  font-size: var(--cds-text-xs);
  font-weight: 700;
  padding: 0.15rem 0.5rem;
  border-radius: 99px;
  text-transform: capitalize;
}

.ai-badge--baja     { background: #d4edda; color: #1a5c30; }
.ai-badge--media    { background: #fff3cd; color: #7a5a00; }
.ai-badge--alta     { background: #ffe0c2; color: #7a3000; }
.ai-badge--muy_alta { background: #f8d7da; color: #7a0010; }

/* Fallas conocidas */
.ai-fallas {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.ai-fallas-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.ai-falla-pill {
  background: var(--cds-white);
  border: 1px solid var(--cds-border-card);
  border-radius: 99px;
  padding: 0.2rem 0.65rem;
  font-size: var(--cds-text-xs);
  cursor: pointer;
  color: var(--cds-text-normal);
  transition: background 0.15s, border-color 0.15s;
  text-align: left;
}

.ai-falla-pill:hover {
  background: var(--cds-primary);
  border-color: var(--cds-primary);
  color: var(--cds-white);
}

/* Cobro options */
.ai-cobro {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.ai-cobro-options {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.ai-cobro-option {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.3rem 0.75rem;
  background: var(--cds-white);
  border: 1px solid var(--cds-border-card);
  border-radius: var(--cds-radius-sm);
  font-size: var(--cds-text-sm);
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s, color 0.15s;
}

.ai-cobro-option input[type="radio"] {
  accent-color: var(--cds-primary);
  cursor: pointer;
}

.ai-cobro-option.is-selected {
  background: var(--cds-primary);
  border-color: var(--cds-primary);
  color: var(--cds-white);
}

/* Notes */
.ai-notas {
  font-size: var(--cds-text-xs);
  color: var(--cds-text-muted);
  padding: 0.5rem 0.65rem;
  background: var(--cds-white);
  border-radius: var(--cds-radius-sm);
  border-left: 2px solid var(--cds-border-card);
  display: flex;
  gap: 0.4rem;
  align-items: flex-start;
  line-height: 1.5;
}

@media (max-width: 768px) {
  .ai-cobro-options {
    gap: 0.3rem;
  }
  .ai-cobro-option {
    font-size: var(--cds-text-xs);
    padding: 0.25rem 0.55rem;
  }
}
</style>
