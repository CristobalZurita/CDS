<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    class="base-button"
    :class="[`base-button--${variant}`]"
    @click="$emit('click', $event)"
  >
    <span v-if="$slots.prefix && !loading" class="base-button__slot">
      <slot name="prefix" />
    </span>
    <span v-if="loading">{{ loadingText || 'Procesando...' }}</span>
    <span v-else><slot /></span>
    <span v-if="$slots.suffix && !loading" class="base-button__slot">
      <slot name="suffix" />
    </span>
  </button>
</template>

<script setup>
defineProps({
  type: { type: String, default: 'button' },
  variant: { type: String, default: 'primary' },
  disabled: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
  loadingText: { type: String, default: '' }
})

defineEmits({
  click: (event) => event instanceof Event
})
</script>

<style scoped>
.base-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  width: 100%;
  min-height: 44px;
  border: 2px solid transparent;
  border-radius: 0.5rem;
  padding: 0.75rem 1rem;
  font-size: var(--cds-text-base);
  font-weight: var(--cds-font-semibold);
  line-height: 1;
  cursor: pointer;
}

.base-button:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.base-button--primary {
  background: var(--cds-primary);
  border-color: var(--cds-primary);
  color: var(--cds-white);
}

.base-button--secondary {
  background: var(--cds-dark);
  border-color: var(--cds-dark);
  color: var(--cds-white);
}

.base-button--ghost {
  background: transparent;
  border-color: var(--cds-light-5);
  color: var(--cds-text-normal);
}

.base-button__slot {
  display: inline-flex;
  align-items: center;
}
</style>
