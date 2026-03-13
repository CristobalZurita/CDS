import { computed, reactive } from 'vue'
import { normalizeDecimal } from '@/utils/format'
import { toAmp } from '@/utils/units'

export const ledCurrentUnitOptions = [
  { value: 'ma', label: 'mA' },
  { value: 'a', label: 'A' },
]

export function useLedSeriesResistorCalculator() {
  const form = reactive({
    supply_v: 12,
    led_forward_v: 2,
    led_count: 1,
    led_current_value: 20,
    led_current_unit: 'ma',
  })

  const canCalculate = computed(() => {
    const vs = Number(form.supply_v)
    const vf = Number(form.led_forward_v)
    const count = Number(form.led_count)
    const i = toAmp(form.led_current_value, form.led_current_unit)
    return Number.isFinite(vs) && vs > 0 && Number.isFinite(vf) && vf > 0 && Number.isFinite(count) && count > 0 && Number.isFinite(i) && i > 0
  })

  const result = computed(() => {
    if (!canCalculate.value) return null

    const vs = Number(form.supply_v)
    const vfTotal = Number(form.led_forward_v) * Number(form.led_count)
    const i = toAmp(form.led_current_value, form.led_current_unit)

    const vResistor = vs - vfTotal
    if (!(vResistor > 0)) {
      return {
        error: 'La suma de voltajes de LED debe ser menor que la fuente.',
      }
    }

    const resistorOhm = vResistor / i
    const resistorPowerW = vResistor * i

    return {
      resistor_ohm: normalizeDecimal(resistorOhm, 6),
      resistor_power_w: normalizeDecimal(resistorPowerW, 9),
      recommended_power_w: normalizeDecimal(resistorPowerW * 2, 6),
      voltage_drop_v: normalizeDecimal(vResistor, 6),
      led_current_a: normalizeDecimal(i, 9),
    }
  })

  function reset() {
    form.supply_v = 12
    form.led_forward_v = 2
    form.led_count = 1
    form.led_current_value = 20
    form.led_current_unit = 'ma'
  }

  return {
    form,
    canCalculate,
    result,
    reset,
  }
}
