import { TemperatureInput, TemperatureOutput } from './contract';

export function convertTemperature(input: TemperatureInput): TemperatureOutput {
  let c: number;

  switch (input.from) {
    case 'C': c = input.value; break;
    case 'F': c = (input.value - 32) * 5/9; break;
    case 'K': c = input.value - 273.15; break;
    case 'R': c = (input.value - 491.67) * 5/9; break;
  }

  let out: number;
  switch (input.to) {
    case 'C': out = c!; break;
    case 'F': out = c! * 9/5 + 32; break;
    case 'K': out = c! + 273.15; break;
    case 'R': out = (c! + 273.15) * 9/5; break;
  }

  return { value: out! };
}
