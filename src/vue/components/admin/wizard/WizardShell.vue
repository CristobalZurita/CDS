<template>
  <div class="wizard-shell">
    <div class="wizard-header">
      <div class="wizard-steps">
        <div
          v-for="(step, index) in steps"
          :key="step.key"
          class="wizard-step"
          :class="{ active: index === currentIndex, done: index < currentIndex }"
        >
          <span class="wizard-step-index">{{ index + 1 }}</span>
          <span class="wizard-step-title">{{ step.title }}</span>
        </div>
      </div>
      <div class="wizard-actions">
        <button class="admin-btn admin-btn-outline" :disabled="currentIndex === 0" @click="prev">
          Volver
        </button>
        <button class="admin-btn admin-btn-primary" :disabled="!canContinue" @click="next">
          {{ isLast ? 'Finalizar' : 'Continuar' }}
        </button>
      </div>
    </div>
    <div class="wizard-body">
      <slot :current-index="currentIndex" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  steps: { type: Array, default: () => [] },
  currentIndex: { type: Number, default: 0 },
  canContinue: { type: Boolean, default: true }
})

const emit = defineEmits(['next', 'prev'])

const isLast = computed(() => props.currentIndex >= props.steps.length - 1)

const next = () => emit('next')
const prev = () => emit('prev')
</script>

<style scoped lang="scss">
.wizard-shell {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.wizard-header {
  display: flex;
  justify-content: space-between;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.wizard-steps {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.wizard-step {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.6rem 0.8rem;
  border-radius: 10px;
  border: 1px solid #e5e7eb;
  background: #fff;
  font-weight: 600;
  color: #6b7280;
}

.wizard-step.active {
  border-color: #ec6b00;
  color: #1f2937;
  background: #fff6eb;
}

.wizard-step.done {
  color: #1f2937;
}

.wizard-step-index {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: #ec6b00;
  color: #fff;
  font-size: 0.85rem;
  display: grid;
  place-items: center;
}

.wizard-actions {
  display: flex;
  gap: 0.75rem;
}

.wizard-body {
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  padding: 1.5rem;
}
</style>
