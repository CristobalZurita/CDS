import { computed, reactive } from 'vue'
import { normalizeDecimal } from '@/utils/format'
import { toFarad, fromFarad } from '@/utils/units'

export const capacitorNetworkModes = [
  { value: 'series', label: 'Serie' },
  { value: 'parallel', label: 'Paralelo' },
]

export const capacitorUnitOptions = [
  { value: 'pf', label: 'pF' },
  { value: 'nf', label: 'nF' },
  { value: 'uf', label: 'µF' },
  { value: 'mf', label: 'mF' },
  { value: 'f', label: 'F' },
]

export function useSeriesParallelCapacitorCalculator() {
  const form = reactive({
    mode: 'series',
    input_unit: 'uf',
    output_unit: 'uf',
    capacitors: [10, 10],
  })

  const sanitizedCapacitors = computed(() =>
    form.capacitors
      .map((value) => toFarad(value, form.input_unit))
      .filter((value) => Number.isFinite(value) && value > 0)
  )

  const canCalculate = computed(() => sanitizedCapacitors.value.length >= 2)

  const resultFarad = computed(() => {
    if (!canCalculate.value) return null

    if (form.mode === 'parallel') {
      return normalizeDecimal(sanitizedCapacitors.value.reduce((acc, value) => acc + value, 0), 12)
    }

    const inverse = sanitizedCapacitors.value.reduce((acc, value) => acc + (1 / value), 0)
    if (inverse <= 0) return null
    return normalizeDecimal(1 / inverse, 12)
  })

  const result = computed(() => {
    if (resultFarad.value == null) return null
    return {
      total_f: resultFarad.value,
      total_in_output_unit: normalizeDecimal(fromFarad(resultFarad.value, form.output_unit), 12),
    }
  })

  function addCapacitor() {
    form.capacitors.push(10)
  }

  function removeCapacitor() {
    if (form.capacitors.length <= 2) return
    form.capacitors.pop()
  }

  function reset() {
    form.mode = 'series'
    form.input_unit = 'uf'
    form.output_unit = 'uf'
    form.capacitors.splice(0, form.capacitors.length, 10, 10)
  }

  return {
    form,
    canCalculate,
    sanitizedCapacitors,
    result,
    addCapacitor,
    removeCapacitor,
    reset,
  }
}
