import { computed, reactive } from 'vue'

function asNumber(value) {
  if (value === '' || value === null || value === undefined) return null
  const parsed = Number(value)
  if (!Number.isFinite(parsed)) return null
  if (parsed < 0) return null
  return parsed
}

function normalizeDecimal(value, decimals = 6) {
  if (!Number.isFinite(value)) return null
  return Number(value.toFixed(decimals))
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

  function reset() {
    form.voltage_v = ''
    form.current_a = ''
    form.resistance_ohm = ''
  }

  return {
    form,
    canCalculate,
    result,
    reset
  }
}
