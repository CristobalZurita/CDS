import { ValidationError } from './rules';

export function validateVoltage(v: number): ValidationError | null {
  if (v < 0) {
    return { code: 'PHYSICALLY_IMPOSSIBLE', message: 'Voltage cannot be negative' };
  }
  return null;
}

export function validateCapacitance(c: number): ValidationError | null {
  if (c <= 0) {
    return { code: 'PHYSICALLY_IMPOSSIBLE', message: 'Capacitance must be > 0' };
  }
  return null;
}

export function validateResistance(r: number): ValidationError | null {
  if (r <= 0) {
    return { code: 'PHYSICALLY_IMPOSSIBLE', message: 'Resistance must be > 0' };
  }
  return null;
}
