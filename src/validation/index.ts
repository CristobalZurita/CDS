import { ValidationResult } from './rules';

export function createValidationResult(): ValidationResult {
  return { valid: true, errors: [], warnings: [] };
}

export function invalidate(result: ValidationResult, error: any) {
  result.valid = false;
  result.errors.push(error);
}
