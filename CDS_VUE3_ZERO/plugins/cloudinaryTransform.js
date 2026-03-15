/**
 * Plugin de Vite para transformar rutas locales de imágenes a Cloudinary
 * ADITIVO: Transforma src="/images/..." → src="https://res.cloudinary.com/..."
 */

import { readFileSync } from 'fs'
import { resolve, dirname } from 'path'
import { fileURLToPath } from 'url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const CLOUDINARY_BASE_URL = 'https://res.cloudinary.com/dgwwi77ic/image/upload'

// Cargar el mapeo de imágenes desde el archivo JSON
const imageMap = new Map()
try {
  const mappingPath = resolve(__dirname, '../image-mapping.json')
  const imageMapping = JSON.parse(readFileSync(mappingPath, 'utf-8'))
  if (Array.isArray(imageMapping)) {
    for (const item of imageMapping) {
      if (item.local) {
        imageMap.set(item.local, item.cloudinary || item.altUrl)
      }
    }
    console.log(`[cloudinary-transform] Cargadas ${imageMap.size} imágenes del mapeo`)
  }
} catch (e) {
  console.error('[cloudinary-transform] Error cargando image-mapping.json:', e.message)
}

/**
 * Convierte una ruta local a URL de Cloudinary
 */
function toCloudinaryUrl(localPath) {
  if (!localPath || !localPath.startsWith('/images/')) {
    return localPath
  }
  
  // Buscar en el mapeo
  const cloudUrl = imageMap.get(localPath)
  if (cloudUrl) {
    return cloudUrl
  }
  
  // Fallback robusto: usa el nombre de archivo como public_id
  const fileName = String(localPath).split('/').pop()
  if (!fileName) return localPath
  return `${CLOUDINARY_BASE_URL}/${encodeURIComponent(fileName)}`
}

/**
 * Transforma el contenido de archivos Vue/HTML
 */
function transformContent(content, id) {
  // Solo procesar archivos Vue, HTML, JSX, TSX, JS, TS
  if (!/\.(vue|html|jsx|tsx|js|ts)$/i.test(id)) {
    return content
  }
  
  // Patrón para encontrar cualquier string literal "/images/..."
  const imgRegex = /(["'])\/images\/([^"']+)\1/g
  
  let changed = false
  const transformed = content.replace(imgRegex, (match, quote, imagePath) => {
    const localPath = `/images/${imagePath}`
    const cloudUrl = toCloudinaryUrl(localPath)
    
    if (cloudUrl !== localPath) {
      changed = true
      return `${quote}${cloudUrl}${quote}`
    }
    
    return match
  })
  
  return changed ? transformed : content
}

export default function cloudinaryTransformPlugin() {
  return {
    name: 'cloudinary-transform',
    enforce: 'pre',
    
    transform(code, id) {
      const transformed = transformContent(code, id)
      
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
