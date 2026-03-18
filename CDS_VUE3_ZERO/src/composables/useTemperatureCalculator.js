import { computed, reactive } from 'vue'
import { normalizeDecimal } from '@/utils/format'

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

  const allScales = computed(() => {
    if (!canConvert.value) return null
    const inputValue = Number(form.value)
    const celsius = toCelsius(inputValue, form.from)
    return {
      C: normalizeDecimal(celsius, 4),
      F: normalizeDecimal(fromCelsius(celsius, 'F'), 4),
      K: normalizeDecimal(fromCelsius(celsius, 'K'), 4),
      R: normalizeDecimal(fromCelsius(celsius, 'R'), 4)
    }
  })

  const displayScales = computed(() => (
    allScales.value || {
      C: 0,
      F: 32,
      K: 273.15,
      R: 491.67
    }
  ))

  const thermoItems = computed(() => ([
    {
      key: 'C',
      label: 'Celsius',
      unit: '°C',
      value: displayScales.value.C,
      min: -50,
      max: 150,
      tone: 'hot'
    },
    {
      key: 'F',
      label: 'Fahrenheit',
      unit: '°F',
      value: displayScales.value.F,
      min: -58,
      max: 302,
      tone: 'warm'
    },
    {
      key: 'K',
      label: 'Kelvin',
      unit: 'K',
      value: displayScales.value.K,
      min: 223.15,
      max: 423.15,
      tone: 'cool'
    }
  ]))

  function fillPercent(item) {
    if (!Number.isFinite(item.value)) return 0
    const span = item.max - item.min
    if (!(span > 0)) return 0
    const ratio = ((item.value - item.min) / span) * 100
    return Math.min(100, Math.max(0, ratio))
  }

  function formatScale(value, unit) {
    if (!Number.isFinite(value)) return `- ${unit}`
    return `${value.toFixed(2)} ${unit}`
  }

  function swapScales() {
    const nextFrom = form.to
    form.to = form.from
    form.from = nextFrom
  }

  function reset() {
    form.value = ''
    form.from = 'C'
    form.to = 'F'
  }

  return {
    form,
    canConvert,
    result,
    allScales,
    displayScales,
    fillPercent,
    formatScale,
    thermoItems,
    reset,
    swapScales
  }
}
