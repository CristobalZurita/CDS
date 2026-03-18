/**
 * Composable legacy de compatibilidad para resolver imágenes Cloudinary.
 * Ya no consulta el backend ni usa image-mapping.json.
 * Mantiene firma async sólo para no romper imports antiguos.
 *
 * @deprecated Sin consumidores activos. La resolución canónica vive en
 * useCloudinary.ts + cloudinary.js.
 */

import { ref } from 'vue'
import { toCloudinaryUrl } from '@/utils/cloudinary'

// Cache local de mapeos ruta → URL
const imageCache = new Map()

/**
 * Resuelve una ruta local a URL de Cloudinary
 * @param {string} localPath - Ruta local (ej: '/images/INVENTARIO/foto.webp')
 * @returns {Promise<string>} URL de Cloudinary
 */
export async function resolveImage(localPath) {
  if (!localPath) return ''

  if (localPath.startsWith('http')) return localPath
  if (imageCache.has(localPath)) {
    return imageCache.get(localPath)
  }

  const url = toCloudinaryUrl(localPath) || localPath
  imageCache.set(localPath, url)
  return url
}

/**
 * Resuelve múltiples imágenes a la vez
 * @param {string[]} paths - Array de rutas locales
 * @returns {Promise<Object>} Mapa de rutas a URLs
 */
export async function resolveImagesBatch(paths) {
  if (!paths?.length) return {}

  const mappings = {}
  for (const path of paths) {
    if (path?.startsWith?.('http')) {
      mappings[path] = path
      continue
    }

    const cached = imageCache.get(path)
    if (cached) {
      mappings[path] = cached
      continue
    }

    const url = toCloudinaryUrl(path) || path
    imageCache.set(path, url)
    mappings[path] = url
  }

  return mappings
}

/**
 * Composable para usar en componentes
 */
export function useCloudinaryImages() {
  const loading = ref(false)
  const error = ref(null)
  
  const resolve = async (path) => {
    loading.value = true
    error.value = null
    
    try {
      const url = await resolveImage(path)
      return url
    } catch (e) {
      error.value = e.message
      return path
    } finally {
      loading.value = false
    }
  }
  
  const resolveBatch = async (paths) => {
    loading.value = true
    error.value = null
    
    try {
      const mappings = await resolveImagesBatch(paths)
      return mappings
    } catch (e) {
      error.value = e.message
      return Object.fromEntries(paths.map(p => [p, p]))
    } finally {
      loading.value = false
    }
  }
  
  return {
    loading,
    error,
    resolve,
    resolveBatch
  }
}
