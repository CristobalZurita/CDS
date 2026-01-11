export type SmdResistorCodeType = 'EIA3' | 'EIA4' | 'EIA96';

export interface SmdResistorInput {
  code: string;
  type: SmdResistorCodeType;
}

export interface SmdResistorOutput {
  resistance_ohm: number;
}
