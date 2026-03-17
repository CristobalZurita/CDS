<script>
export default {
  inheritAttrs: false
}
</script>

<template>
  <div class="base-textarea-wrapper" :class="wrapperClasses">
    <label v-if="label" :for="textareaId" class="base-textarea-label">
      {{ label }}
      <span v-if="required" class="required-mark">*</span>
    </label>
    
    <textarea
      ref="textareaRef"
      :id="textareaId"
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      :readonly="readonly"
      :required="required"
      :rows="rows"
      :maxlength="maxlength"
      :class="textareaClasses"
      v-bind="attrs"
      @input="handleInput"
      @blur="handleBlur"
      @focus="$emit('focus', $event)"
    ></textarea>
    
    <div v-if="showCount || hint || error" class="base-textarea-footer">
      <span v-if="hint || error" class="base-textarea-hint" :class="{ 'is-error': error }">
        {{ error || hint }}
      </span>
      <span v-if="showCount" class="char-count" :class="{ 'is-limit': isNearLimit }">
        {{ charCount }}/{{ maxlength }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, useAttrs } from 'vue'

const props = defineProps({
  modelValue: { type: String, default: '' },
  label: { type: String, default: '' },
  placeholder: { type: String, default: '' },
  hint: { type: String, default: '' },
  error: { type: String, default: '' },
  disabled: { type: Boolean, default: false },
  readonly: { type: Boolean, default: false },
  required: { type: Boolean, default: false },
  rows: { type: Number, default: 3 },
  maxlength: { type: Number, default: undefined },
  id: { type: String, default: '' },
  size: { 
    type: String, 
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg'].includes(value)
  },
  showCount: { type: Boolean, default: false },
  autoResize: { type: Boolean, default: false }
})

const emit = defineEmits(['update:modelValue', 'blur', 'focus', 'validate'])
const attrs = useAttrs()
const textareaRef = ref(null)

const textareaId = computed(() => props.id || `textarea-${Math.random().toString(36).substr(2, 9)}`)

const charCount = computed(() => props.modelValue?.length || 0)

const isNearLimit = computed(() => {
  if (!props.maxlength) return false
  return charCount.value > props.maxlength * 0.9
})

const wrapperClasses = computed(() => ({
  'has-error': !!props.error,
  'is-disabled': props.disabled,
  [`size-${props.size}`]: true
}))

const textareaClasses = computed(() => [
  'base-textarea',
  {
    'is-invalid': !!props.error,
    [`textarea-${props.size}`]: true,
    'auto-resize': props.autoResize
  }
])

function handleInput(event) {
  let value = event.target.value
  
  // Respetar maxlength
  if (props.maxlength && value.length > props.maxlength) {
    value = value.slice(0, props.maxlength)
  }
  
  emit('update:modelValue', value)
  
  // Auto-resize
  if (props.autoResize) {
    autoResize(event.target)
  }
}

function handleBlur(event) {
  emit('blur', event)
  
  // Validación básica
  if (props.required && !event.target.value.trim()) {
    emit('validate', { valid: false, message: 'Este campo es obligatorio' })
  } else {
    emit('validate', { valid: true, message: '' })
  }
}

function autoResize(element) {
  element.style.height = 'auto'
  element.style.height = element.scrollHeight + 'px'
}

defineExpose({
  focus: () => textareaRef.value?.focus(),
  select: () => textareaRef.value?.select()
})
</script>

<style scoped>
.base-textarea-wrapper {
  display: grid;
  gap: 0.35rem;
}

.base-textarea-label {
  font-size: var(--cds-text-sm);
  font-weight: 500;
  color: var(--cds-text-normal);
}

.required-mark {
  color: var(--cds-danger);
}

.base-textarea {
  width: 100%;
  min-height: 44px;
  padding: 0.65rem 0.9rem;
  border: 1px solid var(--cds-border-input);
  border-radius: var(--cds-radius-sm);
  background: var(--cds-white);
  color: var(--cds-text-normal);
  font-size: var(--cds-text-base);
  font-family: inherit;
  line-height: 1.5;
  resize: vertical;
  transition: all 0.2s ease;
}

.base-textarea::placeholder {
  color: var(--cds-light-5);
}

.base-textarea:hover:not(:disabled) {
  border-color: color-mix(in srgb, var(--cds-light) 40%, white);
}

.base-textarea:focus {
  outline: none;
  border-color: var(--cds-primary);
  box-shadow: var(--cds-focus-ring);
}

.base-textarea:disabled {
  background: var(--cds-light-1);
  cursor: not-allowed;
  opacity: 0.7;
}

.base-textarea.is-invalid {
  border-color: var(--cds-danger);
  background: var(--cds-invalid-bg);
}

.base-textarea.auto-resize {
  resize: none;
  overflow: hidden;
}

/* Tamaños */
.size-sm .base-textarea {
  padding: 0.5rem 0.75rem;
  font-size: var(--cds-text-sm);
}

.size-lg .base-textarea {
  padding: 0.8rem 1rem;
  font-size: var(--cds-text-lg);
}

/* Footer */
.base-textarea-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
}

.base-textarea-hint {
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
  flex: 1;
}

.base-textarea-hint.is-error {
  color: var(--cds-danger);
}

.char-count {
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
  white-space: nowrap;
}

.char-count.is-limit {
  color: var(--cds-warning);
  font-weight: 500;
}

.base-textarea-wrapper.has-error .base-textarea-label {
  color: var(--cds-danger);
}
</style>
