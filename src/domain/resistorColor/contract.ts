export interface ResistorColorInput {
  bands: number;
  colors: string[];
  temperature_c?: number;
}

export interface ResistorColorOutput {
  resistance_ohm: number;
  tolerance_percent: number;
  min_ohm: number;
  max_ohm: number;
  tempco_ppm?: number;
}
