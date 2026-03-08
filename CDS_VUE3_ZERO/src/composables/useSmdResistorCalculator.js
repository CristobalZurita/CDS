import { computed, reactive } from 'vue'

const e96Values = [
  100, 102, 105, 107, 110, 113, 115, 118, 121, 124, 127, 130,
  133, 137, 140, 143, 147, 150, 154, 158, 162, 165, 169, 174,
  178, 182, 187, 191, 196, 200, 205, 210, 215, 221, 226, 232,
  237, 243, 249, 255, 261, 267, 274, 280, 287, 294, 301, 309,
  316, 324, 332, 340, 348, 357, 365, 374, 383, 392, 402, 412,
  422, 432, 442, 453, 464, 475, 487, 499, 511, 523, 536, 549,
  562, 576, 590, 604, 619, 634, 649, 665, 681, 698, 715, 732,
  750, 768, 787, 806, 825, 845, 866, 887, 909, 931, 953, 976
]

const e96MultiplierMap = {
  Z: 0.001,
  Y: 0.01,
  R: 0.1,
  X: 1,
  S: 10,
  B: 100,
  H: 1000,
  C: 10000
}

export const smdResistorTypeOptions = [
  { value: 'EIA3', label: 'EIA-3 (3 dígitos)' },
  { value: 'EIA4', label: 'EIA-4 (4 dígitos)' },
  { value: 'EIA96', label: 'EIA-96 (2 dígitos + letra)' }
]

function formatResistance(valueOhm) {
  if (!Number.isFinite(valueOhm)) return '—'
  if (valueOhm >= 1000000) return `${(valueOhm / 1000000).toFixed(3)} MΩ`
  if (valueOhm >= 1000) return `${(valueOhm / 1000).toFixed(3)} kΩ`
  return `${valueOhm.toFixed(3)} Ω`
}

function decodeSmdResistor(code, type) {
  const normalized = String(code || '').trim().toUpperCase()
  if (!normalized) return Number.NaN

  if (type === 'EIA3' && normalized.length === 3) {
    const sig = Number(normalized.slice(0, 2))
    const mult = Math.pow(10, Number(normalized[2]))
    return sig * mult
  }

  if (type === 'EIA4' && normalized.length === 4) {
    const sig = Number(normalized.slice(0, 3))
    const mult = Math.pow(10, Number(normalized[3]))
    return sig * mult
  }

  if (type === 'EIA96' && normalized.length >= 3) {
    const index = Number(normalized.slice(0, 2)) - 1
    const base = e96Values[index] ?? 100
    const mult = e96MultiplierMap[normalized[2]] ?? 1
    return base * mult
  }

  return Number.NaN
}

export function useSmdResistorCalculator() {
  const form = reactive({
    code: '',
    type: 'EIA3'
  })

  const resistanceOhm = computed(() => decodeSmdResistor(form.code, form.type))
  const isValid = computed(() => Number.isFinite(resistanceOhm.value))
  const formattedResistance = computed(() => formatResistance(resistanceOhm.value))

  return {
    form,
    resistanceOhm,
    isValid,
    formattedResistance
  }
}
