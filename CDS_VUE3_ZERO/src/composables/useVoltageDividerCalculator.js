import { computed, reactive } from 'vue'

const resistanceUnitFactor = {
  ohm: 1,
  kohm: 1000,
  mohm: 1000000,
}

function toOhm(value, unit) {
  const factor = resistanceUnitFactor[unit] || 1
  return Number(value) * factor
}

function normalizeDecimal(value, decimals = 6) {
  if (!Number.isFinite(value)) return null
  return Number(value.toFixed(decimals))
}

export const voltageDividerResistanceUnits = [
  { value: 'ohm', label: 'Ω' },
  { value: 'kohm', label: 'kΩ' },
  { value: 'mohm', label: 'MΩ' },
]

export function useVoltageDividerCalculator() {
  const form = reactive({
    vin_v: 12,
    r1_value: 10000,
    r1_unit: 'ohm',
    r2_value: 10000,
    r2_unit: 'ohm',
  })

  const canCalculate = computed(() => {
    const vin = Number(form.vin_v)
    const r1 = toOhm(form.r1_value, form.r1_unit)
    const r2 = toOhm(form.r2_value, form.r2_unit)
    return Number.isFinite(vin) && vin > 0 && Number.isFinite(r1) && r1 > 0 && Number.isFinite(r2) && r2 > 0
  })

  const result = computed(() => {
    if (!canCalculate.value) return null

    const vin = Number(form.vin_v)
    const r1 = toOhm(form.r1_value, form.r1_unit)
    const r2 = toOhm(form.r2_value, form.r2_unit)
    const total = r1 + r2
    const currentA = vin / total
    const vout = vin * (r2 / total)

    return {
      vout_v: normalizeDecimal(vout, 6),
      current_a: normalizeDecimal(currentA, 9),
      current_ma: normalizeDecimal(currentA * 1000, 6),
      p_r1_w: normalizeDecimal(currentA * currentA * r1, 9),
      p_r2_w: normalizeDecimal(currentA * currentA * r2, 9),
      ratio: normalizeDecimal(r2 / total, 9),
    }
  })

  return {
    form,
    canCalculate,
    result,
  }
}
