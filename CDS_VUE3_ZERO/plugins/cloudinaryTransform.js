/**
 * Plugin de Vite para transformar rutas locales de imágenes a Cloudinary
 * ADITIVO: Transforma src="/images/..." → src="https://res.cloudinary.com/..."
 */

import { localPathToBaseDeliveryUrl } from '../src/utils/cloudinaryContract.js'

/**
 * Convierte una ruta local a URL de Cloudinary
 */
function toCloudinaryUrl(localPath, cloudName) {
  if (!localPath || !localPath.startsWith('/images/')) {
    return localPath
  }

  return localPathToBaseDeliveryUrl(localPath, cloudName) || localPath
}

/**
 * Transforma el contenido de archivos Vue/HTML
 */
function transformContent(content, id, cloudName) {
  // Solo procesar archivos Vue, HTML, JSX, TSX, JS, TS
  if (!/\.(vue|html|jsx|tsx|js|ts)$/i.test(id)) {
    return content
  }
  
  // Patrón para encontrar cualquier string literal "/images/..."
  const imgRegex = /(["'])\/images\/([^"']+)\1/g
  
  let changed = false
  const transformed = content.replace(imgRegex, (match, quote, imagePath) => {
    const localPath = `/images/${imagePath}`
    const cloudUrl = toCloudinaryUrl(localPath, cloudName)
    
    if (cloudUrl !== localPath) {
      changed = true
      return `${quote}${cloudUrl}${quote}`
    }
    
    return match
  })
  
  return changed ? transformed : content
}

export default function cloudinaryTransformPlugin({ cloudName }) {
  return {
    name: 'cloudinary-transform',
    enforce: 'pre',
    
    transform(code, id) {
      const transformed = transformContent(code, id, cloudName)
      
      if (transformed !== code) {
        return {
          code: transformed,
          map: null
        }
      }
      
      return null
    }
  }
}
