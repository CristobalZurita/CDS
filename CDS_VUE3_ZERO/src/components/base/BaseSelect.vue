<template>
  <div class="base-select-wrapper" :class="wrapperClasses">
    <label v-if="label" :for="selectId" class="base-select-label">
      {{ label }}
      <span v-if="required" class="required-mark">*</span>
    </label>
    
    <div class="base-select-container">
      <select
        :id="selectId"
        :value="modelValue"
        :disabled="disabled"
        :required="required"
        :class="selectClasses"
        @change="handleChange"
        @blur="$emit('blur', $event)"
      >
        <option v-if="placeholder" value="" disabled>
          {{ placeholder }}
        </option>
        
        <option 
          v-for="option in normalizedOptions" 
          :key="option.value" 
          :value="option.value"
          :disabled="option.disabled"
        >
          {{ option.label }}
        </option>
      </select>
      
      <!-- Icono de flecha -->
      <span class="select-arrow">
        <svg viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
          <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
        </svg>
      </span>
    </div>
    
    <div v-if="hint || error" class="base-select-hint" :class="{ 'is-error': error }">
      {{ error || hint }}
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: { type: [String, Number], default: '' },
  label: { type: String, default: '' },
  options: { 
    type: Array, 
    required: true,
    // Cada opción: { value, label, disabled? } o string
  },
  placeholder: { type: String, default: 'Seleccionar...' },
  hint: { type: String, default: '' },
  error: { type: String, default: '' },
  disabled: { type: Boolean, default: false },
  required: { type: Boolean, default: false },
  id: { type: String, default: '' },
  size: { 
    type: String, 
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg'].includes(value)
  },
  valueKey: { type: String, default: 'value' },
  labelKey: { type: String, default: 'label' }
})

const emit = defineEmits(['update:modelValue', 'change', 'blur'])

const selectId = computed(() => props.id || `select-${Math.random().toString(36).substr(2, 9)}`)

// Normalizar opciones (soporta array de strings u objetos)
const normalizedOptions = computed(() => {
  return props.options.map(opt => {
    if (typeof opt === 'string') {
      return { value: opt, label: opt, disabled: false }
    }
    return {
      value: opt[props.valueKey] ?? opt.value,
      label: opt[props.labelKey] ?? opt.label,
      disabled: opt.disabled || false
    }
  })
})

const wrapperClasses = computed(() => ({
  'has-error': !!props.error,
  'is-disabled': props.disabled,
  [`size-${props.size}`]: true
}))

const selectClasses = computed(() => [
  'base-select',
  {
    'is-invalid': !!props.error,
    [`select-${props.size}`]: true
  }
])

function handleChange(event) {
  let value = event.target.value
  
  // Si el valor original era número, convertir
  if (typeof props.modelValue === 'number' && value !== '') {
    value = Number(value)
  }
  
  emit('update:modelValue', value)
  emit('change', value)
}
</script>

<style scoped>
.base-select-wrapper {
  display: grid;
  gap: 0.35rem;
}

.base-select-label {
  font-size: var(--cds-text-sm);
  font-weight: 500;
  color: var(--cds-text-normal);
}

.required-mark {
  color: var(--cds-danger);
}

.base-select-container {
  position: relative;
}

.base-select {
  width: 100%;
  min-height: 44px;
  padding: 0.65rem 2.5rem 0.65rem 0.9rem;
  border: 1px solid color-mix(in srgb, var(--cds-light) 65%, white);
  border-radius: var(--cds-radius-sm);
  background: var(--cds-white);
  color: var(--cds-text-normal);
  font-size: var(--cds-text-base);
  appearance: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.base-select:hover:not(:disabled) {
  border-color: color-mix(in srgb, var(--cds-light) 40%, white);
}

.base-select:focus {
  outline: none;
  border-color: var(--cds-primary);
  box-shadow: var(--cds-focus-ring);
}

.base-select:disabled {
  background: var(--cds-light-1);
  cursor: not-allowed;
  opacity: 0.7;
}

.base-select.is-invalid {
  border-color: var(--cds-danger);
  background: var(--cds-invalid-bg);
}

/* Tamaños */
.size-sm .base-select {
  min-height: 38px;
  padding: 0.5rem 2.25rem 0.5rem 0.75rem;
  font-size: var(--cds-text-sm);
}

.size-lg .base-select {
  min-height: 52px;
  padding: 0.8rem 2.5rem 0.8rem 1rem;
  font-size: var(--cds-text-lg);
}

/* Icono flecha */
.select-arrow {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  width: 1.25rem;
  height: 1.25rem;
  color: var(--cds-light-5);
  pointer-events: none;
}

/* Hint/Error */
.base-select-hint {
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
  min-height: 1.25rem;
}

.base-select-hint.is-error {
  color: var(--cds-danger);
}

.base-select-wrapper.has-error .base-select-label {
  color: var(--cds-danger);
}
</style>
