import { computed, reactive, ref } from 'vue'

const BASE_DIGITS = '0123456789ABCDEF'
const EMPTY_FORM = Object.freeze({
  binary: '',
  decimal: '',
  hexadecimal: ''
})

const FIELD_META = Object.freeze({
  binary: {
    base: 2,
    label: 'Binario',
    pattern: /^[01]+$/,
    error: 'Usa solo 0 y 1.'
  },
  decimal: {
    base: 10,
    label: 'Decimal',
    pattern: /^\d+$/,
    error: 'Usa solo digitos del 0 al 9.'
  },
  hexadecimal: {
    base: 16,
    label: 'Hexadecimal',
    pattern: /^[0-9A-F]+$/i,
    error: 'Usa solo 0-9 y A-F.'
  }
})

function parseBaseValue(rawValue, base) {
  let parsed = 0n

  for (const char of rawValue) {
    const digit = BASE_DIGITS.indexOf(char)
    if (digit < 0 || digit >= base) return null
    parsed = parsed * BigInt(base) + BigInt(digit)
  }

  return parsed
}

function normalizeInput(field, rawValue) {
  const nextValue = String(rawValue ?? '').trim()
  return field === 'hexadecimal' ? nextValue.toUpperCase() : nextValue
}

function formatValue(value, base) {
  return value.toString(base).toUpperCase()
}

export function useNumberSystemCalculator() {
  const form = reactive({ ...EMPTY_FORM })
  const errors = reactive({ ...EMPTY_FORM })
  const parsedValue = ref(null)
  const activeField = ref('')

  const isValid = computed(() => parsedValue.value !== null)

  const displayValues = computed(() => {
    if (!isValid.value) return { ...EMPTY_FORM }

    return {
      binary: activeField.value === 'binary' ? form.binary : formatValue(parsedValue.value, 2),
      decimal: activeField.value === 'decimal' ? form.decimal : formatValue(parsedValue.value, 10),
      hexadecimal: activeField.value === 'hexadecimal' ? form.hexadecimal : formatValue(parsedValue.value, 16)
    }
  })

  const bitRows = computed(() => {
    if (!isValid.value) return []

    const binaryValue = displayValues.value.binary

    return binaryValue.split('').map((bit, index, digits) => {
      const exponent = digits.length - index - 1
      const placeValue = 1n << BigInt(exponent)

      return {
        id: `${exponent}-${bit}-${index}`,
        bit,
        exponent,
        placeValue: placeValue.toString(),
        contribution: bit === '1' ? placeValue.toString() : '0'
      }
    })
  })

  const summaryRows = computed(() => {
    if (!isValid.value) return []

    return [
      { id: 'binary', label: FIELD_META.binary.label, value: displayValues.value.binary },
      { id: 'decimal', label: FIELD_META.decimal.label, value: displayValues.value.decimal },
      { id: 'hexadecimal', label: FIELD_META.hexadecimal.label, value: displayValues.value.hexadecimal }
    ]
  })

  function reset() {
    Object.assign(form, EMPTY_FORM)
    Object.assign(errors, EMPTY_FORM)
    parsedValue.value = null
    activeField.value = ''
  }

  function updateFrom(field, rawValue) {
    const normalizedValue = normalizeInput(field, rawValue)

    Object.assign(errors, EMPTY_FORM)
    form[field] = normalizedValue
    activeField.value = field

    if (!normalizedValue) {
      reset()
      return
    }

    const fieldMeta = FIELD_META[field]
    if (!fieldMeta.pattern.test(normalizedValue)) {
      errors[field] = fieldMeta.error
      parsedValue.value = null

      for (const key of Object.keys(EMPTY_FORM)) {
        if (key !== field) form[key] = ''
      }
      return
    }

    const nextParsedValue = parseBaseValue(normalizedValue, fieldMeta.base)
    if (nextParsedValue === null) {
      errors[field] = fieldMeta.error
      parsedValue.value = null

      for (const key of Object.keys(EMPTY_FORM)) {
        if (key !== field) form[key] = ''
      }
      return
    }

    parsedValue.value = nextParsedValue

    form.binary = field === 'binary' ? normalizedValue : formatValue(nextParsedValue, 2)
    form.decimal = field === 'decimal' ? normalizedValue : formatValue(nextParsedValue, 10)
    form.hexadecimal = field === 'hexadecimal' ? normalizedValue : formatValue(nextParsedValue, 16)
  }

  return {
    bitRows,
    displayValues,
    errors,
    form,
    isValid,
    reset,
    summaryRows,
    updateFrom
  }
}
