import { computed, reactive } from 'vue'
import { normalizeDecimal } from '@/utils/format'

export function useAwgCalculator() {
  const form = reactive({
    awg: 24
  })

  const parsedAwg = computed(() => Number(form.awg))
  const canCalculate = computed(() => Number.isFinite(parsedAwg.value) && parsedAwg.value >= 0)

  const result = computed(() => {
    if (!canCalculate.value) return null
    const awg = parsedAwg.value

    const diameterMm = 0.127 * Math.pow(92, (36 - awg) / 39)
    const areaMm2 = Math.PI * Math.pow(diameterMm / 2, 2)
    const resistanceOhmPerKm = (0.017241 / areaMm2) * 1000

    return {
      diameter_mm: normalizeDecimal(diameterMm, 6),
      area_mm2: normalizeDecimal(areaMm2, 6),
      resistance_ohm_per_km: normalizeDecimal(resistanceOhmPerKm, 6)
    }
  })

  function reset() {
    form.awg = 24
  }

  return {
    form,
    canCalculate,
    result,
    reset
  }
}
