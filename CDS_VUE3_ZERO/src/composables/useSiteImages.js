/**
 * Composable para imágenes del sitio
 * Convierte rutas locales a URLs de Cloudinary automáticamente
 */

import { toCloudinaryUrl } from '@/utils/cloudinary'

/**
 * Resuelve una ruta de imagen a URL completa
 * @param {string} localPath - Ruta local ej: '/images/logo/logo.webp'
 * @returns {string} URL de Cloudinary o ruta local si falla
 */
export function resolveImageUrl(localPath) {
  if (!localPath) return ''
  if (localPath.startsWith('http')) return localPath
  return toCloudinaryUrl(localPath)
}

/**
 * Array de imágenes con URLs resueltas
 * @param {Array} items - Array de objetos con propiedad 'image'
 * @returns {Array} Mismo array con URLs resueltas
 */
export function resolveImageArray(items) {
  if (!Array.isArray(items)) return []
  return items.map(item => ({
    ...item,
    image: resolveImageUrl(item.image)
  }))
}

/**
 * Hook para usar en componentes
 */
export function useSiteImages() {
  return {
    resolveImageUrl,
    resolveImageArray
  }
}
