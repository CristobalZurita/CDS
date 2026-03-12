/**
 * Utilidades de formateo centralizadas
 * ADITIVO: Extraído de los composables existentes para reutilización
 */

/**
 * Normaliza un número decimal a precisión fija
 * Extraído de: useAwgCalculator.js, useOhmsLawCalculator.js, etc.
 */
export function normalizeDecimal(value, decimals = 6) {
  if (!Number.isFinite(value)) return null
  return Number(value.toFixed(decimals))
}

/**
 * Formatea una fecha para display
 * Extraído de: useAdminDashboardPage.js, useContactMessagesPage.js, etc.
 */
export function formatDate(value) {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '—'
  return new Intl.DateTimeFormat('es-CL', {
    dateStyle: 'medium',
    timeStyle: 'short'
  }).format(date)
}

/**
 * Formatea una fecha solo (sin hora)
 * Extraído de: useSchedulePage.js
 */
export function formatDateOnly(value) {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '—'
  return new Intl.DateTimeFormat('es-CL', {
    dateStyle: 'medium'
  }).format(date)
}

/**
 * Formatea moneda en CLP
 * Extraído de: useQuotesAdminPage.js, useStorePage.js, etc.
 */
export function formatCurrency(value) {
  const num = typeof value === 'string' ? parseFloat(value) : value
  if (!Number.isFinite(num)) return '$—'
  return new Intl.NumberFormat('es-CL', {
    style: 'currency',
    currency: 'CLP',
    maximumFractionDigits: 0
  }).format(num)
}

/**
 * Formatea número con separadores de miles
 * Extraído de: useStatsPage.js
 */
export function formatNumber(value) {
  if (!Number.isFinite(value)) return '—'
  return new Intl.NumberFormat('es-CL').format(value)
}

/**
 * Formatea bytes a unidades legibles
 * Extraído de patrones comunes en el codebase
 */
export function formatBytes(bytes) {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}
