export type TemperatureScale = 'C' | 'F' | 'K' | 'R';

export interface TemperatureInput {
  value: number;
  from: TemperatureScale;
  to: TemperatureScale;
}

export interface TemperatureOutput {
  value: number;
}
