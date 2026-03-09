import { computed, reactive } from 'vue'

const unitFactorMap = {
  mm: 0.001,
  cm: 0.01,
  m: 1,
  km: 1000,
  in: 0.0254,
  ft: 0.3048
}

export const lengthUnits = [
  { value: 'mm', label: 'Milímetros (mm)' },
  { value: 'cm', label: 'Centímetros (cm)' },
  { value: 'm', label: 'Metros (m)' },
  { value: 'km', label: 'Kilómetros (km)' },
  { value: 'in', label: 'Pulgadas (in)' },
  { value: 'ft', label: 'Pies (ft)' }
]

function normalizeDecimal(value, decimals = 6) {
  if (!Number.isFinite(value)) return null
  return Number(value.toFixed(decimals))
}

export function useLengthCalculator() {
  const form = reactive({
    value: '',
    from_unit: 'm',
    to_unit: 'cm'
  })

  const canConvert = computed(() => form.value !== '' && Number.isFinite(Number(form.value)))

  const result = computed(() => {
    if (!canConvert.value) return null

    const fromFactor = unitFactorMap[form.from_unit]
    const toFactor = unitFactorMap[form.to_unit]
    if (!fromFactor || !toFactor) return null

    const meters = Number(form.value) * fromFactor
    return normalizeDecimal(meters / toFactor, 6)
  })

  function reset() {
    form.value = ''
    form.from_unit = 'm'
    form.to_unit = 'cm'
  }

  return {
    form,
    canConvert,
    result,
    reset
  }
}
