/**
 * useFormValidation
 *
 * Capa de estado para validacion de formularios basada en reglas reutilizables.
 */

import { computed, ref } from 'vue'
import { DEFAULT_MESSAGES, getErrorMessage, validators, validateFieldValue } from './formValidationRules'

export function useFormValidation(fieldsConfig = {}) {
  const errors = ref({})
  const touched = ref(new Set())
  const dirty = ref(new Set())

  const hasErrors = computed(() => Object.keys(errors.value).length > 0)
  const isValid = computed(() => !hasErrors.value)
  const errorCount = computed(() => Object.keys(errors.value).length)

  function validateField(fieldName, value, rules = null) {
    const fieldRules = rules || fieldsConfig[fieldName]
    const result = validateFieldValue(fieldRules, value)

    if (!result.valid) {
      errors.value[fieldName] = result.error
      return result
    }

    delete errors.value[fieldName]
    return result
  }

  function validateAll(values) {
    const allErrors = {}
    let isFormValid = true

    for (const [fieldName, rules] of Object.entries(fieldsConfig)) {
      const result = validateField(fieldName, values[fieldName], rules)
      if (!result.valid) {
        allErrors[fieldName] = result.error
        isFormValid = false
      }
    }

    errors.value = allErrors
    return { valid: isFormValid, errors: allErrors }
  }

  function touch(fieldName) {
    touched.value.add(fieldName)
  }

  function makeDirty(fieldName) {
    dirty.value.add(fieldName)
  }

  function clearErrors() {
    errors.value = {}
  }

  function clearField(fieldName) {
    delete errors.value[fieldName]
  }

  function reset() {
    errors.value = {}
    touched.value.clear()
    dirty.value.clear()
  }

  function hasError(fieldName) {
    return !!errors.value[fieldName]
  }

  function isTouched(fieldName) {
    return touched.value.has(fieldName)
  }

  function isDirty(fieldName) {
    return dirty.value.has(fieldName)
  }

  function getError(fieldName) {
    return errors.value[fieldName] || null
  }

  return {
    errors,
    hasErrors,
    isValid,
    errorCount,
    validateField,
    validateAll,
    touch,
    makeDirty,
    isTouched,
    isDirty,
    hasError,
    getError,
    clearErrors,
    clearField,
    reset,
    validators
  }
}

export { validators, DEFAULT_MESSAGES, getErrorMessage, validateFieldValue }
export default useFormValidation
