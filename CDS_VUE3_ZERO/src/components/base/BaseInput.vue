<template>
  <div class="base-input-wrapper" :class="wrapperClasses">
    <label v-if="label" :for="inputId" class="base-input-label">
      {{ label }}
      <span v-if="required" class="required-mark">*</span>
    </label>
    
    <div class="base-input-container">
      <!-- Slot prefijo (ej: símbolo de moneda, unidad) -->
      <span v-if="$slots.prefix" class="input-slot input-slot--prefix">
        <slot name="prefix" />
      </span>

      <input
        :id="inputId"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :readonly="readonly"
        :required="required"
        :min="min"
        :max="max"
        :step="step"
        :pattern="pattern"
        :autocomplete="autocomplete"
        :inputmode="inputmode"
        :class="inputClasses"
        @input="handleInput"
        @blur="handleBlur"
        @focus="$emit('focus', $event)"
        @keydown="$emit('keydown', $event)"
      />

      <!-- Slot sufijo (ej: unidad de medida) -->
      <span v-if="$slots.suffix" class="input-slot input-slot--suffix">
        <slot name="suffix" />
      </span>

      <!-- Icono derecha (legacy) -->
      <span v-if="$slots.rightIcon || rightIcon" class="input-icon-right">
        <slot name="rightIcon">
          <i v-if="rightIcon" :class="rightIcon"></i>
        </slot>
      </span>
    </div>
    
    <!-- Mensaje de ayuda o error -->
    <div v-if="hint || error || $slots.hint" class="base-input-hint" :class="{ 'is-error': error }">
      <slot name="hint">
        {{ error || hint }}
      </slot>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: { type: [String, Number], default: '' },
  modelModifiers: { type: Object, default: () => ({}) },
  label: { type: String, default: '' },
  type: { 
    type: String, 
    default: 'text',
    validator: (value) => [
      'text', 'email', 'tel', 'password', 'number', 
      'url', 'search', 'date', 'datetime-local', 'time'
    ].includes(value)
  },
  placeholder: { type: String, default: '' },
  hint: { type: String, default: '' },
  error: { type: String, default: '' },
  disabled: { type: Boolean, default: false },
  readonly: { type: Boolean, default: false },
  required: { type: Boolean, default: false },
  min: { type: [String, Number], default: undefined },
  max: { type: [String, Number], default: undefined },
  step: { type: [String, Number], default: undefined },
  pattern: { type: String, default: '' },
  autocomplete: { type: String, default: '' },
  inputmode: { type: String, default: '' },
  rightIcon: { type: String, default: '' },
  id: { type: String, default: '' },
  size: { 
    type: String, 
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg'].includes(value)
  }
})

const emit = defineEmits(['update:modelValue', 'blur', 'focus', 'keydown', 'validate'])

// ID único para el input
const inputId = computed(() => props.id || `input-${Math.random().toString(36).substr(2, 9)}`)

// Clases del wrapper
const wrapperClasses = computed(() => ({
  'has-error': !!props.error,
  'is-disabled': props.disabled,
  [`size-${props.size}`]: true
}))

// Clases del input
const inputClasses = computed(() => [
  'base-input',
  {
    'has-right-icon': props.rightIcon || props.$slots?.rightIcon,
    'is-invalid': !!props.error,
    [`input-${props.size}`]: true
  }
])

// Handler de input con modificadores y validación por tipo
function handleInput(event) {
  let value = event.target.value

  if (props.modelModifiers.trim) {
    value = value.trim()
  }

  if (props.modelModifiers.number) {
    const parsed = Number(value)
    emit('update:modelValue', Number.isNaN(parsed) ? '' : parsed)
    return
  }

  // Compatibilidad con type="number" sin modificador
  if (props.type === 'number' && value !== '') {
    value = Number(value)
  }

  emit('update:modelValue', value)
}

// Handler de blur con validación
function handleBlur(event) {
  emit('blur', event)
  
  // Validación inline básica
  const validation = validateInput(event.target.value)
  if (!validation.valid) {
    emit('validate', validation)
  }
}

// Validación por tipo
function validateInput(value) {
  // Si no es requerido y está vacío, es válido
  if (!props.required && (value === '' || value === null || value === undefined)) {
    return { valid: true, message: '' }
  }
  
  // Requerido
  if (props.required && (value === '' || value === null || value === undefined)) {
    return { valid: false, message: 'Este campo es obligatorio' }
  }
  
  // Validación por tipo
  switch (props.type) {
    case 'email':
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
        return { valid: false, message: 'Ingresa un email válido' }
      }
      break
      
    case 'tel':
      // Teléfono chileno: +569XXXXXXXX o 9XXXXXXXX
      if (!/^(\+?56)?\s?9\s?\d{4}\s?\d{4}$/.test(value.replace(/\s/g, ''))) {
        return { valid: false, message: 'Ingresa un teléfono válido (ej: +56912345678)' }
      }
      break
      
    case 'number':
      const num = Number(value)
      if (isNaN(num)) {
        return { valid: false, message: 'Debe ser un número válido' }
      }
      if (props.min !== undefined && num < Number(props.min)) {
        return { valid: false, message: `El mínimo es ${props.min}` }
      }
      if (props.max !== undefined && num > Number(props.max)) {
        return { valid: false, message: `El máximo es ${props.max}` }
      }
      break
      
    case 'text':
      // Si el patrón indica solo letras
      if (props.pattern === 'letters-only' && !/^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/.test(value)) {
        return { valid: false, message: 'Solo se permiten letras' }
      }
      // Si el patrón indica solo números
      if (props.pattern === 'numbers-only' && !/^\d+$/.test(value)) {
        return { valid: false, message: 'Solo se permiten números' }
      }
      // RUT chileno
      if (props.pattern === 'rut' && !/^[0-9]{1,2}\.?[0-9]{3}\.?[0-9]{3}-?[0-9kK]$/.test(value)) {
        return { valid: false, message: 'RUT inválido' }
      }
      break
  }
  
  return { valid: true, message: '' }
}
</script>

<style scoped>
.base-input-wrapper {
  display: grid;
  gap: 0.35rem;
}

.base-input-label {
  font-size: var(--cds-text-sm);
  font-weight: 500;
  color: var(--cds-text-normal);
}

.required-mark {
  color: var(--cds-danger);
}

.base-input-container {
  position: relative;
  display: flex;
  align-items: center;
}

.base-input {
  width: 100%;
  min-height: 44px;
  padding: 0.65rem 0.9rem;
  border: 1px solid color-mix(in srgb, var(--cds-light) 65%, white);
  border-radius: var(--cds-radius-sm);
  background: var(--cds-white);
  color: var(--cds-text-normal);
  font-size: var(--cds-text-base);
  transition: all 0.2s ease;
}

.base-input::placeholder {
  color: var(--cds-light-5);
}

.base-input:hover:not(:disabled) {
  border-color: color-mix(in srgb, var(--cds-light) 40%, white);
}

.base-input:focus {
  outline: none;
  border-color: var(--cds-primary);
  box-shadow: var(--cds-focus-ring);
}

.base-input:disabled {
  background: var(--cds-light-1);
  cursor: not-allowed;
  opacity: 0.7;
}

/* Estados de validación */
.base-input.is-invalid {
  border-color: var(--cds-danger);
  background: var(--cds-invalid-bg);
}

.base-input.is-invalid:focus {
  box-shadow: var(--cds-focus-ring-danger);
}

/* Tamaños */
.size-sm .base-input {
  min-height: 38px;
  padding: 0.5rem 0.75rem;
  font-size: var(--cds-text-sm);
}

.size-lg .base-input {
  min-height: 52px;
  padding: 0.8rem 1rem;
  font-size: var(--cds-text-lg);
}

/* Slots prefix / suffix */
.input-slot {
  display: inline-flex;
  align-items: center;
  color: var(--cds-text-muted);
  font-size: var(--cds-text-sm);
  flex-shrink: 0;
}

.input-slot--prefix { padding-right: 0.4rem; }
.input-slot--suffix { padding-left: 0.4rem; }

/* Icono derecha */
.base-input.has-right-icon {
  padding-right: 2.5rem;
}

.input-icon-right {
  position: absolute;
  right: 0.75rem;
  color: var(--cds-light-5);
  pointer-events: none;
}

/* Hint/Error */
.base-input-hint {
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
  min-height: 1.25rem;
}

.base-input-hint.is-error {
  color: var(--cds-danger);
}

/* Wrapper con error */
.base-input-wrapper.has-error .base-input-label {
  color: var(--cds-danger);
}
</style>
