import { SmdResistorInput, SmdResistorOutput } from './contract'

const E96_VALUES = [
  100, 102, 105, 107, 110, 113, 115, 118, 121, 124, 127, 130,
  133, 137, 140, 143, 147, 150, 154, 158, 162, 165, 169, 174,
  178, 182, 187, 191, 196, 200, 205, 210, 215, 221, 226, 232,
  237, 243, 249, 255, 261, 267, 274, 280, 287, 294, 301, 309,
  316, 324, 332, 340, 348, 357, 365, 374, 383, 392, 402, 412,
  422, 432, 442, 453, 464, 475, 487, 499, 511, 523, 536, 549,
  562, 576, 590, 604, 619, 634, 649, 665, 681, 698, 715, 732,
  750, 768, 787, 806, 825, 845, 866, 887, 909, 931, 953, 976
]

const E96_MULT = {
  Z: 0.001,
  Y: 0.01,
  R: 0.1,
  X: 1,
  S: 10,
  B: 100,
  H: 1000,
  C: 10000
}

export function decodeSmdResistor(input: SmdResistorInput): SmdResistorOutput {
  const code = input.code.trim().toUpperCase()
  if (input.type === 'EIA3' && code.length === 3) {
    const sig = Number(code.slice(0, 2))
    const mult = Math.pow(10, Number(code[2]))
    return { resistance_ohm: sig * mult }
  }
  if (input.type === 'EIA4' && code.length === 4) {
    const sig = Number(code.slice(0, 3))
    const mult = Math.pow(10, Number(code[3]))
    return { resistance_ohm: sig * mult }
  }
  if (input.type === 'EIA96' && code.length >= 3) {
    const idx = Number(code.slice(0, 2)) - 1
    const base = E96_VALUES[idx] ?? 100
    const mult = E96_MULT[code[2]] ?? 1
    return { resistance_ohm: base * mult }
  }
  return { resistance_ohm: NaN }
}

// Alias para compatibilidad con el componente
export const calculateSmdResistor = decodeSmdResistor
