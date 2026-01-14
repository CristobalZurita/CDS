import { OhmsLawInput, OhmsLawOutput } from './contract';

export function calculateOhmsLaw(input: OhmsLawInput): OhmsLawOutput {
  let { voltage_v, current_a, resistance_ohm } = input;

  if (voltage_v !== undefined && current_a !== undefined) {
    resistance_ohm = voltage_v / current_a;
  } else if (voltage_v !== undefined && resistance_ohm !== undefined) {
    current_a = voltage_v / resistance_ohm;
  } else if (current_a !== undefined && resistance_ohm !== undefined) {
    voltage_v = current_a * resistance_ohm;
  }

  const power_w = (voltage_v ?? 0) * (current_a ?? 0);

  return {
    voltage_v: voltage_v!,
    current_a: current_a!,
    resistance_ohm: resistance_ohm!,
    power_w
  };
}
