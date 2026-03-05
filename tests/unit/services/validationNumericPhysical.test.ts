import { describe, expect, it } from 'vitest'
import { greaterThan, isFiniteNumber } from '@/validation/numeric'
import { validateCapacitance, validateResistance, validateVoltage } from '@/validation/physical'

describe('numeric and physical validation helpers', () => {
  it('validates finite numeric values', () => {
    expect(isFiniteNumber(10, 'R')).toBeNull()
    expect(isFiniteNumber('10', 'R')).toEqual({
      code: 'NOT_FINITE',
      message: 'R is not a finite number',
    })
    expect(isFiniteNumber(Number.NaN, 'C')).toEqual({
      code: 'NOT_FINITE',
      message: 'C is not a finite number',
    })
  })

  it('validates greater-than constraints', () => {
    expect(greaterThan(5, 0, 'R')).toBeNull()
    expect(greaterThan(0, 0, 'R')).toEqual({
      code: 'OUT_OF_RANGE',
      message: 'R must be > 0',
    })
  })

  it('validates physical constraints', () => {
    expect(validateVoltage(0)).toBeNull()
    expect(validateVoltage(-1)).toEqual({
      code: 'PHYSICALLY_IMPOSSIBLE',
      message: 'Voltage cannot be negative',
    })

    expect(validateCapacitance(0.000001)).toBeNull()
    expect(validateCapacitance(0)).toEqual({
      code: 'PHYSICALLY_IMPOSSIBLE',
      message: 'Capacitance must be > 0',
    })

    expect(validateResistance(1000)).toBeNull()
    expect(validateResistance(-5)).toEqual({
      code: 'PHYSICALLY_IMPOSSIBLE',
      message: 'Resistance must be > 0',
    })
  })
})
