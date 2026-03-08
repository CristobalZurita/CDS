import { computed, reactive } from 'vue'

export const numericBaseOptions = [
  { value: 2, label: 'Binario (2)' },
  { value: 8, label: 'Octal (8)' },
  { value: 10, label: 'Decimal (10)' },
  { value: 16, label: 'Hexadecimal (16)' }
]

export function useNumberSystemCalculator() {
  const form = reactive({
    value: '',
    from: 10,
    to: 2
  })

  const normalizedValue = computed(() => String(form.value ?? '').trim())

  const parsedValue = computed(() => {
    if (!normalizedValue.value) return Number.NaN
    return parseInt(normalizedValue.value, Number(form.from))
  })

  const isValid = computed(() => Number.isFinite(parsedValue.value))

  const result = computed(() => {
    if (!isValid.value) return ''
    return parsedValue.value.toString(Number(form.to)).toUpperCase()
  })

  return {
    form,
    isValid,
    result
  }
}
