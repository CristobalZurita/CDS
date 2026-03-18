import { computed, reactive } from 'vue'
import { normalizeDecimal } from '@/utils/format'

const formulaCards = [
  { key: 'V', title: 'Voltaje', expression: 'V = I x R' },
  { key: 'I', title: 'Corriente', expression: 'I = V / R' },
  { key: 'R', title: 'Resistencia', expression: 'R = V / I' },
  { key: 'P', title: 'Potencia', expression: 'P = V x I' }
]

function asNumber(value) {
  if (value === '' || value === null || value === undefined) return null
  const parsed = Number(value)
  if (!Number.isFinite(parsed)) return null
  if (parsed < 0) return null
  return parsed
}

export function useOhmsLawCalculator() {
  const form = reactive({
    voltage_v: '',
    current_a: '',
    resistance_ohm: ''
  })

  const parsed = computed(() => {
    const voltage = asNumber(form.voltage_v)
    const current = asNumber(form.current_a)
    const resistance = asNumber(form.resistance_ohm)
    return { voltage, current, resistance }
  })

  const knownCount = computed(() => {
    const { voltage, current, resistance } = parsed.value
    return [voltage, current, resistance].filter((entry) => entry !== null).length
  })

  const canCalculate = computed(() => knownCount.value >= 2)

  const result = computed(() => {
    if (!canCalculate.value) return null

    let { voltage, current, resistance } = parsed.value

    if (voltage !== null && current !== null && current !== 0) {
      resistance = voltage / current
    } else if (voltage !== null && resistance !== null && resistance !== 0) {
      current = voltage / resistance
    } else if (current !== null && resistance !== null) {
      voltage = current * resistance
    } else {
      return null
    }

    if (voltage === null || current === null || resistance === null) return null

    return {
      voltage_v: normalizeDecimal(voltage, 6),
      current_a: normalizeDecimal(current, 6),
      resistance_ohm: normalizeDecimal(resistance, 6),
      power_w: normalizeDecimal(voltage * current, 6)
    }
  })

  const inputState = computed(() => ({
    hasV: form.voltage_v !== '' && Number.isFinite(Number(form.voltage_v)) && Number(form.voltage_v) >= 0,
    hasI: form.current_a !== '' && Number.isFinite(Number(form.current_a)) && Number(form.current_a) >= 0,
    hasR: form.resistance_ohm !== '' && Number.isFinite(Number(form.resistance_ohm)) && Number(form.resistance_ohm) >= 0
  }))

  const solvedVariable = computed(() => {
    if (!canCalculate.value || !result.value) return null
    const { hasV, hasI, hasR } = inputState.value
    if (hasV && hasI) return 'R'
    if (hasV && hasR) return 'I'
    if (hasI && hasR) return 'V'
    return null
  })

  const solvedVariableLabel = computed(() => {
    if (solvedVariable.value === 'V') return 'Voltaje (V)'
    if (solvedVariable.value === 'I') return 'Corriente (I)'
    if (solvedVariable.value === 'R') return 'Resistencia (R)'
    return '-'
  })

  const displayResult = computed(() => (
    result.value || {
      voltage_v: '-',
      current_a: '-',
      resistance_ohm: '-',
      power_w: '-'
    }
  ))

  const numericResult = computed(() => (
    result.value || {
      voltage_v: 0,
      current_a: 0,
      resistance_ohm: 0,
      power_w: 0
    }
  ))

  const highlightedFormulas = computed(() => (
    solvedVariable.value ? [solvedVariable.value, 'P'] : []
  ))

  function meterPercent(value, softMax) {
    const numeric = Math.abs(Number(value))
    if (!Number.isFinite(numeric)) return 0
    return Math.min(100, (numeric / softMax) * 100)
  }

  const meterItems = computed(() => ([
    {
      key: 'V',
      label: 'Voltaje',
      unit: 'V',
      value: numericResult.value.voltage_v,
      percent: meterPercent(numericResult.value.voltage_v, 50),
      tone: 'voltage'
    },
    {
      key: 'I',
      label: 'Corriente',
      unit: 'A',
      value: numericResult.value.current_a,
      percent: meterPercent(numericResult.value.current_a, 5),
      tone: 'current'
    },
    {
      key: 'R',
      label: 'Resistencia',
      unit: 'Ohm',
      value: numericResult.value.resistance_ohm,
      percent: meterPercent(numericResult.value.resistance_ohm, 10000),
      tone: 'resistance'
    },
    {
      key: 'P',
      label: 'Potencia',
      unit: 'W',
      value: numericResult.value.power_w,
      percent: meterPercent(numericResult.value.power_w, 250),
      tone: 'power'
    }
  ]))

  function reset() {
    form.voltage_v = ''
    form.current_a = ''
    form.resistance_ohm = ''
  }

  return {
    form,
    canCalculate,
    result,
    displayResult,
    formulaCards,
    highlightedFormulas,
    meterItems,
    reset,
    solvedVariableLabel
  }
}
