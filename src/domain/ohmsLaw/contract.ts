export interface OhmsLawInput {
  voltage_v?: number;
  current_a?: number;
  resistance_ohm?: number;
}

export interface OhmsLawOutput {
  voltage_v: number;
  current_a: number;
  resistance_ohm: number;
  power_w: number;
}
