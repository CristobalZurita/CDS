<template>
  <div class="form-field" :class="fieldClasses">
    <!-- Label con tooltip opcional -->
    <div v-if="label" class="field-header">
      <label :for="inputId" class="field-label">
        {{ label }}
        <span v-if="required" class="required-mark">*</span>
      </label>
      <button
        v-if="helpText"
        type="button"
        class="help-trigger"
        @click="showHelp = !showHelp"
        :aria-expanded="showHelp"
      >
        <span class="sr-only">Ayuda</span>
        ?
      </button>
    </div>
    
    <!-- Tooltip de ayuda -->
    <div v-if="helpText && showHelp" class="help-text">
      {{ helpText }}
    </div>
    
    <!-- Input dinámico según tipo -->
    <div class="field-input-wrapper">
      <component
        :is="inputComponent"
        :id="inputId"
        :modelValue="modelValue"
        @update:modelValue="$emit('update:modelValue', $event)"
        :type="type"
        :placeholder="placeholder"
        :disabled="disabled"
        :required="required"
        :options="options"
        :rows="rows"
        :error="error"
        :size="size"
        v-bind="$attrs"
      />
      
      <!-- Icono de estado -->
      <span v-if="showStatusIcon && !error" class="status-icon valid">✓</span>
      <span v-if="error" class="status-icon invalid">✕</span>
    </div>
    
    <!-- Error o hint -->
    <div class="field-footer">
      <span v-if="error" class="field-error">
        {{ error }}
      </span>
      <span v-else-if="hint" class="field-hint">
        {{ hint }}
      </span>
      <span v-if="maxlength && showCount" class="char-count" :class="countClass">
        {{ charCount }}/{{ maxlength }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import BaseInput from '../base/BaseInput.vue'
import BaseSelect from '../base/BaseSelect.vue'
import BaseTextarea from '../base/BaseTextarea.vue'
import BaseCheckbox from '../base/BaseCheckbox.vue'

const props = defineProps({
  // Identificación
  name: { type: String, default: '' },
  label: { type: String, default: '' },
  
  // Valor
  modelValue: { type: [String, Number, Boolean], default: '' },
  
  // Tipo de campo
  type: { 
    type: String, 
    default: 'text',
    validator: (v) => ['text', 'email', 'tel', 'number', 'select', 'textarea', 'checkbox', 'date'].includes(v)
  },
  
  // Opciones para select
  options: { type: Array, default: () => [] },
  
  // Configuración
  placeholder: { type: String, default: '' },
  hint: { type: String, default: '' },
  helpText: { type: String, default: '' },
  error: { type: String, default: '' },
  disabled: { type: Boolean, default: false },
  required: { type: Boolean, default: false },
  
  // Tamaño
  size: { type: String, default: 'md' },
  
  // Para textarea
  rows: { type: Number, default: 3 },
  
  // Validación visual
  showStatusIcon: { type: Boolean, default: false },
  showCount: { type: Boolean, default: false },
  maxlength: { type: Number, default: undefined }
})

const emit = defineEmits(['update:modelValue', 'blur', 'focus'])

const showHelp = ref(false)

const inputId = computed(() => props.name || `field-${Math.random().toString(36).substr(2, 9)}`)

const inputComponent = computed(() => {
  switch (props.type) {
    case 'select': return BaseSelect
    case 'textarea': return BaseTextarea
    case 'checkbox': return BaseCheckbox
    default: return BaseInput
  }
})

const fieldClasses = computed(() => ({
  'has-error': !!props.error,
  'is-disabled': props.disabled,
  [`size-${props.size}`]: true,
  'field-checkbox': props.type === 'checkbox'
}))

const charCount = computed(() => String(props.modelValue || '').length)

const countClass = computed(() => {
  if (!props.maxlength) return ''
  const ratio = charCount.value / props.maxlength
  if (ratio > 1) return 'is-exceeded'
  if (ratio > 0.9) return 'is-warning'
  return ''
})
</script>

<style scoped>
.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.form-field.field-checkbox {
  flex-direction: row;
  align-items: flex-start;
  gap: 0.75rem;
}

/* Header con label y ayuda */
.field-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.field-label {
  font-size: var(--cds-text-sm);
  font-weight: 500;
  color: var(--cds-text-normal);
}

.required-mark {
  color: var(--cds-danger);
}

.help-trigger {
  width: 1.25rem;
  height: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  border: 1px solid var(--cds-light-4);
  background: var(--cds-light-1);
  color: var(--cds-text-muted);
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.help-trigger:hover {
  background: var(--cds-primary);
  border-color: var(--cds-primary);
  color: var(--cds-white);
}

/* Texto de ayuda */
.help-text {
  padding: 0.75rem;
  background: color-mix(in srgb, var(--cds-primary) 8%, white);
  border-left: 3px solid var(--cds-primary);
  border-radius: 0 0.35rem 0.35rem 0;
  font-size: var(--cds-text-sm);
  color: var(--cds-text-normal);
}

/* Input wrapper con iconos de estado */
.field-input-wrapper {
  position: relative;
}

.status-icon {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  width: 1.25rem;
  height: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-size: 0.75rem;
  font-weight: bold;
  pointer-events: none;
}

.status-icon.valid {
  background: var(--cds-success);
  color: var(--cds-white);
}

.status-icon.invalid {
  background: var(--cds-danger);
  color: var(--cds-white);
}

/* Footer */
.field-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
  min-height: 1.25rem;
}

.field-error {
  font-size: var(--cds-text-sm);
  color: var(--cds-danger);
}

.field-hint {
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
}

.char-count {
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
  white-space: nowrap;
}

.char-count.is-warning {
  color: var(--cds-warning);
  font-weight: 500;
}

.char-count.is-exceeded {
  color: var(--cds-danger);
  font-weight: 600;
}

/* Estados */
.form-field.has-error .field-label {
  color: var(--cds-danger);
}
</style>
