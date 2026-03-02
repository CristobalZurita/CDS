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
