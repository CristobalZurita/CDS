import { CalculationState } from './calculationState';

export interface CalculationResult<T> {
  state: CalculationState;
  value?: T;
  errors?: string[];
  warnings?: string[];
}
