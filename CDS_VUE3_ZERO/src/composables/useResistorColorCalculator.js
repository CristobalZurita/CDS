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

const digitColorKeys = ['black', 'brown', 'red', 'orange', 'yellow', 'green', 'blue', 'violet', 'gray', 'white']
const multiplierColorKeys = ['silver', 'gold', ...digitColorKeys]
const toleranceColorKeys = ['brown', 'red', 'green', 'blue', 'violet', 'gray', 'gold', 'silver']
const tempcoColorKeys = ['brown', 'red', 'orange', 'yellow', 'blue', 'violet']

function createOption(value) {
  return { value, label: colorLabels[value] || value }
}

export const digitColorOptions = digitColorKeys.map(createOption)
export const multiplierColorOptions = multiplierColorKeys.map(createOption)
export const toleranceColorOptions = toleranceColorKeys.map(createOption)
export const tempcoColorOptions = tempcoColorKeys.map(createOption)

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

  function setBands(nextBands) {
    form.bands = nextBands
  }

  return {
    form,
    digitsCount,
    multiplierIndex,
    toleranceIndex,
    tempcoIndex,
    result,
    setBands
  }
}
