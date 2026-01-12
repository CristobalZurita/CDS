import { CalculationResult } from '@/domain/common/types';
import { CalculationState } from '@/domain/common/calculationState';
import { ValidationResult } from '@/validation/rules';

export function applyValidation<T>(
  validation: ValidationResult,
  compute: () => T
): CalculationResult<T> {
  if (!validation.valid) {
    return {
      state: CalculationState.INVALID,
      errors: validation.errors.map(e => e.message),
      warnings: validation.warnings.map(w => w.message)
    };
  }

  try {
    const value = compute();
    return {
      state: CalculationState.OK,
      value,
      warnings: validation.warnings.map(w => w.message)
    };
  } catch (e: any) {
    return {
      state: CalculationState.INVALID,
      errors: [e.message ?? 'Unknown error']
    };
  }
}
