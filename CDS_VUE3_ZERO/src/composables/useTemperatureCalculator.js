import { computed, reactive } from 'vue'

export const temperatureScales = [
  { value: 'C', label: 'Celsius (°C)' },
  { value: 'F', label: 'Fahrenheit (°F)' },
  { value: 'K', label: 'Kelvin (K)' },
  { value: 'R', label: 'Rankine (°R)' }
]

function toCelsius(value, from) {
  switch (from) {
    case 'F':
      return (value - 32) * (5 / 9)
    case 'K':
      return value - 273.15
    case 'R':
      return (value - 491.67) * (5 / 9)
    case 'C':
    default:
      return value
  }
}

function fromCelsius(value, to) {
  switch (to) {
    case 'F':
      return value * (9 / 5) + 32
    case 'K':
      return value + 273.15
    case 'R':
      return (value + 273.15) * (9 / 5)
    case 'C':
    default:
      return value
  }
}

function normalizeDecimal(value, decimals = 4) {
  if (!Number.isFinite(value)) return null
  return Number(value.toFixed(decimals))
}

export function useTemperatureCalculator() {
  const form = reactive({
    value: '',
    from: 'C',
    to: 'F'
  })

  const canConvert = computed(() => form.value !== '' && Number.isFinite(Number(form.value)))

  const result = computed(() => {
    if (!canConvert.value) return null
    const inputValue = Number(form.value)
    const celsius = toCelsius(inputValue, form.from)
    const converted = fromCelsius(celsius, form.to)
    return normalizeDecimal(converted, 4)
  })

  return {
    form,
    canConvert,
    result
  }
}
