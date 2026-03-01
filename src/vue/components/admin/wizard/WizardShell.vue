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
        <button class="admin-btn admin-btn-outline" data-testid="wizard-prev" :disabled="currentIndex === 0" @click="prev">
          Volver
        </button>
        <button class="admin-btn admin-btn-primary" data-testid="wizard-next" :disabled="!canContinue" @click="next">
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
@use "@/scss/_core.scss" as *;

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
  border: 1px solid $color-gray-200-legacy;
  background: $color-white;
  font-weight: 600;
  color: $color-gray-500-legacy;
}

.wizard-step.active {
  border-color: $color-primary;
  color: $color-gray-800-legacy;
  background: $color-orange-50-legacy;
}

.wizard-step.done {
  color: $color-gray-800-legacy;
}

.wizard-step-index {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: $color-primary;
  color: $color-white;
  font-size: 0.85rem;
  display: grid;
  place-items: center;
}

.wizard-actions {
  display: flex;
  gap: 0.75rem;
}

.wizard-body {
  background: $color-white;
  border-radius: 12px;
  border: 1px solid $color-gray-200-legacy;
  padding: 1.5rem;
}
</style>
