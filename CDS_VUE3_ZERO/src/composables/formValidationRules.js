export const DEFAULT_MESSAGES = {
  required: 'Este campo es obligatorio',
  email: 'Ingresa un email valido (ejemplo@correo.com)',
  phone: 'Ingresa un telefono valido (ej: +56912345678)',
  rut: 'RUT invalido',
  textOnly: 'Solo se permiten letras',
  numbersOnly: 'Solo se permiten numeros',
  alphanumeric: 'Solo letras y numeros',
  minLength: (min) => `Minimo ${min} caracteres`,
  maxLength: (max) => `Maximo ${max} caracteres`,
  min: (min) => `El valor minimo es ${min}`,
  max: (max) => `El valor maximo es ${max}`,
  pattern: 'Formato invalido',
  match: 'Los campos no coinciden',
  url: 'URL invalida',
  date: 'Fecha invalida'
}

export const validators = {
  required: (value) => {
    if (value === undefined || value === null) return false
    if (typeof value === 'string') return value.trim() !== ''
    if (Array.isArray(value)) return value.length > 0
    if (typeof value === 'boolean') return true
    return true
  },
  email: (value) => {
    if (!value) return true
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(value))
  },
  phone: (value) => {
    if (!value) return true
    const cleaned = String(value).replace(/\s/g, '')
    return /^(\+?56)?9\d{8}$/.test(cleaned)
  },
  rut: (value) => {
    if (!value) return true
    const cleaned = String(value).replace(/\./g, '').replace('-', '').toUpperCase()
    if (!/^\d{7,8}[0-9K]$/.test(cleaned)) return false

    const dv = cleaned.slice(-1)
    const num = cleaned.slice(0, -1)

    let sum = 0
    let mul = 2
    for (let i = num.length - 1; i >= 0; i -= 1) {
      sum += parseInt(num[i], 10) * mul
      mul = mul === 7 ? 2 : mul + 1
    }

    const res = 11 - (sum % 11)
    const expectedDv = res === 11 ? '0' : res === 10 ? 'K' : String(res)

    return dv === expectedDv
  },
  textOnly: (value) => {
    if (!value) return true
    return /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/.test(String(value))
  },
  numbersOnly: (value) => {
    if (!value) return true
    return /^\d+$/.test(String(value))
  },
  alphanumeric: (value) => {
    if (!value) return true
    return /^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s]+$/.test(String(value))
  },
  minLength: (value, min) => {
    if (!value) return true
    return String(value).length >= min
  },
  maxLength: (value, max) => {
    if (!value) return true
    return String(value).length <= max
  },
  min: (value, min) => {
    if (value === undefined || value === null || value === '') return true
    return Number(value) >= min
  },
  max: (value, max) => {
    if (value === undefined || value === null || value === '') return true
    return Number(value) <= max
  },
  pattern: (value, regex) => {
    if (!value) return true
    return regex.test(String(value))
  },
  match: (value, targetValue) => value === targetValue,
  url: (value) => {
    if (!value) return true
    try {
      new URL(String(value))
      return true
    } catch {
      return false
    }
  },
  date: (value) => {
    if (!value) return true
    const date = new Date(value)
    return !Number.isNaN(date.getTime())
  }
}

function getRuleValidity(ruleName, ruleValue, value) {
  switch (ruleName) {
    case 'required':
    case 'email':
    case 'phone':
    case 'rut':
    case 'textOnly':
    case 'numbersOnly':
    case 'alphanumeric':
    case 'url':
    case 'date':
      return !ruleValue || validators[ruleName](value)
    case 'minLength':
    case 'maxLength':
    case 'min':
    case 'max':
    case 'pattern':
    case 'match':
      return validators[ruleName](value, ruleValue)
    case 'custom':
      if (typeof ruleValue !== 'function') return true
      return ruleValue(value)
    default:
      return true
  }
}

export function getErrorMessage(ruleName, ruleValue, customMessage) {
  if (customMessage) return customMessage

  const message = DEFAULT_MESSAGES[ruleName]
  if (typeof message === 'function') {
    return message(ruleValue)
  }
  return message || 'Campo invalido'
}

export function validateFieldValue(fieldRules, value) {
  if (!fieldRules) return { valid: true, error: null }

  const errorsList = []

  for (const [ruleName, ruleValue] of Object.entries(fieldRules)) {
    if (ruleName === 'message') continue

    const result = getRuleValidity(ruleName, ruleValue, value)
    if (result === true) continue

    if (ruleName === 'custom' && typeof result === 'string') {
      errorsList.push(result)
      continue
    }

    errorsList.push(getErrorMessage(ruleName, ruleValue, fieldRules.message))
  }

  if (errorsList.length > 0) {
    return { valid: false, error: errorsList[0] }
  }

  return { valid: true, error: null }
}
