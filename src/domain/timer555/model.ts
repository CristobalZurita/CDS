import { Timer555Input, Timer555Output } from './contract';

export function calculateTimer555(input: Timer555Input): Timer555Output {
  const { mode, R1_ohm, R2_ohm, R_ohm, C_farad } = input;

  if (mode === 'monostable' && R_ohm) {
    const period = 1.0986 * R_ohm * C_farad;
    return { period_s: period };
  }

  if (mode === 'astable_standard' && R1_ohm && R2_ohm) {
    const tHigh = 0.693 * (R1_ohm + R2_ohm) * C_farad;
    const tLow = 0.693 * R2_ohm * C_farad;
    const period = tHigh + tLow;
    return {
      t_high_s: tHigh,
      t_low_s: tLow,
      period_s: period,
      frequency_hz: 1 / period,
      duty_cycle: tHigh / period
    };
  }

  return {};
}
