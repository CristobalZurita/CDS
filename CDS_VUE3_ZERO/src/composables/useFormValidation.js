/**
 * useFormValidation
 * 
 * Composable para validación de formularios con reglas estrictas por tipo.
 * Valida: RUT chileno, email, teléfono, texto (solo letras), números, etc.
 */

import { ref, computed } from 'vue'

// Mensajes de error predefinidos
const DEFAULT_MESSAGES = {
  required: 'Este campo es obligatorio',
  email: 'Ingresa un email válido (ejemplo@correo.com)',
  phone: 'Ingresa un teléfono válido (ej: +56912345678)',
  rut: 'RUT inválido',
  textOnly: 'Solo se permiten letras',
  numbersOnly: 'Solo se permiten números',
  alphanumeric: 'Solo letras y números',
  minLength: (min) => `Mínimo ${min} caracteres`,
  maxLength: (max) => `Máximo ${max} caracteres`,
  min: (min) => `El valor mínimo es ${min}`,
  max: (max) => `El valor máximo es ${max}`,
  pattern: 'Formato inválido',
  match: 'Los campos no coinciden',
  url: 'URL inválida',
  date: 'Fecha inválida'
}

// Reglas de validación individuales
const validators = {
  // Requerido
  required: (value) => {
    if (value === undefined || value === null) return false
    if (typeof value === 'string') return value.trim() !== ''
    if (Array.isArray(value)) return value.length > 0
    if (typeof value === 'boolean') return true
    return true
  },

  // Email
  email: (value) => {
    if (!value) return true // Si no es required, vacío es válido
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(value))
  },

  // Teléfono chileno
  phone: (value) => {
    if (!value) return true
    const cleaned = String(value).replace(/\s/g, '')
    return /^(\+?56)?9\d{8}$/.test(cleaned)
  },

  // RUT chileno (con dígito verificador)
  rut: (value) => {
    if (!value) return true
    const cleaned = String(value).replace(/\./g, '').replace('-', '').toUpperCase()
    
    // Validar formato básico
    if (!/^\d{7,8}[0-9K]$/.test(cleaned)) return false
    
    const dv = cleaned.slice(-1)
    const num = cleaned.slice(0, -1)
    
    // Calcular dígito verificador
    let sum = 0
    let mul = 2
    for (let i = num.length - 1; i >= 0; i--) {
      sum += parseInt(num[i]) * mul
      mul = mul === 7 ? 2 : mul + 1
    }
    
    const res = 11 - (sum % 11)
    const expectedDv = res === 11 ? '0' : res === 10 ? 'K' : String(res)
    
    return dv === expectedDv
  },

  // Solo letras (incluye tildes y ñ)
  textOnly: (value) => {
    if (!value) return true
    return /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/.test(String(value))
  },

  // Solo números
  numbersOnly: (value) => {
    if (!value) return true
    return /^\d+$/.test(String(value))
  },

  // Alfanumérico
  alphanumeric: (value) => {
    if (!value) return true
    return /^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s]+$/.test(String(value))
  },

  // Longitud mínima
  minLength: (value, min) => {
    if (!value) return true
    return String(value).length >= min
  },

  // Longitud máxima
  maxLength: (value, max) => {
    if (!value) return true
    return String(value).length <= max
  },

  // Valor mínimo (números)
  min: (value, min) => {
    if (value === undefined || value === null || value === '') return true
    return Number(value) >= min
  },

  // Valor máximo (números)
  max: (value, max) => {
    if (value === undefined || value === null || value === '') return true
    return Number(value) <= max
  },

  // Patrón regex personalizado
  pattern: (value, regex) => {
    if (!value) return true
    return regex.test(String(value))
  },

  // Coincidencia entre campos
  match: (value, targetValue) => {
    return value === targetValue
  },

  // URL
  url: (value) => {
    if (!value) return true
    try {
      new URL(String(value))
      return true
    } catch {
      return false
    }
  },

  // Fecha válida
  date: (value) => {
    if (!value) return true
    const date = new Date(value)
    return !isNaN(date.getTime())
  }
}

/**
 * Crear validador de formulario
 */
export function useFormValidation(fieldsConfig = {}) {
  const errors = ref({})
  const touched = ref(new Set())
  const dirty = ref(new Set())

  // Estado computado
  const hasErrors = computed(() => Object.keys(errors.value).length > 0)
  const isValid = computed(() => !hasErrors.value)
  const errorCount = computed(() => Object.keys(errors.value).length)

  /**
   * Validar un campo específico
   */
  function validateField(fieldName, value, rules = null) {
    const fieldRules = rules || fieldsConfig[fieldName]
    if (!fieldRules) return { valid: true, error: null }

    const errorsList = []

    // Iterar sobre cada regla
    for (const [ruleName, ruleValue] of Object.entries(fieldRules)) {
      // Saltar reglas que no son de validación
      if (ruleName === 'message') continue

      let isValid = true

      // Validar según tipo de regla
      switch (ruleName) {
        case 'required':
          if (ruleValue && !validators.required(value)) {
            isValid = false
          }
          break

        case 'email':
          if (ruleValue && !validators.email(value)) {
            isValid = false
          }
          break

        case 'phone':
          if (ruleValue && !validators.phone(value)) {
            isValid = false
          }
          break

        case 'rut':
          if (ruleValue && !validators.rut(value)) {
            isValid = false
          }
          break

        case 'textOnly':
          if (ruleValue && !validators.textOnly(value)) {
            isValid = false
          }
          break

        case 'numbersOnly':
          if (ruleValue && !validators.numbersOnly(value)) {
            isValid = false
          }
          break

        case 'alphanumeric':
          if (ruleValue && !validators.alphanumeric(value)) {
            isValid = false
          }
          break

        case 'minLength':
          if (!validators.minLength(value, ruleValue)) {
            isValid = false
          }
          break

        case 'maxLength':
          if (!validators.maxLength(value, ruleValue)) {
            isValid = false
          }
          break

        case 'min':
          if (!validators.min(value, ruleValue)) {
            isValid = false
          }
          break

        case 'max':
          if (!validators.max(value, ruleValue)) {
            isValid = false
          }
          break

        case 'pattern':
          if (!validators.pattern(value, ruleValue)) {
            isValid = false
          }
          break

        case 'match':
          if (!validators.match(value, ruleValue)) {
            isValid = false
          }
          break

        case 'url':
          if (ruleValue && !validators.url(value)) {
            isValid = false
          }
          break

        case 'date':
          if (ruleValue && !validators.date(value)) {
            isValid = false
          }
          break

        case 'custom':
          if (typeof ruleValue === 'function') {
            const customResult = ruleValue(value)
            if (customResult !== true) {
              isValid = false
              // Mensaje custom del validador
              if (typeof customResult === 'string') {
                errorsList.push(customResult)
                continue
              }
            }
          }
          break
      }

      // Si no es válido, agregar mensaje de error
      if (!isValid) {
        const message = getErrorMessage(ruleName, ruleValue, fieldRules.message)
        errorsList.push(message)
      }
    }

    // Actualizar estado de errores
    if (errorsList.length > 0) {
      errors.value[fieldName] = errorsList[0] // Solo el primer error
      return { valid: false, error: errorsList[0] }
    } else {
      delete errors.value[fieldName]
      return { valid: true, error: null }
    }
  }

  /**
   * Obtener mensaje de error
   */
  function getErrorMessage(ruleName, ruleValue, customMessage) {
    if (customMessage) return customMessage

    const msg = DEFAULT_MESSAGES[ruleName]
    if (typeof msg === 'function') {
      return msg(ruleValue)
    }
    return msg || 'Campo inválido'
  }

  /**
   * Validar todo el formulario
   */
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

  /**
   * Marcar campo como touched
   */
  function touch(fieldName) {
    touched.value.add(fieldName)
  }

  /**
   * Marcar campo como dirty (modificado)
   */
  function makeDirty(fieldName) {
    dirty.value.add(fieldName)
  }

  /**
   * Limpiar errores
   */
  function clearErrors() {
    errors.value = {}
  }

  /**
   * Limpiar campo específico
   */
  function clearField(fieldName) {
    delete errors.value[fieldName]
  }

  /**
   * Resetear todo
   */
  function reset() {
    errors.value = {}
    touched.value.clear()
    dirty.value.clear()
  }

  /**
   * Verificar si campo tiene error
   */
  function hasError(fieldName) {
    return !!errors.value[fieldName]
  }

  /**
   * Verificar si campo fue tocado
   */
  function isTouched(fieldName) {
    return touched.value.has(fieldName)
  }

  /**
   * Verificar si campo fue modificado
   */
  function isDirty(fieldName) {
    return dirty.value.has(fieldName)
  }

  /**
   * Obtener error de campo
   */
  function getError(fieldName) {
    return errors.value[fieldName] || null
  }

  return {
    // Estado
    errors,
    hasErrors,
    isValid,
    errorCount,
    
    // Validación
    validateField,
    validateAll,
    
    // Estado de campos
    touch,
    makeDirty,
    isTouched,
    isDirty,
    hasError,
    getError,
    
    // Limpieza
    clearErrors,
    clearField,
    reset,
    
    // Utilidades expuestas
    validators
  }
}

// Exportar utilidades individuales
export { validators, DEFAULT_MESSAGES }
export default useFormValidation
