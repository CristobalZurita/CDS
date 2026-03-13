import { computed, reactive } from 'vue'
import { normalizeDecimal } from '@/utils/format'
import { toHz, toFarad, toHenry } from '@/utils/units'

export const reactanceModeOptions = [
  { value: 'capacitive', label: 'Capacitiva (Xc)' },
  { value: 'inductive', label: 'Inductiva (Xl)' },
]

export const reactanceFrequencyUnitOptions = [
  { value: 'hz', label: 'Hz' },
  { value: 'khz', label: 'kHz' },
  { value: 'mhz', label: 'MHz' },
]

export const reactanceCapacitanceUnitOptions = [
  { value: 'pf', label: 'pF' },
  { value: 'nf', label: 'nF' },
  { value: 'uf', label: 'µF' },
  { value: 'mf', label: 'mF' },
  { value: 'f', label: 'F' },
]

export const reactanceInductanceUnitOptions = [
  { value: 'uh', label: 'µH' },
  { value: 'mh', label: 'mH' },
  { value: 'h', label: 'H' },
]

export function useReactanceCalculator() {
  const form = reactive({
    mode: 'capacitive',
    frequency_value: 1,
    frequency_unit: 'khz',
    capacitance_value: 100,
    capacitance_unit: 'nf',
    inductance_value: 10,
    inductance_unit: 'mh',
  })

  const canCalculate = computed(() => {
    const f = toHz(form.frequency_value, form.frequency_unit)
    if (!Number.isFinite(f) || f <= 0) return false

    if (form.mode === 'capacitive') {
      const c = toFarad(form.capacitance_value, form.capacitance_unit)
      return Number.isFinite(c) && c > 0
    }

    const l = toHenry(form.inductance_value, form.inductance_unit)
    return Number.isFinite(l) && l > 0
  })

  const result = computed(() => {
    if (!canCalculate.value) return null

    const f = toHz(form.frequency_value, form.frequency_unit)

    if (form.mode === 'capacitive') {
      const c = toFarad(form.capacitance_value, form.capacitance_unit)
      const xc = 1 / (2 * Math.PI * f * c)
      return {
        mode: 'capacitive',
        reactance_ohm: normalizeDecimal(xc, 9),
      }
    }

    const l = toHenry(form.inductance_value, form.inductance_unit)
    const xl = 2 * Math.PI * f * l
    return {
      mode: 'inductive',
      reactance_ohm: normalizeDecimal(xl, 9),
    }
  })

  function reset() {
    form.mode = 'capacitive'
    form.frequency_value = 1
    form.frequency_unit = 'khz'
    form.capacitance_value = 100
    form.capacitance_unit = 'nf'
    form.inductance_value = 10
    form.inductance_unit = 'mh'
  }

  return {
    form,
    canCalculate,
    result,
    reset,
  }
}
