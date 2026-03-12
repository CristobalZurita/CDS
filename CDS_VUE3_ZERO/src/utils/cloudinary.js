/**
 * Utilidad para construir URLs de Cloudinary
 * ADITIVO: Convierte rutas locales a URLs de Cloudinary usando el mapeo
 */

import imageMapping from '../../../image-mapping.json'

const CLOUDINARY_CLOUD_NAME = 'dgwwi77ic'
const CLOUDINARY_FOLDER_BASE = 'cirujano'
const CLOUDINARY_BASE_URL = `https://res.cloudinary.com/${CLOUDINARY_CLOUD_NAME}/image/upload/${CLOUDINARY_FOLDER_BASE}`

// Crear índice del mapeo para búsqueda rápida
const imageMap = new Map()
if (Array.isArray(imageMapping)) {
  for (const item of imageMapping) {
    if (item.local) {
      imageMap.set(item.local, item.cloudinary || item.altUrl)
    }
  }
}

/**
 * Convierte una ruta local a URL de Cloudinary
 * Usa el image-mapping.json para obtener la URL correcta con versión
 * @param {string} localPath - Ruta local (ej: '/images/instrumentos/ms20.jpg')
 * @param {Object} options - Opciones de transformación
 * @returns {string} URL completa de Cloudinary
 */
export function toCloudinaryUrl(localPath, options = {}) {
  if (!localPath) return ''
  
  // Si ya es URL completa, devolverla
  if (localPath.startsWith('http')) return localPath
  
  // Buscar en el mapeo primero (para obtener URL con versión correcta)
  let url = imageMap.get(localPath)
  
  // Si no está en el mapeo, construir URL manualmente (fallback)
  if (!url) {
    const cleanPath = localPath.startsWith('/') ? localPath.slice(1) : localPath
    url = `${CLOUDINARY_BASE_URL}/${cleanPath}`
  }
  
  // Aplicar transformaciones si se solicitan
  if (options.width || options.height || options.quality) {
    const transforms = []
    if (options.width) transforms.push(`w_${options.width}`)
    if (options.height) transforms.push(`h_${options.height}`)
    if (options.crop) transforms.push(`c_${options.crop}`)
    if (options.quality) transforms.push(`q_${options.quality}`)
    
    const transformStr = transforms.join(',')
    
    // Insertar transformaciones después de /upload/ y antes de la versión/path
    if (url.includes('/upload/v')) {
      // URL con versión: .../upload/v1234567890/path
      url = url.replace('/upload/v', `/upload/${transformStr}/v`)
    } else if (url.includes('/image/upload/')) {
      // URL sin versión: .../image/upload/path
      url = url.replace('/image/upload/', `/image/upload/${transformStr}/`)
    }
  }
  
  return url
}

/**
 * Genera URL de thumbnail
 */
export function toThumbnail(localPath, width = 200) {
  return toCloudinaryUrl(localPath, { width, crop: 'limit', quality: 'auto' })
}

/**
 * Genera URL de imagen completa optimizada
 */
export function toOptimized(localPath, width = 800) {
  return toCloudinaryUrl(localPath, { width, crop: 'limit', quality: 'auto' })
}

/**
 * Obtiene la URL de Cloudinary directamente del mapeo
 * @param {string} localPath - Ruta local
 * @returns {string|null} URL de Cloudinary o null si no existe
 */
export function getCloudinaryUrlFromMapping(localPath) {
  if (!localPath) return null
  if (localPath.startsWith('http')) return localPath
  return imageMap.get(localPath) || null
}
