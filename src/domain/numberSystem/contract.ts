export type NumericBase = 2 | 8 | 10 | 16;

export interface NumberSystemInput {
  value: string;
  from: NumericBase;
  to: NumericBase;
}

export interface NumberSystemOutput {
  value: string;
}
