import { computed, reactive } from 'vue'

const resistanceUnitFactor = {
  ohm: 1,
  kohm: 1000,
  mohm: 1000000
}

const capacitanceUnitFactor = {
  pf: 1e-12,
  nf: 1e-9,
  uf: 1e-6
}

export const timer555ModeOptions = [
  { value: 'astable_standard', label: 'Astable' },
  { value: 'monostable', label: 'Monostable' }
]

function toResistance(value, unit) {
  const factor = resistanceUnitFactor[unit] || 1
  return Number(value) * factor
}

function toCapacitance(value, unit) {
  const factor = capacitanceUnitFactor[unit] || 1e-6
  return Number(value) * factor
}

function normalizeDecimal(value, decimals = 9) {
  if (!Number.isFinite(value)) return null
  return Number(value.toFixed(decimals))
}

export function useTimer555Calculator() {
  const form = reactive({
    mode: 'astable_standard',
    r1_value: 1,
    r1_unit: 'kohm',
    r2_value: 330,
    r2_unit: 'kohm',
    r_value: 1,
    r_unit: 'kohm',
    c_value: 2.2,
    c_unit: 'uf',
    vcc_v: 5
  })

  const isAstable = computed(() => form.mode === 'astable_standard')
  const isMonostable = computed(() => form.mode === 'monostable')

  const canCalculate = computed(() => {
    const c = toCapacitance(form.c_value, form.c_unit)
    if (!Number.isFinite(c) || c <= 0) return false
    if (isAstable.value) {
      const r1 = toResistance(form.r1_value, form.r1_unit)
      const r2 = toResistance(form.r2_value, form.r2_unit)
      return Number.isFinite(r1) && r1 > 0 && Number.isFinite(r2) && r2 > 0
    }
    const r = toResistance(form.r_value, form.r_unit)
    return Number.isFinite(r) && r > 0
  })

  const result = computed(() => {
    if (!canCalculate.value) return null
    const c = toCapacitance(form.c_value, form.c_unit)

    if (isMonostable.value) {
      const r = toResistance(form.r_value, form.r_unit)
      const period = 1.0986 * r * c
      return {
        period_s: normalizeDecimal(period),
        frequency_hz: period > 0 ? normalizeDecimal(1 / period) : null
      }
    }

    const r1 = toResistance(form.r1_value, form.r1_unit)
    const r2 = toResistance(form.r2_value, form.r2_unit)
    const tHigh = 0.693 * (r1 + r2) * c
    const tLow = 0.693 * r2 * c
    const period = tHigh + tLow
    const frequency = period > 0 ? 1 / period : 0
    const dutyCycle = period > 0 ? tHigh / period : 0

    return {
      t_high_s: normalizeDecimal(tHigh),
      t_low_s: normalizeDecimal(tLow),
      period_s: normalizeDecimal(period),
      frequency_hz: normalizeDecimal(frequency),
      duty_cycle: normalizeDecimal(dutyCycle)
    }
  })

  function reset() {
    form.mode = 'astable_standard'
    form.r1_value = 1
    form.r1_unit = 'kohm'
    form.r2_value = 330
    form.r2_unit = 'kohm'
    form.r_value = 1
    form.r_unit = 'kohm'
    form.c_value = 2.2
    form.c_unit = 'uf'
    form.vcc_v = 5
  }

  return {
    form,
    isAstable,
    isMonostable,
    canCalculate,
    result,
    reset
  }
}
