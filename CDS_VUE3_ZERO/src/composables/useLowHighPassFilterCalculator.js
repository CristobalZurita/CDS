import { computed, reactive } from 'vue'

const resistanceUnitFactor = {
  ohm: 1,
  kohm: 1000,
  mohm: 1000000,
}

const capacitanceUnitFactor = {
  pf: 1e-12,
  nf: 1e-9,
  uf: 1e-6,
  mf: 1e-3,
  f: 1,
}

const frequencyUnitFactor = {
  hz: 1,
  khz: 1000,
  mhz: 1000000,
}

function normalizeDecimal(value, decimals = 9) {
  if (!Number.isFinite(value)) return null
  return Number(value.toFixed(decimals))
}

function toOhm(value, unit) {
  return Number(value) * (resistanceUnitFactor[unit] || 1)
}

function toFarad(value, unit) {
  return Number(value) * (capacitanceUnitFactor[unit] || 1)
}

function toHz(value, unit) {
  return Number(value) * (frequencyUnitFactor[unit] || 1)
}

export const filterModeOptions = [
  { value: 'lowpass', label: 'Low Pass' },
  { value: 'highpass', label: 'High Pass' },
]

export const filterResistanceUnitOptions = [
  { value: 'ohm', label: 'Ω' },
  { value: 'kohm', label: 'kΩ' },
  { value: 'mohm', label: 'MΩ' },
]

export const filterCapacitanceUnitOptions = [
  { value: 'pf', label: 'pF' },
  { value: 'nf', label: 'nF' },
  { value: 'uf', label: 'µF' },
  { value: 'mf', label: 'mF' },
  { value: 'f', label: 'F' },
]

export const filterFrequencyUnitOptions = [
  { value: 'hz', label: 'Hz' },
  { value: 'khz', label: 'kHz' },
  { value: 'mhz', label: 'MHz' },
]

export function useLowHighPassFilterCalculator() {
  const form = reactive({
    mode: 'lowpass',
    r_value: 1,
    r_unit: 'kohm',
    c_value: 100,
    c_unit: 'nf',
    frequency_value: 1000,
    frequency_unit: 'hz',
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
    const fc = 1 / (2 * Math.PI * r * c)

    const f = toHz(form.frequency_value, form.frequency_unit)
    const ratio = f > 0 ? (f / fc) : 0

    let gain = null
    if (f > 0) {
      if (form.mode === 'lowpass') {
        gain = 1 / Math.sqrt(1 + (ratio * ratio))
      } else {
        gain = ratio / Math.sqrt(1 + (ratio * ratio))
      }
    }

    const gainDb = gain && gain > 0 ? (20 * Math.log10(gain)) : null

    return {
      cutoff_hz: normalizeDecimal(fc, 9),
      gain_ratio: gain == null ? null : normalizeDecimal(gain, 9),
      gain_percent: gain == null ? null : normalizeDecimal(gain * 100, 6),
      gain_db: gainDb == null ? null : normalizeDecimal(gainDb, 6),
    }
  })

  function reset() {
    form.mode = 'lowpass'
    form.r_value = 1
    form.r_unit = 'kohm'
    form.c_value = 100
    form.c_unit = 'nf'
    form.frequency_value = 1000
    form.frequency_unit = 'hz'
  }

  return {
    form,
    canCalculate,
    result,
    reset,
  }
}
