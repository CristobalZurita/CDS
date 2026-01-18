import { LengthInput, LengthOutput } from './contract'

const UNITS: Record<string, number> = {
  mm: 0.001,
  cm: 0.01,
  m: 1,
  km: 1000,
  in: 0.0254,
  ft: 0.3048
}

export function convertLength(input: LengthInput): LengthOutput {
  const from = UNITS[input.from_unit]
  const to = UNITS[input.to_unit]
  if (!from || !to) {
    return { value: input.value }
  }
  const meters = input.value * from
  return { value: meters / to }
}
