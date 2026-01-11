export type Timer555Mode =
  | 'monostable'
  | 'astable_standard'
  | 'astable_diode'
  | 'astable_50';

export interface Timer555Input {
  mode: Timer555Mode;
  R1_ohm?: number;
  R2_ohm?: number;
  R_ohm?: number;
  C_farad: number;
  Vcc_volt: number;
}

export interface Timer555Output {
  frequency_hz?: number;
  period_s?: number;
  duty_cycle?: number;
  t_high_s?: number;
  t_low_s?: number;
}
