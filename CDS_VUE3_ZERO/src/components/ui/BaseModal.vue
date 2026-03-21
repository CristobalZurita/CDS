<template>
  <div v-if="modelValue" class="base-modal__overlay" @click.self="close">
    <div class="base-modal__container" role="dialog" aria-modal="true">
      <button class="base-modal__close" @click="close" aria-label="Cerrar">
        <span aria-hidden="true">&times;</span>
      </button>
      <div class="base-modal__content">
        <slot />
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  modelValue: { type: Boolean, required: true }
})
const emit = defineEmits(['update:modelValue'])

function close() {
  emit('update:modelValue', false)
}
</script>

<style scoped>
.base-modal__overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.45);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}
.base-modal__container {
  background: var(--cds-surface-1, #fff);
  border-radius: 1.1rem;
  box-shadow: 0 8px 32px rgba(0,0,0,0.18);
  max-width: 38rem;
  width: 92vw;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
  padding: 2.2rem 1.5rem 1.5rem 1.5rem;
}
.base-modal__close {
  position: absolute;
  top: 1.1rem;
  right: 1.1rem;
  background: none;
  border: none;
  font-size: 2.1rem;
  color: var(--cds-text-muted, #888);
  cursor: pointer;
  z-index: 1;
}
.base-modal__content {
  margin-top: 0.5rem;
}
</style>
