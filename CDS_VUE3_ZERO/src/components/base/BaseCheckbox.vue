<template>
  <label class="base-checkbox" :class="wrapperClasses">
    <input
      ref="checkboxRef"
      type="checkbox"
      :checked="modelValue"
      :value="trueValue"
      :disabled="disabled"
      :required="required"
      :class="checkboxClasses"
      v-bind="attrs"
      @change="handleChange"
    />
    
    <span class="checkbox-box" aria-hidden="true">
      <svg v-if="modelValue" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
      </svg>
    </span>
    
    <span v-if="label" class="checkbox-label">
      {{ label }}
      <span v-if="required" class="required-mark">*</span>
    </span>
  </label>
  
  <div v-if="hint || error" class="checkbox-hint" :class="{ 'is-error': error }">
    {{ error || hint }}
  </div>
</template>

<script setup>
import { computed, ref, useAttrs } from 'vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  label: { type: String, default: '' },
  trueValue: { type: [Boolean, String, Number], default: true },
  falseValue: { type: [Boolean, String, Number], default: false },
  hint: { type: String, default: '' },
  error: { type: String, default: '' },
  disabled: { type: Boolean, default: false },
  required: { type: Boolean, default: false },
  size: { 
    type: String, 
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg'].includes(value)
  }
})

const emit = defineEmits(['update:modelValue', 'change'])
const attrs = useAttrs()
const checkboxRef = ref(null)

const wrapperClasses = computed(() => ({
  'has-error': !!props.error,
  'is-disabled': props.disabled,
  [`size-${props.size}`]: true
}))

const checkboxClasses = computed(() => [
  'checkbox-input',
  {
    'is-invalid': !!props.error
  }
])

function handleChange(event) {
  const value = event.target.checked ? props.trueValue : props.falseValue
  emit('update:modelValue', value)
  emit('change', value)
}

defineExpose({
  focus: () => checkboxRef.value?.focus()
})
</script>

<style scoped>
.base-checkbox {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.base-checkbox.is-disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.checkbox-input {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.checkbox-box {
  width: 1.25rem;
  height: 1.25rem;
  border: 2px solid var(--cds-border-input);
  border-radius: 0.25rem;
  background: var(--cds-white);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.checkbox-box svg {
  width: 0.875rem;
  height: 0.875rem;
  color: var(--cds-white);
  opacity: 0;
  transform: scale(0.5);
  transition: all 0.15s ease;
}

/* Estados del checkbox */
.checkbox-input:checked + .checkbox-box {
  background: var(--cds-primary);
  border-color: var(--cds-primary);
}

.checkbox-input:checked + .checkbox-box svg {
  opacity: 1;
  transform: scale(1);
}

.checkbox-input:focus + .checkbox-box {
  box-shadow: var(--cds-focus-ring);
}

.checkbox-input:disabled + .checkbox-box {
  background: var(--cds-light-2);
  border-color: var(--cds-light-4);
}

.checkbox-input.is-invalid + .checkbox-box {
  border-color: var(--cds-danger);
}

.checkbox-input.is-invalid:checked + .checkbox-box {
  background: var(--cds-danger);
}

/* Label */
.checkbox-label {
  font-size: var(--cds-text-base);
  color: var(--cds-text-normal);
  user-select: none;
}

.required-mark {
  color: var(--cds-danger);
}

/* Tamaños */
.size-sm .checkbox-box {
  width: 1rem;
  height: 1rem;
}

.size-sm .checkbox-box svg {
  width: 0.75rem;
  height: 0.75rem;
}

.size-sm .checkbox-label {
  font-size: var(--cds-text-sm);
}

.size-lg .checkbox-box {
  width: 1.5rem;
  height: 1.5rem;
}

.size-lg .checkbox-box svg {
  width: 1rem;
  height: 1rem;
}

.size-lg .checkbox-label {
  font-size: var(--cds-text-lg);
}

/* Hint */
.checkbox-hint {
  margin-top: 0.25rem;
  margin-left: 1.75rem;
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
}

.checkbox-hint.is-error {
  color: var(--cds-danger);
}
</style>
