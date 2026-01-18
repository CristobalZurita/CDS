import { AwgInput, AwgOutput } from './contract'

export function calculateAwg(input: AwgInput): AwgOutput {
  const awg = input.awg
  const diameter_mm = 0.127 * Math.pow(92, (36 - awg) / 39)
  const area_mm2 = Math.PI * Math.pow(diameter_mm / 2, 2)
  const resistance_ohm_per_km = (0.017241 / area_mm2) * 1000
  return { diameter_mm, area_mm2, resistance_ohm_per_km }
}
