<template>
  <div class="base-input">
    <label v-if="label" class="base-input__label" :for="inputId">{{ label }}</label>
    <div class="base-input__field" :class="{ 'base-input__field--error': Boolean(error) }">
      <span v-if="$slots.prefix" class="base-input__slot base-input__slot--prefix">
        <slot name="prefix" />
      </span>

      <input
        :id="inputId"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :autocomplete="autocomplete"
        :required="required"
        :disabled="disabled"
        :inputmode="inputmode"
        :min="min"
        :max="max"
        :step="step"
        class="base-input__control"
        @input="handleInput"
        @blur="$emit('blur', $event)"
        @focus="$emit('focus', $event)"
      />

      <span v-if="$slots.suffix" class="base-input__slot base-input__slot--suffix">
        <slot name="suffix" />
      </span>
    </div>
    <p v-if="error" class="base-input__error">{{ error }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

let fallbackIdCounter = 0

const props = defineProps({
  id: { type: String, default: '' },
  label: { type: String, default: '' },
  type: { type: String, default: 'text' },
  modelValue: { type: [String, Number], default: '' },
  modelModifiers: { type: Object, default: () => ({}) },
  placeholder: { type: String, default: '' },
  autocomplete: { type: String, default: 'off' },
  inputmode: { type: String, default: '' },
  min: { type: [String, Number], default: undefined },
  max: { type: [String, Number], default: undefined },
  step: { type: [String, Number], default: undefined },
  required: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
  error: { type: String, default: '' }
})

const emit = defineEmits({
  'update:modelValue': (value) => typeof value === 'string' || typeof value === 'number',
  blur: (event) => event instanceof Event,
  focus: (event) => event instanceof Event
})

const inputId = computed(() => {
  if (props.id) return props.id
  fallbackIdCounter += 1
  return `input-${fallbackIdCounter}`
})

function handleInput(event) {
  const target = event.target
  if (!(target instanceof HTMLInputElement)) {
    return
  }

  let value = target.value
  if (props.modelModifiers.trim) {
    value = value.trim()
  }

  if (props.modelModifiers.number) {
    const parsed = Number(value)
    emit('update:modelValue', Number.isNaN(parsed) ? '' : parsed)
    return
  }

  emit('update:modelValue', value)
}
</script>

<style scoped>
.base-input {
  display: grid;
  gap: 0.5rem;
}

.base-input__label {
  font-size: var(--cds-text-sm);
  font-weight: var(--cds-font-medium);
  color: var(--cds-text-normal);
}

.base-input__field {
  display: flex;
  align-items: center;
  border: 2px solid var(--cds-light-4);
  border-radius: 0.5rem;
  background: var(--cds-white);
}

.base-input__field:focus-within {
  border-color: var(--cds-primary);
}

.base-input__field--error {
  border-color: #b42318;
}

.base-input__control {
  flex: 1;
  width: 100%;
  min-height: 44px;
  padding: 0.75rem 0.875rem;
  border: none;
  background: var(--cds-white);
  color: var(--cds-text-normal);
  font-size: var(--cds-text-base);
  line-height: var(--cds-leading-normal);
}

.base-input__control:focus {
  outline: none;
}

.base-input__slot {
  display: inline-flex;
  align-items: center;
  color: var(--cds-text-muted);
  font-size: var(--cds-text-sm);
}

.base-input__slot--prefix {
  padding-left: 0.875rem;
}

.base-input__slot--suffix {
  padding-right: 0.875rem;
}

.base-input__error {
  margin: 0;
  font-size: var(--cds-text-sm);
  color: #b42318;
}
</style>
