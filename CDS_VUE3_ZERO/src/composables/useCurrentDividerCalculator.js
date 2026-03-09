import { computed, reactive } from 'vue'

const resistanceUnitFactor = {
  ohm: 1,
  kohm: 1000,
  mohm: 1000000,
}

const currentUnitFactor = {
  a: 1,
  ma: 1e-3,
}

function toOhm(value, unit) {
  return Number(value) * (resistanceUnitFactor[unit] || 1)
}

function toAmp(value, unit) {
  return Number(value) * (currentUnitFactor[unit] || 1)
}

function fromAmp(value, unit) {
  const factor = currentUnitFactor[unit] || 1
  return value / factor
}

function normalizeDecimal(value, decimals = 9) {
  if (!Number.isFinite(value)) return null
  return Number(value.toFixed(decimals))
}

export const currentDividerResistanceUnitOptions = [
  { value: 'ohm', label: 'Ω' },
  { value: 'kohm', label: 'kΩ' },
  { value: 'mohm', label: 'MΩ' },
]

export const currentDividerCurrentUnitOptions = [
  { value: 'a', label: 'A' },
  { value: 'ma', label: 'mA' },
]

export function useCurrentDividerCalculator() {
  const form = reactive({
    total_current_value: 10,
    total_current_unit: 'ma',
    resistor_unit: 'ohm',
    output_current_unit: 'ma',
    resistors: [1000, 2200],
  })

  const totalCurrentA = computed(() => toAmp(form.total_current_value, form.total_current_unit))

  const sanitizedResistors = computed(() =>
    form.resistors
      .map((value) => toOhm(value, form.resistor_unit))
      .filter((value) => Number.isFinite(value) && value > 0)
  )

  const canCalculate = computed(() =>
    Number.isFinite(totalCurrentA.value) && totalCurrentA.value > 0 && sanitizedResistors.value.length >= 2
  )

  const branchCurrentsA = computed(() => {
    if (!canCalculate.value) return []

    const conductanceSum = sanitizedResistors.value.reduce((acc, value) => acc + (1 / value), 0)
    if (conductanceSum <= 0) return []

    return sanitizedResistors.value.map((resistance) => {
      const ratio = (1 / resistance) / conductanceSum
      return totalCurrentA.value * ratio
    })
  })

  const result = computed(() => {
    if (!canCalculate.value || branchCurrentsA.value.length === 0) return null

    return {
      total_current_a: normalizeDecimal(totalCurrentA.value, 9),
      total_current_output_unit: normalizeDecimal(fromAmp(totalCurrentA.value, form.output_current_unit), 9),
      branches: branchCurrentsA.value.map((value, index) => ({
        index: index + 1,
        current_a: normalizeDecimal(value, 9),
        current_output_unit: normalizeDecimal(fromAmp(value, form.output_current_unit), 9),
      })),
    }
  })

  function addBranch() {
    form.resistors.push(1000)
  }

  function removeBranch() {
    if (form.resistors.length <= 2) return
    form.resistors.pop()
  }

  function reset() {
    form.total_current_value = 10
    form.total_current_unit = 'ma'
    form.resistor_unit = 'ohm'
    form.output_current_unit = 'ma'
    form.resistors.splice(0, form.resistors.length, 1000, 2200)
  }

  return {
    form,
    canCalculate,
    result,
    addBranch,
    removeBranch,
    reset,
  }
}
