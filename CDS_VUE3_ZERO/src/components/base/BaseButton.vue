<template>
  <button
    ref="buttonRef"
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
import { computed, ref } from 'vue'

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
const buttonRef = ref(null)

const buttonClasses = computed(() => [
  `variant-${props.variant}`,
  `size-${props.size}`,
  {
    'is-block': props.block,
    'is-rounded': props.rounded,
    'is-loading': props.loading
  }
])

defineExpose({
  focus: () => buttonRef.value?.focus()
})
</script>

<style scoped>
.base-button {
  --button-min-height: 44px;
  --button-pad-block: 0.75rem;
  --button-pad-inline: 1.25rem;
  --button-font-size: var(--cds-text-base);
  --button-bg: transparent;
  --button-border: transparent;
  --button-text: var(--cds-text-normal);
  --button-hover-bg: var(--button-bg);
  --button-hover-border: var(--button-border);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  border: 2px solid transparent;
  border-radius: var(--cds-radius-sm);
  min-height: var(--button-min-height);
  padding: var(--button-pad-block) var(--button-pad-inline);
  font-size: var(--button-font-size);
  font-weight: var(--cds-font-semibold);
  line-height: 1;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  background: var(--button-bg);
  border-color: var(--button-border);
  color: var(--button-text);
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
  --button-min-height: 36px;
  --button-pad-block: 0.5rem;
  --button-pad-inline: 0.875rem;
  --button-font-size: var(--cds-text-sm);
}

.size-md {
  --button-min-height: 44px;
  --button-pad-block: 0.75rem;
  --button-pad-inline: 1.25rem;
  --button-font-size: var(--cds-text-base);
}

.size-lg {
  --button-min-height: 52px;
  --button-pad-block: 1rem;
  --button-pad-inline: 1.75rem;
  --button-font-size: var(--cds-text-lg);
}

/* Variantes */
.variant-primary {
  --button-bg: var(--cds-primary);
  --button-border: var(--cds-primary);
  --button-text: var(--cds-white);
  --button-hover-bg: var(--cds-primary-hover);
  --button-hover-border: var(--cds-primary-hover);
}

.variant-secondary {
  --button-bg: var(--cds-dark);
  --button-border: var(--cds-dark);
  --button-text: var(--cds-white);
  --button-hover-bg: var(--cds-dark-hover);
  --button-hover-border: var(--cds-dark-hover);
}

.variant-ghost {
  --button-bg: transparent;
  --button-border: var(--cds-border-card);
  --button-text: var(--cds-text-normal);
  --button-hover-bg: var(--cds-surface-2);
  --button-hover-border: var(--cds-border-input);
}

.variant-danger {
  --button-bg: var(--cds-danger);
  --button-border: var(--cds-danger);
  --button-text: var(--cds-white);
  --button-hover-bg: #8d412f;
  --button-hover-border: #8d412f;
}

.variant-success {
  --button-bg: var(--cds-success);
  --button-border: var(--cds-success);
  --button-text: var(--cds-white);
  --button-hover-bg: #5d6738;
  --button-hover-border: #5d6738;
}

.variant-warning {
  --button-bg: var(--cds-warning);
  --button-border: var(--cds-warning);
  --button-text: var(--cds-white);
  --button-hover-bg: #a47830;
  --button-hover-border: #a47830;
}

.base-button:hover:not(:disabled) {
  background: var(--button-hover-bg);
  border-color: var(--button-hover-border);
}

/* Modificadores */
.is-block {
  width: 100%;
}

.is-rounded {
  border-radius: var(--cds-radius-pill);
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
