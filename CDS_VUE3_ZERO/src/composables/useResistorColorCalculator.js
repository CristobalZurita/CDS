import { computed, reactive } from 'vue'

const digitMap = {
  black: 0,
  brown: 1,
  red: 2,
  orange: 3,
  yellow: 4,
  green: 5,
  blue: 6,
  violet: 7,
  gray: 8,
  white: 9
}

const multiplierMap = {
  black: 1,
  brown: 10,
  red: 100,
  orange: 1000,
  yellow: 10000,
  green: 100000,
  blue: 1000000,
  violet: 10000000,
  gray: 100000000,
  white: 1000000000,
  gold: 0.1,
  silver: 0.01
}

const toleranceMap = {
  brown: 1,
  red: 2,
  green: 0.5,
  blue: 0.25,
  violet: 0.1,
  gray: 0.05,
  gold: 5,
  silver: 10
}

const tempcoMap = {
  brown: 100,
  red: 50,
  orange: 15,
  yellow: 25,
  blue: 10,
  violet: 5
}

const colorLabels = {
  black: 'Negro',
  brown: 'Café',
  red: 'Rojo',
  orange: 'Naranja',
  yellow: 'Amarillo',
  green: 'Verde',
  blue: 'Azul',
  violet: 'Violeta',
  gray: 'Gris',
  white: 'Blanco',
  gold: 'Oro',
  silver: 'Plata'
}

const colorPalette = {
  black: { swatch: '#111111', textColor: '#ffffff', borderColor: '#111111' },
  brown: { swatch: '#6f4a2a', textColor: '#ffffff', borderColor: '#6f4a2a' },
  red: { swatch: '#d83a22', textColor: '#ffffff', borderColor: '#d83a22' },
  orange: { swatch: '#df7a43', textColor: '#ffffff', borderColor: '#df7a43' },
  yellow: { swatch: '#efd35a', textColor: '#2d2414', borderColor: '#d1b53d' },
  green: { swatch: '#4a8b58', textColor: '#ffffff', borderColor: '#4a8b58' },
  blue: { swatch: '#2f63a7', textColor: '#ffffff', borderColor: '#2f63a7' },
  violet: { swatch: '#6e67ca', textColor: '#ffffff', borderColor: '#6e67ca' },
  gray: { swatch: '#8b8b8b', textColor: '#ffffff', borderColor: '#8b8b8b' },
  white: { swatch: '#ffffff', textColor: '#202020', borderColor: '#b8b8b8' },
  gold: { swatch: '#cfab46', textColor: '#20180b', borderColor: '#b7922e' },
  silver: { swatch: '#c5ccd7', textColor: '#1e293b', borderColor: '#9aa5b1' }
}

const digitColorKeys = ['black', 'brown', 'red', 'orange', 'yellow', 'green', 'blue', 'violet', 'gray', 'white']
const multiplierColorKeys = ['silver', 'gold', ...digitColorKeys]
const toleranceColorKeys = ['brown', 'red', 'green', 'blue', 'violet', 'gray', 'gold', 'silver']
const tempcoColorKeys = ['brown', 'red', 'orange', 'yellow', 'blue', 'violet']

function formatMultiplierBadge(value) {
  if (value === 0.01) return 'x0.01'
  if (value === 0.1) return 'x0.1'
  if (value >= 1000000000) return `x${value / 1000000000}G`
  if (value >= 1000000) return `x${value / 1000000}M`
  if (value >= 1000) return `x${value / 1000}k`
  return `x${value}`
}

function createOption(value, badgeResolver = null) {
  const palette = colorPalette[value] || {}
  return {
    value,
    label: colorLabels[value] || value,
    badge: badgeResolver ? badgeResolver(value) : '',
    swatch: palette.swatch,
    textColor: palette.textColor,
    borderColor: palette.borderColor
  }
}

export const digitColorOptions = digitColorKeys.map((value) => createOption(value, (color) => String(digitMap[color] ?? '')))
export const multiplierColorOptions = multiplierColorKeys.map((value) => createOption(value, (color) => formatMultiplierBadge(multiplierMap[color] ?? 1)))
export const toleranceColorOptions = toleranceColorKeys.map((value) => createOption(value, (color) => `±${toleranceMap[color] ?? 5}%`))
export const tempcoColorOptions = tempcoColorKeys.map((value) => createOption(value, (color) => `${tempcoMap[color] ?? '—'} ppm`))

function formatResistance(valueOhm) {
  if (!Number.isFinite(valueOhm)) return '—'
  const abs = Math.abs(valueOhm)
  if (abs >= 1000000) return `${(valueOhm / 1000000).toFixed(3)} MΩ`
  if (abs >= 1000) return `${(valueOhm / 1000).toFixed(3)} kΩ`
  return `${valueOhm.toFixed(3)} Ω`
}

export function useResistorColorCalculator() {
  const form = reactive({
    bands: 4,
    colors: ['brown', 'black', 'red', 'gold', 'brown', 'brown']
  })

  const digitsCount = computed(() => (form.bands >= 5 ? 3 : 2))
  const multiplierIndex = computed(() => digitsCount.value)
  const toleranceIndex = computed(() => digitsCount.value + 1)
  const tempcoIndex = computed(() => digitsCount.value + 2)

  const result = computed(() => {
    const digits = form.colors.slice(0, digitsCount.value).map((color) => digitMap[color] ?? 0)
    const significant = Number(digits.join(''))
    const multiplierColor = form.colors[multiplierIndex.value]
    const toleranceColor = form.colors[toleranceIndex.value]

    const multiplier = multiplierMap[multiplierColor] ?? 1
    const resistanceOhm = significant * multiplier
    const tolerancePercent = toleranceMap[toleranceColor] ?? 5
    const minOhm = resistanceOhm * (1 - tolerancePercent / 100)
    const maxOhm = resistanceOhm * (1 + tolerancePercent / 100)

    const tempcoColor = form.colors[tempcoIndex.value]
    const tempcoPpm = form.bands === 6 ? tempcoMap[tempcoColor] : undefined

    return {
      resistance_ohm: resistanceOhm,
      tolerance_percent: tolerancePercent,
      min_ohm: minOhm,
      max_ohm: maxOhm,
      tempco_ppm: tempcoPpm,
      formattedResistance: formatResistance(resistanceOhm),
      formattedRange: `${formatResistance(minOhm)} - ${formatResistance(maxOhm)}`
    }
  })

  const previewBands = computed(() => form.colors.slice(0, form.bands))

  const bandSummaries = computed(() => {
    const summaries = []
    const digitLabels = digitsCount.value === 2
      ? ['1ra cifra', '2da cifra']
      : ['1ra cifra', '2da cifra', '3ra cifra']

    for (let index = 0; index < digitsCount.value; index += 1) {
      const color = form.colors[index]
      summaries.push({
        roleLabel: digitLabels[index],
        valueText: String(digitMap[color] ?? '—'),
        color,
        ...(colorPalette[color] || {})
      })
    }

    const multiplierColor = form.colors[multiplierIndex.value]
    summaries.push({
      roleLabel: 'Multiplicador',
      valueText: formatMultiplierBadge(multiplierMap[multiplierColor] ?? 1),
      color: multiplierColor,
      ...(colorPalette[multiplierColor] || {})
    })

    const toleranceColor = form.colors[toleranceIndex.value]
    summaries.push({
      roleLabel: 'Tolerancia',
      valueText: `±${toleranceMap[toleranceColor] ?? 5}%`,
      color: toleranceColor,
      ...(colorPalette[toleranceColor] || {})
    })

    if (form.bands === 6) {
      const tempcoColor = form.colors[tempcoIndex.value]
      summaries.push({
        roleLabel: 'Tempco',
        valueText: `${tempcoMap[tempcoColor] ?? '—'} ppm`,
        color: tempcoColor,
        ...(colorPalette[tempcoColor] || {})
      })
    }

    return summaries
  })

  function setBands(nextBands) {
    form.bands = nextBands
  }

  function applyBands(bands) {
    setBands(bands)
    if (bands === 4) {
      form.colors.splice(0, form.colors.length, 'brown', 'black', 'red', 'gold', 'brown', 'brown')
    }
    if (bands === 5 || bands === 6) {
      form.colors.splice(0, form.colors.length, 'brown', 'black', 'black', 'red', 'brown', 'brown')
    }
  }

  function resetBands() {
    applyBands(4)
  }

  function bandClass(color) {
    const normalized = String(color || '').toLowerCase()
    return normalized ? `band-${normalized}` : 'band-default'
  }

  return {
    form,
    digitsCount,
    multiplierIndex,
    toleranceIndex,
    tempcoIndex,
    previewBands,
    bandSummaries,
    result,
    applyBands,
    bandClass,
    resetBands,
    setBands
  }
}
