import { computed, reactive } from 'vue'

const unitFactor = {
  ohm: 1,
  kohm: 1000,
  mohm: 1000000,
}

function toOhm(value, unit) {
  const factor = unitFactor[unit] || 1
  return Number(value) * factor
}

function fromOhm(value, unit) {
  const factor = unitFactor[unit] || 1
  return value / factor
}

function normalizeDecimal(value, decimals = 6) {
  if (!Number.isFinite(value)) return null
  return Number(value.toFixed(decimals))
}

export const resistorNetworkModes = [
  { value: 'parallel', label: 'Paralelo' },
  { value: 'series', label: 'Serie' },
]

export const resistorUnitOptions = [
  { value: 'ohm', label: 'Ω' },
  { value: 'kohm', label: 'kΩ' },
  { value: 'mohm', label: 'MΩ' },
]

export function useSeriesParallelResistorCalculator() {
  const form = reactive({
    mode: 'parallel',
    input_unit: 'ohm',
    output_unit: 'ohm',
    resistors: [1000, 1000],
  })

  const sanitizedResistors = computed(() =>
    form.resistors
      .map((value) => toOhm(value, form.input_unit))
      .filter((value) => Number.isFinite(value) && value > 0)
  )

  const canCalculate = computed(() => sanitizedResistors.value.length >= 2)

  const resultOhm = computed(() => {
    if (!canCalculate.value) return null

    if (form.mode === 'series') {
      const total = sanitizedResistors.value.reduce((acc, value) => acc + value, 0)
      return normalizeDecimal(total, 9)
    }

    const inverse = sanitizedResistors.value.reduce((acc, value) => acc + (1 / value), 0)
    if (inverse <= 0) return null
    return normalizeDecimal(1 / inverse, 9)
  })

  const result = computed(() => {
    if (resultOhm.value == null) return null
    return {
      total_ohm: resultOhm.value,
      total_in_output_unit: normalizeDecimal(fromOhm(resultOhm.value, form.output_unit), 9),
    }
  })

  function addResistor() {
    form.resistors.push(1000)
  }

  function removeResistor() {
    if (form.resistors.length <= 2) return
    form.resistors.pop()
  }

  function reset() {
    form.mode = 'parallel'
    form.input_unit = 'ohm'
    form.output_unit = 'ohm'
    form.resistors.splice(0, form.resistors.length, 1000, 1000)
  }

  return {
    form,
    canCalculate,
    sanitizedResistors,
    result,
    addResistor,
    removeResistor,
    reset,
  }
}
