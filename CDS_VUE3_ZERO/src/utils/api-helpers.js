/**
 * Helpers para construcción de URLs de API
 * ADITIVO: Extraído de useRepairDetailAdminPage.js y otros composables
 */

/**
 * Construye el host base de la API
 * Extraído de: useRepairDetailAdminPage.js, useManualsPage.js, etc.
 */
export function buildApiHost() {
  const rawBase = String(import.meta.env.VITE_API_URL || '/api/v1').trim()

  if (rawBase.startsWith('http://') || rawBase.startsWith('https://')) {
    const baseWithoutApi = rawBase.includes('/api/') ? rawBase.split('/api/')[0] : rawBase
    return baseWithoutApi.replace(/\/+$/, '')
  }

  if (typeof window !== 'undefined' && window.location?.origin) {
    return window.location.origin
  }

  return ''
}

/**
 * Host base cacheado para uso síncrono
 */
export const API_HOST = buildApiHost()

/**
 * Convierte una ruta relativa a URL absoluta
 * Extraído de: useRepairDetailAdminPage.js
 */
export function toAbsoluteUrl(value) {
  const path = String(value || '').trim()
  if (!path) return ''
  if (path.startsWith('http://') || path.startsWith('https://')) return path
  if (path.startsWith('/')) return `${API_HOST}${path}`
  return `${API_HOST}/${path}`
}

/**
 * Resuelve una URL de imagen (igual que toAbsoluteUrl pero semánticamente para imágenes)
 * Extraído de: useManualsPage.js (resolveUrl)
 */
export function resolveUrl(value) {
  return toAbsoluteUrl(value)
}

/**
 * Construye URL completa de endpoint API
 * @param {string} path - Path del endpoint (ej: '/repairs/123')
 * @returns {string} URL completa
 */
export function buildApiUrl(path) {
  const base = String(import.meta.env.VITE_API_URL || '/api/v1').replace(/\/+$/, '')
  const cleanPath = String(path || '').replace(/^\/+/, '')
  return `${base}/${cleanPath}`
}

/**
 * Extrae el nombre de host/base para mostrar
 * @param {string} url - URL completa
 * @returns {string} Host simplificado
 */
export function simplifyHost(url) {
  if (!url) return ''
  try {
    const urlObj = new URL(url)
    return urlObj.hostname.replace(/^www\./, '')
  } catch {
    return url
  }
}

/**
 * Normaliza una entrada de cliente a forma canónica mínima
 * ADITIVO: Extraído de useRepairsAdminPage.js y usePurchaseRequestsPage.js (idéntico en ambos)
 */
export function normalizeClient(entry) {
  return {
    id: Number(entry?.id || 0),
    name: String(entry?.name || ''),
    client_code: String(entry?.client_code || '')
  }
}
