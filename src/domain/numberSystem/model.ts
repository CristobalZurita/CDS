import { NumberSystemInput, NumberSystemOutput } from './contract'

export function convertNumberSystem(input: NumberSystemInput): NumberSystemOutput {
  const parsed = parseInt(input.value, input.from)
  if (Number.isNaN(parsed)) {
    return { value: '' }
  }
  return { value: parsed.toString(input.to).toUpperCase() }
}
