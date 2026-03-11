<template>
  <form
    class="base-form"
    :class="formClasses"
    @submit.prevent="handleSubmit"
  >
    <!-- Errores generales del formulario -->
    <div v-if="generalError" class="form-error-banner" role="alert">
      <span class="error-icon">⚠️</span>
      <span>{{ generalError }}</span>
    </div>

    <!-- Contenido del formulario -->
    <div class="form-body">
      <slot
        :validate="validateField"
        :errors="fieldErrors"
        :isSubmitting="isSubmitting"
      ></slot>
    </div>

    <!-- Acciones del formulario -->
    <div v-if="$slots.actions || showDefaultActions" class="form-actions">
      <slot name="actions" :isSubmitting="isSubmitting" :submit="handleSubmit">
        <BaseButton
          v-if="showDefaultActions"
          type="button"
          variant="ghost"
          :disabled="isSubmitting"
          @click="$emit('cancel')"
        >
          {{ cancelText }}
        </BaseButton>
        <BaseButton
          v-if="showDefaultActions"
          type="submit"
          :variant="submitVariant"
          :loading="isSubmitting"
          :loading-text="loadingText"
        >
          {{ submitText }}
        </BaseButton>
      </slot>
    </div>
  </form>
</template>

<script setup>
import { ref, computed, provide } from 'vue'
import BaseButton from './BaseButton.vue'

const props = defineProps({
  // Validación
  validationRules: { type: Object, default: () => ({}) },
  validateOnSubmit: { type: Boolean, default: true },
  validateOnBlur: { type: Boolean, default: true },
  
  // Textos
  submitText: { type: String, default: 'Guardar' },
  cancelText: { type: String, default: 'Cancelar' },
  loadingText: { type: String, default: 'Guardando...' },
  submitVariant: { type: String, default: 'primary' },
  
  // UI
  showDefaultActions: { type: Boolean, default: false },
  compact: { type: Boolean, default: false },
  
  // Datos iniciales
  initialData: { type: Object, default: () => ({}) }
})

const emit = defineEmits(['submit', 'cancel', 'validate', 'error'])

// Estado
const isSubmitting = ref(false)
const generalError = ref('')
const fieldErrors = ref({})
const touchedFields = ref(new Set())

const formClasses = computed(() => ({
  'is-compact': props.compact,
  'has-errors': Object.keys(fieldErrors.value).length > 0
}))

// Validar un campo específico
function validateField(fieldName, value, rules = null) {
  const fieldRules = rules || props.validationRules[fieldName]
  if (!fieldRules) return { valid: true, message: '' }
  
  const errors = []
  
  // Requerido
  if (fieldRules.required && (!value || (typeof value === 'string' && !value.trim()))) {
    errors.push(fieldRules.requiredMessage || 'Este campo es obligatorio')
  }
  
  // Mínimo caracteres
  if (fieldRules.minLength && String(value).length < fieldRules.minLength) {
    errors.push(`Mínimo ${fieldRules.minLength} caracteres`)
  }
  
  // Máximo caracteres
  if (fieldRules.maxLength && String(value).length > fieldRules.maxLength) {
    errors.push(`Máximo ${fieldRules.maxLength} caracteres`)
  }
  
  // Patrón regex
  if (fieldRules.pattern && !fieldRules.pattern.test(String(value))) {
    errors.push(fieldRules.patternMessage || 'Formato inválido')
  }
  
  // Validación custom
  if (fieldRules.validator && typeof fieldRules.validator === 'function') {
    const customError = fieldRules.validator(value)
    if (customError) errors.push(customError)
  }
  
  // Email
  if (fieldRules.email && value) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(String(value))) {
      errors.push('Email inválido')
    }
  }
  
  // Teléfono chileno
  if (fieldRules.phone && value) {
    const phoneRegex = /^(\+?56)?\s?9\s?\d{4}\s?\d{4}$/
    if (!phoneRegex.test(String(value).replace(/\s/g, ''))) {
      errors.push('Teléfono inválido (ej: +56912345678)')
    }
  }
  
  // RUT chileno
  if (fieldRules.rut && value) {
    if (!validateRut(String(value))) {
      errors.push('RUT inválido')
    }
  }
  
  // Número mínimo
  if (fieldRules.min !== undefined && Number(value) < fieldRules.min) {
    errors.push(`El mínimo es ${fieldRules.min}`)
  }
  
  // Número máximo
  if (fieldRules.max !== undefined && Number(value) > fieldRules.max) {
    errors.push(`El máximo es ${fieldRules.max}`)
  }
  
  const errorMessage = errors[0] || ''
  
  // Actualizar errores
  if (errorMessage) {
    fieldErrors.value[fieldName] = errorMessage
  } else {
    delete fieldErrors.value[fieldName]
  }
  
  return { valid: !errorMessage, message: errorMessage }
}

// Validar RUT chileno
function validateRut(rut) {
  rut = rut.replace(/\./g, '').replace('-', '').toUpperCase()
  const dv = rut.slice(-1)
  const num = rut.slice(0, -1)
  
  if (!/^\d+$/.test(num)) return false
  
  let sum = 0
  let mul = 2
  
  for (let i = num.length - 1; i >= 0; i--) {
    sum += parseInt(num[i]) * mul
    mul = mul === 7 ? 2 : mul + 1
  }
  
  const res = 11 - (sum % 11)
  const expectedDv = res === 11 ? '0' : res === 10 ? 'K' : String(res)
  
  return dv === expectedDv
}

// Validar todo el formulario
function validateAll(data) {
  const errors = {}
  
  for (const [fieldName, rules] of Object.entries(props.validationRules)) {
    const result = validateField(fieldName, data[fieldName], rules)
    if (!result.valid) {
      errors[fieldName] = result.message
    }
  }
  
  fieldErrors.value = errors
  return { valid: Object.keys(errors).length === 0, errors }
}

// Handler de submit
async function handleSubmit(event) {
  generalError.value = ''
  
  // Emitir evento para obtener datos actuales
  const formData = {}
  
  if (props.validateOnSubmit) {
    const validation = validateAll(formData)
    
    if (!validation.valid) {
      emit('error', validation.errors)
      // Scroll al primer error
      const firstError = document.querySelector('.is-invalid')
      if (firstError) {
        firstError.scrollIntoView({ behavior: 'smooth', block: 'center' })
        firstError.focus()
      }
      return
    }
  }
  
  isSubmitting.value = true
  
  try {
    await emit('submit', formData, {
      setError: (msg) => { generalError.value = msg },
      setFieldError: (field, msg) => { fieldErrors.value[field] = msg },
      clearErrors: () => {
        generalError.value = ''
        fieldErrors.value = {}
      }
    })
  } catch (error) {
    generalError.value = error?.message || 'Error al guardar'
  } finally {
    isSubmitting.value = false
  }
}

// Proveer validación a componentes hijos
provide('formValidation', {
  validateField,
  fieldErrors,
  touchedFields,
  validateOnBlur: props.validateOnBlur
})
</script>

<style scoped>
.base-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.base-form.is-compact {
  gap: 1rem;
}

/* Banner de error general */
.form-error-banner {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  border-radius: var(--cds-radius-md);
  background: var(--cds-invalid-bg);
  border: 1px solid var(--cds-invalid-border);
  color: var(--cds-invalid-text);
  font-size: var(--cds-text-base);
}

.error-icon {
  font-size: 1.25rem;
}

/* Cuerpo del formulario */
.form-body {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.is-compact .form-body {
  gap: 0.75rem;
}

/* Acciones */
.form-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
  padding-top: 0.5rem;
  border-top: 1px solid color-mix(in srgb, var(--cds-light) 70%, white);
}

.form-actions :deep(.base-button) {
  min-width: 120px;
}

@media (max-width: 640px) {
  .form-actions {
    flex-direction: column;
  }
  
  .form-actions :deep(.base-button) {
    width: 100%;
  }
}
</style>
