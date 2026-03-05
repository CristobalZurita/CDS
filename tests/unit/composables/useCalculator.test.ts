import { describe, expect, it, vi } from 'vitest'

import { useCalculator } from '@/composables/useCalculator'
import { CalculationState } from '@/domain/common/calculationState'
import { createValidationResult, invalidate } from '@/validation'

describe('useCalculator', () => {
  it('returns an OK result when validation passes', () => {
    const { result, calculate } = useCalculator(
      (input: { value: number }) => {
        const validation = createValidationResult()
        validation.warnings.push({ code: 'warning', message: 'warning' })
        return validation
      },
      (input: { value: number }) => input.value * 2
    )

    calculate({ value: 21 })

    expect(result.value).toEqual({
      state: CalculationState.OK,
      value: 42,
      warnings: ['warning'],
    })
  })

  it('returns INVALID and skips the calculator when validation fails', () => {
    const calculator = vi.fn((input: { value: number }) => input.value * 2)
    const { result, calculate } = useCalculator(
      () => {
        const validation = createValidationResult()
        invalidate(validation, { code: 'bad-input', message: 'bad input' })
        return validation
      },
      calculator
    )

    calculate({ value: 21 })

    expect(calculator).not.toHaveBeenCalled()
    expect(result.value).toEqual({
      state: CalculationState.INVALID,
      errors: ['bad input'],
      warnings: [],
    })
  })

  it('captures thrown calculator errors as INVALID state', () => {
    const { result, calculate } = useCalculator(
      () => createValidationResult(),
      () => {
        throw new Error('explode')
      }
    )

    calculate({} as never)

    expect(result.value).toEqual({
      state: CalculationState.INVALID,
      errors: ['explode'],
    })
  })
})
