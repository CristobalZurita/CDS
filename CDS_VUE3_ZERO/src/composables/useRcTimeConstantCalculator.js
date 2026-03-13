import { computed, reactive } from 'vue'
import { normalizeDecimal } from '@/utils/format'
import { toOhm, toFarad } from '@/utils/units'

export const rcResistanceUnitOptions = [
  { value: 'ohm', label: 'Ω' },
  { value: 'kohm', label: 'kΩ' },
  { value: 'mohm', label: 'MΩ' },
]

export const rcCapacitanceUnitOptions = [
  { value: 'pf', label: 'pF' },
  { value: 'nf', label: 'nF' },
  { value: 'uf', label: 'µF' },
  { value: 'mf', label: 'mF' },
  { value: 'f', label: 'F' },
]

export function useRcTimeConstantCalculator() {
  const form = reactive({
    r_value: 10,
    r_unit: 'kohm',
    c_value: 100,
    c_unit: 'nf',
    target_percent: 63.2,
  })

  const canCalculate = computed(() => {
    const r = toOhm(form.r_value, form.r_unit)
    const c = toFarad(form.c_value, form.c_unit)
    return Number.isFinite(r) && r > 0 && Number.isFinite(c) && c > 0
  })

  const result = computed(() => {
    if (!canCalculate.value) return null

    const r = toOhm(form.r_value, form.r_unit)
    const c = toFarad(form.c_value, form.c_unit)
    const tau = r * c
    const cutoff = 1 / (2 * Math.PI * r * c)

    const percent = Math.min(Math.max(Number(form.target_percent), 1), 99.999)
    const target = percent / 100
    const tCharge = -tau * Math.log(1 - target)

    return {
      tau_s: normalizeDecimal(tau, 12),
      tau_ms: normalizeDecimal(tau * 1000, 9),
      five_tau_s: normalizeDecimal(tau * 5, 12),
      cutoff_hz: normalizeDecimal(cutoff, 9),
      target_percent: normalizeDecimal(percent, 4),
      t_charge_s: normalizeDecimal(tCharge, 12),
    }
  })

  function reset() {
    form.r_value = 10
    form.r_unit = 'kohm'
    form.c_value = 100
    form.c_unit = 'nf'
    form.target_percent = 63.2
  }

  return {
    form,
    canCalculate,
    result,
    reset,
  }
}
