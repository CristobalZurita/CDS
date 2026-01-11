import { ref } from 'vue';
import { CalculationResult } from '@/domain/common/types';
import { ValidationResult } from '@/validation/rules';
import { applyValidation } from './useValidation';

export function useCalculator<I, O>(
  validator: (input: I) => ValidationResult,
  calculator: (input: I) => O
) {
  const result = ref<CalculationResult<O> | null>(null);

  function calculate(input: I) {
    const validation = validator(input);
    result.value = applyValidation(validation, () => calculator(input));
  }

  return {
    result,
    calculate
  };
}
