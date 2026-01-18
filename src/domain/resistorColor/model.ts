import { ResistorColorInput, ResistorColorOutput } from './contract'

const DIGIT_MAP: Record<string, number> = {
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

const MULTIPLIER_MAP: Record<string, number> = {
  black: 1,
  brown: 10,
  red: 100,
  orange: 1_000,
  yellow: 10_000,
  green: 100_000,
  blue: 1_000_000,
  violet: 10_000_000,
  gray: 100_000_000,
  white: 1_000_000_000,
  gold: 0.1,
  silver: 0.01
}

const TOLERANCE_MAP: Record<string, number> = {
  brown: 1,
  red: 2,
  green: 0.5,
  blue: 0.25,
  violet: 0.1,
  gray: 0.05,
  gold: 5,
  silver: 10
}

const TEMPCO_MAP: Record<string, number> = {
  brown: 100,
  red: 50,
  orange: 15,
  yellow: 25,
  blue: 10,
  violet: 5
}

export function calculateResistorColor(input: ResistorColorInput): ResistorColorOutput {
  const colors = input.colors.map((c) => c.toLowerCase())
  const bands = input.bands
  const digits = bands >= 5 ? 3 : 2
  const digitValues = colors.slice(0, digits).map((c) => DIGIT_MAP[c] ?? 0)
  const sig = Number(digitValues.join(''))
  const multiplier = MULTIPLIER_MAP[colors[digits]] ?? 1
  const resistance_ohm = sig * multiplier
  const tolerance_color = colors[digits + 1]
  const tolerance_percent = TOLERANCE_MAP[tolerance_color] ?? 5
  const min_ohm = resistance_ohm * (1 - tolerance_percent / 100)
  const max_ohm = resistance_ohm * (1 + tolerance_percent / 100)
  const tempco_color = colors[digits + 2]
  const tempco_ppm = tempco_color ? TEMPCO_MAP[tempco_color] : undefined

  return {
    resistance_ohm,
    tolerance_percent,
    min_ohm,
    max_ohm,
    tempco_ppm
  }
}
