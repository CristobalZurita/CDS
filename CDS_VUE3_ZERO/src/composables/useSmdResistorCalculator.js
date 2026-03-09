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
  if (valueOhm >= 1 && valueOhm < 1000 && valueOhm % 1 !== 0) return `${valueOhm.toFixed(3)} Ω`
  if (valueOhm >= 1000000) return `${(valueOhm / 1000000).toFixed(3)} MΩ`
  if (valueOhm >= 1000) return `${(valueOhm / 1000).toFixed(3)} kΩ`
  return `${valueOhm.toFixed(3)} Ω`
}

function decodeRNotation(code) {
  const hasR = code.includes('R')
  if (!hasR) return null
  if ((code.match(/R/g) || []).length !== 1) return null
  if (!/^[0-9R]+$/.test(code)) return null

  const decimalNotation = code.replace('R', '.')
  const resistanceOhm = Number(decimalNotation)
  if (!Number.isFinite(resistanceOhm)) return null

  return {
    mode: 'R_NOTATION',
    resistance_ohm: resistanceOhm,
    significant: null,
    multiplier: null,
    multiplierLabel: null,
    normalizedCode: code
  }
}

function decodeSmdResistor(code, type) {
  const normalized = String(code || '').trim().toUpperCase()
  if (!normalized) return null

  const rNotationResult = decodeRNotation(normalized)
  if (rNotationResult) return rNotationResult

  if (type === 'EIA3' && /^\d{3}$/.test(normalized)) {
    const sig = Number(normalized.slice(0, 2))
    const mult = Math.pow(10, Number(normalized[2]))
    return {
      mode: 'EIA3',
      resistance_ohm: sig * mult,
      significant: sig,
      multiplier: mult,
      multiplierLabel: `10^${normalized[2]}`,
      normalizedCode: normalized
    }
  }

  if (type === 'EIA4' && /^\d{4}$/.test(normalized)) {
    const sig = Number(normalized.slice(0, 3))
    const mult = Math.pow(10, Number(normalized[3]))
    return {
      mode: 'EIA4',
      resistance_ohm: sig * mult,
      significant: sig,
      multiplier: mult,
      multiplierLabel: `10^${normalized[3]}`,
      normalizedCode: normalized
    }
  }

  if (type === 'EIA96' && /^\d{2}[ZYRXSBHC]$/.test(normalized)) {
    const index = Number(normalized.slice(0, 2)) - 1
    const base = e96Values[index]
    const multCode = normalized[2]
    const mult = e96MultiplierMap[multCode]
    if (!Number.isFinite(base) || !Number.isFinite(mult)) return null
    return {
      mode: 'EIA96',
      resistance_ohm: base * mult,
      significant: base,
      multiplier: mult,
      multiplierLabel: multCode,
      normalizedCode: normalized
    }
  }

  return null
}

export function useSmdResistorCalculator() {
  const form = reactive({
    code: '',
    type: 'EIA3'
  })

  const decoded = computed(() => decodeSmdResistor(form.code, form.type))
  const resistanceOhm = computed(() => decoded.value?.resistance_ohm ?? Number.NaN)
  const isValid = computed(() => Number.isFinite(resistanceOhm.value))
  const formattedResistance = computed(() => formatResistance(resistanceOhm.value))

  const formulaText = computed(() => {
    if (!decoded.value) return '—'
    if (decoded.value.mode === 'R_NOTATION') return `R como punto decimal: ${decoded.value.normalizedCode}`
    if (decoded.value.mode === 'EIA96') return `${decoded.value.significant} × ${decoded.value.multiplierLabel}`
    if (decoded.value.mode === 'EIA3' || decoded.value.mode === 'EIA4') {
      return `${decoded.value.significant} × ${decoded.value.multiplierLabel}`
    }
    return '—'
  })

  const modeLabel = computed(() => {
    if (!decoded.value) return '—'
    if (decoded.value.mode === 'R_NOTATION') return 'Notación R'
    if (decoded.value.mode === 'EIA3') return 'EIA-3'
    if (decoded.value.mode === 'EIA4') return 'EIA-4'
    if (decoded.value.mode === 'EIA96') return 'EIA-96'
    return '—'
  })

  function reset() {
    form.code = ''
    form.type = 'EIA3'
  }

  return {
    form,
    decoded,
    resistanceOhm,
    isValid,
    formattedResistance,
    formulaText,
    modeLabel,
    reset
  }
}
