<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    class="base-button"
    :class="buttonClasses"
    @click="$emit('click', $event)"
  >
    <!-- Loading spinner -->
    <span v-if="loading" class="btn-spinner" aria-hidden="true"></span>
    
    <!-- Prefix slot -->
    <span v-if="$slots.prefix && !loading" class="btn-slot prefix">
      <slot name="prefix" />
    </span>
    
    <!-- Content -->
    <span class="btn-content" :class="{ 'is-loading': loading }">
      <slot>{{ loading ? (loadingText || 'Cargando...') : '' }}</slot>
    </span>
    
    <!-- Suffix slot -->
    <span v-if="$slots.suffix && !loading" class="btn-slot suffix">
      <slot name="suffix" />
    </span>
  </button>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  type: { 
    type: String, 
    default: 'button',
    validator: (v) => ['button', 'submit', 'reset'].includes(v)
  },
  variant: { 
    type: String, 
    default: 'primary',
    validator: (v) => ['primary', 'secondary', 'ghost', 'danger', 'success', 'warning'].includes(v)
  },
  size: {
    type: String,
    default: 'md',
    validator: (v) => ['sm', 'md', 'lg'].includes(v)
  },
  disabled: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
  loadingText: { type: String, default: '' },
  block: { type: Boolean, default: false },
  rounded: { type: Boolean, default: false }
})

const emit = defineEmits(['click'])

const buttonClasses = computed(() => [
  `variant-${props.variant}`,
  `size-${props.size}`,
  {
    'is-block': props.block,
    'is-rounded': props.rounded,
    'is-loading': props.loading
  }
])
</script>

<style scoped>
.base-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  border: 2px solid transparent;
  border-radius: var(--cds-radius-sm);
  font-weight: 600;
  line-height: 1;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.base-button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: var(--cds-shadow-sm);
}

.base-button:active:not(:disabled) {
  transform: translateY(0);
}

.base-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Tamaños */
.size-sm {
  min-height: 36px;
  padding: 0.5rem 0.875rem;
  font-size: var(--cds-text-sm);
}

.size-md {
  min-height: 44px;
  padding: 0.75rem 1.25rem;
  font-size: var(--cds-text-base);
}

.size-lg {
  min-height: 52px;
  padding: 1rem 1.75rem;
  font-size: var(--cds-text-lg);
}

/* Variantes */
.variant-primary {
  background: var(--cds-primary);
  border-color: var(--cds-primary);
  color: var(--cds-white);
}

.variant-primary:hover:not(:disabled) {
  background: color-mix(in srgb, var(--cds-primary) 90%, black);
  border-color: color-mix(in srgb, var(--cds-primary) 90%, black);
}

.variant-secondary {
  background: var(--cds-dark);
  border-color: var(--cds-dark);
  color: var(--cds-white);
}

.variant-secondary:hover:not(:disabled) {
  background: color-mix(in srgb, var(--cds-dark) 80%, black);
  border-color: color-mix(in srgb, var(--cds-dark) 80%, black);
}

.variant-ghost {
  background: transparent;
  border-color: var(--cds-light-5);
  color: var(--cds-text-normal);
}

.variant-ghost:hover:not(:disabled) {
  background: color-mix(in srgb, var(--cds-light) 10%, white);
  border-color: var(--cds-light-4);
}

.variant-danger {
  background: var(--cds-danger);
  border-color: var(--cds-danger);
  color: var(--cds-white);
}

.variant-danger:hover:not(:disabled) {
  background: color-mix(in srgb, var(--cds-danger) 90%, black);
  border-color: color-mix(in srgb, var(--cds-danger) 90%, black);
}

.variant-success {
  background: var(--cds-success);
  border-color: var(--cds-success);
  color: var(--cds-white);
}

.variant-success:hover:not(:disabled) {
  background: color-mix(in srgb, var(--cds-success) 90%, black);
  border-color: color-mix(in srgb, var(--cds-success) 90%, black);
}

.variant-warning {
  background: var(--cds-warning);
  border-color: var(--cds-warning);
  color: var(--cds-dark);
}

.variant-warning:hover:not(:disabled) {
  background: color-mix(in srgb, var(--cds-warning) 90%, black);
  border-color: color-mix(in srgb, var(--cds-warning) 90%, black);
}

/* Modificadores */
.is-block {
  width: 100%;
}

.is-rounded {
  border-radius: 9999px;
}

.is-loading {
  cursor: wait;
}

/* Spinner */
.btn-spinner {
  width: 1em;
  height: 1em;
  border: 2px solid currentColor;
  border-right-color: transparent;
  border-radius: 50%;
  animation: spin 0.75s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Slots */
.btn-slot {
  display: inline-flex;
  align-items: center;
}

.btn-content.is-loading {
  opacity: 0.8;
}
</style>
