<template>
  <div class="cotizador-card">
    <CotizadorStepHeader badge="Paso 2 de 4" title="Síntomas del equipo">
      <template #description>
        Selecciona todo lo que presenta tu <strong>{{ selectedBrandName }} {{ selectedModelName }}</strong>.
      </template>
    </CotizadorStepHeader>

    <div v-if="loading" class="loading-row">
      <span class="spinner"></span> Cargando fallas disponibles…
    </div>

    <div v-else class="faults-grid">
      <label
        v-for="fault in faults"
        :key="fault.id"
        class="fault-card"
        :class="{ 'fault-card--selected': selectedFaultIds.includes(fault.id) }"
      >
        <input
          type="checkbox"
          class="sr-only"
          :value="fault.id"
          :checked="selectedFaultIds.includes(fault.id)"
          @change="emit('toggle-fault', fault.id)"
        />
        <span class="fault-icon">
          <i :class="`fa-solid ${fault.icon || 'fa-wrench'}`"></i>
        </span>
        <span class="fault-name">{{ fault.name }}</span>
        <span class="fault-desc">{{ fault.description }}</span>
        <span v-if="fault.isPrecedence" class="fault-precedence">
          Anula otras fallas
        </span>
      </label>
    </div>

    <TurnstileWidget
      v-if="!loading"
      :key="quoteTurnstileRenderKey"
      @verify="emit('quote-verify', $event)"
    />

    <div class="actions">
      <button class="btn-secondary" @click="emit('back')">← Atrás</button>
      <button
        class="btn-primary"
        :disabled="!canContinueStep2 || loading"
        @click="emit('continue')"
      >
        <span v-if="loading"><span class="spinner spinner--sm"></span> Calculando…</span>
        <span v-else>Ver estimación →</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import CotizadorStepHeader from '@/components/business/CotizadorStepHeader.vue'
import TurnstileWidget from '@/components/widgets/TurnstileWidget.vue'

defineProps({
  loading: {
    type: Boolean,
    default: false
  },
  selectedBrandName: {
    type: String,
    required: true
  },
  selectedModelName: {
    type: String,
    required: true
  },
  faults: {
    type: Array,
    default: () => []
  },
  selectedFaultIds: {
    type: Array,
    default: () => []
  },
  quoteTurnstileRenderKey: {
    type: Number,
    default: 0
  },
  canContinueStep2: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['toggle-fault', 'quote-verify', 'back', 'continue'])
</script>

<style scoped>
@import './cotizadorStepShared.css';

.faults-grid {
  display: grid;
  gap: var(--cds-space-xs);
}

.fault-card {
  display: grid;
  grid-template-columns: 2rem 1fr;
  grid-template-rows: auto auto auto;
  column-gap: 0.6rem;
  row-gap: 0.1rem;
  padding: 0.7rem 0.85rem;
  border: 1px solid var(--cds-border-input);
  border-radius: var(--cds-radius-sm);
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
}

.fault-card:hover {
  border-color: color-mix(in srgb, var(--cds-primary) 40%, white);
  background: color-mix(in srgb, var(--cds-primary) 4%, white);
}

.fault-card--selected {
  border-color: var(--cds-primary);
  background: color-mix(in srgb, var(--cds-primary) 8%, white);
}

.fault-icon {
  grid-row: 1 / 3;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--cds-primary);
  font-size: 1rem;
}

.fault-name {
  font-weight: 600;
  font-size: var(--cds-text-sm);
  align-self: end;
}

.fault-desc {
  grid-column: 2;
  font-size: var(--cds-text-xs);
  color: var(--cds-text-muted);
  line-height: 1.4;
}

.fault-precedence {
  grid-column: 2;
  font-size: var(--cds-text-xs);
  font-weight: 600;
  color: var(--cds-primary);
  margin-top: 0.1rem;
}

@media (min-width: 640px) {
  .faults-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (min-width: 1024px) {
  .faults-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
</style>
