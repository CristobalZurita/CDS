import { describe, expect, it } from 'vitest'

import { calculateAwg } from '@/domain/awg/model'
import { convertLength } from '@/domain/length/model'
import { convertNumberSystem } from '@/domain/numberSystem/model'
import { calculateOhmsLaw } from '@/domain/ohmsLaw/model'
import { calculateResistorColor } from '@/domain/resistorColor/model'
import { decodeSmdCapacitor } from '@/domain/smdCapacitor/model'
import { decodeSmdResistor } from '@/domain/smdResistor/model'
import { convertTemperature } from '@/domain/temperature/model'
import { calculateTimer555 } from '@/domain/timer555/model'

describe('calculator domain models', () => {
  it('calculates AWG derived values from the wire number', () => {
    const result = calculateAwg({ awg: 24 })

    expect(result.diameter_mm).toBeCloseTo(0.5106, 3)
    expect(result.area_mm2).toBeCloseTo(0.2047, 3)
    expect(result.resistance_ohm_per_km).toBeCloseTo(84.2, 0)
  })

  it('converts lengths and leaves the input untouched for unknown units', () => {
    expect(convertLength({ value: 123, from_unit: 'cm', to_unit: 'm' }).value).toBeCloseTo(1.23)
    expect(convertLength({ value: 7, from_unit: 'foo', to_unit: 'm' }).value).toBe(7)
  })

  it('converts number systems and returns an empty string for invalid input', () => {
    expect(convertNumberSystem({ value: 'ff', from: 16, to: 10 }).value).toBe('255')
    expect(convertNumberSystem({ value: 'xyz', from: 10, to: 2 }).value).toBe('')
  })

  it('solves Ohm law from the available operands', () => {
    expect(calculateOhmsLaw({ voltage_v: 12, current_a: 2 })).toEqual({
      voltage_v: 12,
      current_a: 2,
      resistance_ohm: 6,
      power_w: 24,
    })

    expect(calculateOhmsLaw({ voltage_v: 9, resistance_ohm: 3 })).toEqual({
      voltage_v: 9,
      current_a: 3,
      resistance_ohm: 3,
      power_w: 27,
    })
  })

  it('decodes resistor color bands for standard 4-band resistors', () => {
    const result = calculateResistorColor({
      bands: 4,
      colors: ['brown', 'black', 'red', 'gold'],
    })

    expect(result).toEqual({
      resistance_ohm: 1000,
      tolerance_percent: 5,
      min_ohm: 950,
      max_ohm: 1050,
      tempco_ppm: undefined,
    })
  })

  it('decodes SMD capacitor codes for EIA-3 and EIA-4', () => {
    expect(decodeSmdCapacitor({ code: '104', type: 'EIA3' })).toEqual({
      value_pf: 100000,
      value_nf: 100,
      value_uf: 0.1,
    })

    expect(decodeSmdCapacitor({ code: '1002', type: 'EIA4' })).toEqual({
      value_pf: 10000,
      value_nf: 10,
      value_uf: 0.01,
    })
  })

  it('decodes SMD resistor codes and reports invalid codes with NaN', () => {
    expect(decodeSmdResistor({ code: '103', type: 'EIA3' }).resistance_ohm).toBe(10000)
    expect(decodeSmdResistor({ code: '01C', type: 'EIA96' }).resistance_ohm).toBe(1000000)
    expect(Number.isNaN(decodeSmdResistor({ code: 'XX', type: 'EIA4' }).resistance_ohm)).toBe(true)
  })

  it('converts temperatures across supported scales', () => {
    expect(convertTemperature({ value: 100, from: 'C', to: 'F' }).value).toBe(212)
    expect(convertTemperature({ value: 491.67, from: 'R', to: 'K' }).value).toBeCloseTo(273.15, 2)
  })

  it('calculates Timer 555 outputs for monostable and astable modes', () => {
    expect(calculateTimer555({
      mode: 'monostable',
      R_ohm: 1000,
      C_farad: 0.000001,
      Vcc_volt: 5,
    })).toEqual({
      period_s: 0.0010986,
    })

    const astable = calculateTimer555({
      mode: 'astable_standard',
      R1_ohm: 1000,
      R2_ohm: 2000,
      C_farad: 0.000001,
      Vcc_volt: 5,
    })

    expect(astable.t_high_s).toBeCloseTo(0.002079, 6)
    expect(astable.t_low_s).toBeCloseTo(0.001386, 6)
    expect(astable.period_s).toBeCloseTo(0.003465, 6)
    expect(astable.frequency_hz).toBeCloseTo(288.6, 1)
    expect(astable.duty_cycle).toBeCloseTo(0.6, 1)
  })
})
