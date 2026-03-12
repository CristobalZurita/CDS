/**
 * Utilidad para construir URLs de Cloudinary
 * ADITIVO: Convierte rutas locales a URLs de Cloudinary
 */

const CLOUDINARY_CLOUD_NAME = 'dgwwi77ic'
const CLOUDINARY_FOLDER_BASE = 'cirujano'
const CLOUDINARY_BASE_URL = `https://res.cloudinary.com/${CLOUDINARY_CLOUD_NAME}/image/upload/${CLOUDINARY_FOLDER_BASE}`

/**
 * Convierte una ruta local a URL de Cloudinary
 * @param {string} localPath - Ruta local (ej: '/images/instrumentos/ms20.jpg')
 * @param {Object} options - Opciones de transformación
 * @returns {string} URL completa de Cloudinary
 */
export function toCloudinaryUrl(localPath, options = {}) {
  if (!localPath) return ''
  
  // Si ya es URL completa, devolverla
  if (localPath.startsWith('http')) return localPath
  
  // Limpiar ruta (quitar leading slash)
  const cleanPath = localPath.startsWith('/') ? localPath.slice(1) : localPath
  
  // Construir URL base
  let url = `${CLOUDINARY_BASE_URL}/${cleanPath}`
  
  // Aplicar transformaciones si se solicitan
  if (options.width || options.height || options.quality) {
    const transforms = []
    if (options.width) transforms.push(`w_${options.width}`)
    if (options.height) transforms.push(`h_${options.height}`)
    if (options.crop) transforms.push(`c_${options.crop}`)
    if (options.quality) transforms.push(`q_${options.quality}`)
    
    const transformStr = transforms.join(',')
    url = `${CLOUDINARY_BASE_URL}/${transformStr}/${cleanPath}`
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
