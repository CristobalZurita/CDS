export type SmdCapacitorCodeType = 'EIA3' | 'EIA4' | 'EIA198';

export interface SmdCapacitorInput {
  code: string;
  type: SmdCapacitorCodeType;
}

export interface SmdCapacitorOutput {
  value_pf: number;
  value_nf: number;
  value_uf: number;
  tolerance?: string;
}
