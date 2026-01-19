import { SmdCapacitorInput, SmdCapacitorOutput } from './contract'

export function decodeSmdCapacitor(input: SmdCapacitorInput): SmdCapacitorOutput {
  const code = input.code.trim().toUpperCase()
  let value_pf = NaN

  if ((input.type === 'EIA3' || input.type === 'EIA198') && code.length === 3) {
    const sig = Number(code.slice(0, 2))
    const mult = Math.pow(10, Number(code[2]))
    value_pf = sig * mult
  } else if (input.type === 'EIA4' && code.length === 4) {
    const sig = Number(code.slice(0, 3))
    const mult = Math.pow(10, Number(code[3]))
    value_pf = sig * mult
  }

  const value_nf = Number.isFinite(value_pf) ? value_pf / 1_000 : NaN
  const value_uf = Number.isFinite(value_pf) ? value_pf / 1_000_000 : NaN

  return {
    value_pf,
    value_nf,
    value_uf
  }
}

// Alias para compatibilidad con el componente
export const calculateSmdCapacitor = decodeSmdCapacitor
