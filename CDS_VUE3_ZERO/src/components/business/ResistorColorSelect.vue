<template>
  <div ref="rootRef" class="resistor-color-select">
    <button
      type="button"
      class="resistor-color-select__trigger"
      :class="{ 'is-open': isOpen, 'has-color': hasColorPreview }"
      :style="triggerStyle"
      :aria-expanded="isOpen ? 'true' : 'false'"
      @click="toggleMenu"
    >
      <span class="resistor-color-select__label">{{ selectedOption?.label || placeholder }}</span>
      <span v-if="hasColorPreview && selectedOption?.badge" class="resistor-color-select__badge">
        {{ selectedOption.badge }}
      </span>
      <span class="resistor-color-select__arrow" aria-hidden="true">▾</span>
    </button>

    <div v-if="isOpen" class="resistor-color-select__menu" role="listbox">
      <button
        v-for="option in options"
        :key="option.value"
        type="button"
        class="resistor-color-select__option"
        :class="{ 'is-selected': option.value === modelValue }"
        :style="optionStyle(option)"
        @click="selectOption(option)"
      >
        <span class="resistor-color-select__option-label">{{ option.label }}</span>
        <span v-if="option.badge" class="resistor-color-select__option-badge">{{ option.badge }}</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  options: {
    type: Array,
    required: true
  },
  neutral: {
    type: Boolean,
    default: false
  },
  placeholder: {
    type: String,
    default: 'Selecciona un color'
  }
})

const emit = defineEmits(['update:modelValue'])

const rootRef = ref(null)
const isOpen = ref(false)

const selectedOption = computed(() => props.options.find((option) => option.value === props.modelValue) || null)
const hasColorPreview = computed(() => !props.neutral && !!selectedOption.value)

const triggerStyle = computed(() => {
  if (!hasColorPreview.value || !selectedOption.value) {
    return {}
  }

  return optionStyle(selectedOption.value)
})

function optionStyle(option) {
  const background = option.swatch || 'var(--cds-white)'
  const color = option.textColor || 'var(--cds-text-normal)'
  const borderColor = option.borderColor || option.swatch || 'var(--cds-border-input)'

  return {
    background,
    color,
    borderColor
  }
}

function toggleMenu() {
  isOpen.value = !isOpen.value
}

function closeMenu() {
  isOpen.value = false
}

function selectOption(option) {
  emit('update:modelValue', option.value)
  closeMenu()
}

function handleDocumentClick(event) {
  if (!rootRef.value?.contains(event.target)) {
    closeMenu()
  }
}

function handleEscape(event) {
  if (event.key === 'Escape') {
    closeMenu()
  }
}

onMounted(() => {
  document.addEventListener('click', handleDocumentClick)
  document.addEventListener('keydown', handleEscape)
})

onUnmounted(() => {
  document.removeEventListener('click', handleDocumentClick)
  document.removeEventListener('keydown', handleEscape)
})
</script>

<style scoped>
.resistor-color-select {
  position: relative;
}

.resistor-color-select__trigger {
  width: 100%;
  min-height: 44px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto auto;
  align-items: center;
  gap: 0.6rem;
  padding: 0.65rem 0.8rem;
  border: 1.5px solid rgba(62, 60, 56, 0.25);
  border-radius: 0.5rem;
  background: var(--cds-white);
  color: var(--cds-dark);
  font-size: var(--cds-text-base);
  text-align: left;
  cursor: pointer;
  box-sizing: border-box;
}

.resistor-color-select__trigger:focus-visible,
.resistor-color-select__trigger.is-open {
  outline: none;
  border-color: var(--cds-primary);
  box-shadow: var(--cds-focus-ring);
}

.resistor-color-select__trigger.has-color {
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.12);
}

.resistor-color-select__label,
.resistor-color-select__option-label {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.resistor-color-select__badge,
.resistor-color-select__option-badge {
  font-weight: var(--cds-font-bold);
}

.resistor-color-select__arrow {
  font-size: 0.9em;
  line-height: 1;
}

.resistor-color-select__menu {
  position: absolute;
  left: 0;
  right: 0;
  top: calc(100% + 0.35rem);
  z-index: 30;
  display: grid;
  gap: 0.2rem;
  padding: 0.25rem;
  border: 1px solid rgba(62, 60, 56, 0.18);
  border-radius: 0.75rem;
  background: var(--cds-white);
  box-shadow: var(--cds-shadow-md);
  max-height: 18rem;
  overflow-y: auto;
}

.resistor-color-select__option {
  width: 100%;
  min-height: 40px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: center;
  gap: 0.6rem;
  padding: 0.65rem 0.8rem;
  border: 1px solid transparent;
  border-radius: 0.55rem;
  font-size: var(--cds-text-sm);
  text-align: left;
  cursor: pointer;
}

.resistor-color-select__option.is-selected {
  box-shadow: inset 0 0 0 2px rgba(255, 255, 255, 0.42);
}
</style>
