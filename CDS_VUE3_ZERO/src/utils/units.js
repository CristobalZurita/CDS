/**
 * Utilidades de conversión de unidades eléctricas
 * ADITIVO: Extraído de los composables de calculadoras
 */

// ==========================================
// RESISTENCIA
// ==========================================

export const resistanceUnitFactor = {
  ohm: 1,
  kohm: 1000,
  mohm: 1000000,
}

export const resistanceUnits = [
  { value: 'ohm', label: 'Ω' },
  { value: 'kohm', label: 'kΩ' },
  { value: 'mohm', label: 'MΩ' },
]

export function toOhm(value, unit) {
  const factor = resistanceUnitFactor[unit] || 1
  return Number(value) * factor
}

export function fromOhm(value, unit) {
  const factor = resistanceUnitFactor[unit] || 1
  return value / factor
}

// ==========================================
// CAPACITANCIA
// ==========================================

export const capacitanceUnitFactor = {
  pf: 1e-12,
  nf: 1e-9,
  uf: 1e-6,
  mf: 1e-3,
  f: 1,
}

export const capacitanceUnits = [
  { value: 'pf', label: 'pF' },
  { value: 'nf', label: 'nF' },
  { value: 'uf', label: 'µF' },
  { value: 'mf', label: 'mF' },
  { value: 'f', label: 'F' },
]

export function toFarad(value, unit) {
  const factor = capacitanceUnitFactor[unit] || 1
  return Number(value) * factor
}

export function fromFarad(value, unit) {
  const factor = capacitanceUnitFactor[unit] || 1
  return value / factor
}

// ==========================================
// FRECUENCIA
// ==========================================

export const frequencyUnitFactor = {
  hz: 1,
  khz: 1000,
  mhz: 1000000,
  ghz: 1000000000,
}

export const frequencyUnits = [
  { value: 'hz', label: 'Hz' },
  { value: 'khz', label: 'kHz' },
  { value: 'mhz', label: 'MHz' },
  { value: 'ghz', label: 'GHz' },
]

export function toHz(value, unit) {
  const factor = frequencyUnitFactor[unit] || 1
  return Number(value) * factor
}

export function fromHz(value, unit) {
  const factor = frequencyUnitFactor[unit] || 1
  return value / factor
}

// ==========================================
// INDUCTANCIA
// ==========================================

export const inductanceUnitFactor = {
  nh: 1e-9,
  uh: 1e-6,
  mh: 1e-3,
  h: 1,
}

export const inductanceUnits = [
  { value: 'nh', label: 'nH' },
  { value: 'uh', label: 'µH' },
  { value: 'mh', label: 'mH' },
  { value: 'h', label: 'H' },
]

export function toHenry(value, unit) {
  const factor = inductanceUnitFactor[unit] || 1
  return Number(value) * factor
}

export function fromHenry(value, unit) {
  const factor = inductanceUnitFactor[unit] || 1
  return value / factor
}

// ==========================================
// CORRIENTE
// ==========================================

export const currentUnitFactor = {
  ua: 1e-6,
  ma: 1e-3,
  a: 1,
}

export const currentUnits = [
  { value: 'ua', label: 'µA' },
  { value: 'ma', label: 'mA' },
  { value: 'a', label: 'A' },
]

export function toAmp(value, unit) {
  const factor = currentUnitFactor[unit] || 1
  return Number(value) * factor
}

export function fromAmp(value, unit) {
  const factor = currentUnitFactor[unit] || 1
  return value / factor
}

// ==========================================
// VOLTAJE
// ==========================================

export const voltageUnitFactor = {
  uv: 1e-6,
  mv: 1e-3,
  v: 1,
  kv: 1000,
}

export const voltageUnits = [
  { value: 'uv', label: 'µV' },
  { value: 'mv', label: 'mV' },
  { value: 'v', label: 'V' },
  { value: 'kv', label: 'kV' },
]

export function toVolt(value, unit) {
  const factor = voltageUnitFactor[unit] || 1
  return Number(value) * factor
}

export function fromVolt(value, unit) {
  const factor = voltageUnitFactor[unit] || 1
  return value / factor
}

// ==========================================
// LONGITUD
// ==========================================

export const lengthUnitFactor = {
  mm: 0.001,
  cm: 0.01,
  m: 1,
  km: 1000,
  inch: 0.0254,
  ft: 0.3048,
}

export const lengthUnits = [
  { value: 'mm', label: 'mm' },
  { value: 'cm', label: 'cm' },
  { value: 'm', label: 'm' },
  { value: 'km', label: 'km' },
  { value: 'inch', label: 'in' },
  { value: 'ft', label: 'ft' },
]

export function toMeter(value, unit) {
  const factor = lengthUnitFactor[unit] || 1
  return Number(value) * factor
}

export function fromMeter(value, unit) {
  const factor = lengthUnitFactor[unit] || 1
  return value / factor
}

// ==========================================
// TEMPERATURA
// ==========================================

export function celsiusToFahrenheit(c) {
  return (c * 9 / 5) + 32
}

export function celsiusToKelvin(c) {
  return c + 273.15
}

export function fahrenheitToCelsius(f) {
  return (f - 32) * 5 / 9
}

export function kelvinToCelsius(k) {
  return k - 273.15
}
