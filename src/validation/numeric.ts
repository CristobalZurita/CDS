import { ValidationError } from './rules';

export function isFiniteNumber(value: unknown, field: string): ValidationError | null {
  if (typeof value !== 'number' || !Number.isFinite(value)) {
    return { code: 'NOT_FINITE', message: `${field} is not a finite number` };
  }
  return null;
}

export function greaterThan(value: number, min: number, field: string): ValidationError | null {
  if (value <= min) {
    return { code: 'OUT_OF_RANGE', message: `${field} must be > ${min}` };
  }
  return null;
}
