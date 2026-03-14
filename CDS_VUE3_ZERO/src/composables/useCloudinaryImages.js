/**
 * Composable para resolver imágenes desde Cloudinary vía API.
 * ADITIVO: No modifica rutas, consulta al backend.
 *
 * @deprecated Sin consumidores activos. Definido pero no importado fuera de este archivo.
 * Alternativa activa: useSiteImages.js (resolución sincrónica vía toCloudinaryUrl).
 * Mantener hasta confirmar que el endpoint /images/resolve no se retomará.
 */

import { ref, onMounted } from 'vue'
import api from '@/services/api'

// Cache local de mapeos ruta → URL
const imageCache = new Map()

/**
 * Resuelve una ruta local a URL de Cloudinary
 * @param {string} localPath - Ruta local (ej: '/images/INVENTARIO/foto.webp')
 * @returns {Promise<string>} URL de Cloudinary
 */
export async function resolveImage(localPath) {
  if (!localPath) return ''
  
  // Si ya es URL completa, devolverla
  if (localPath.startsWith('http')) return localPath
  
  // Revisar cache
  if (imageCache.has(localPath)) {
    return imageCache.get(localPath)
  }
  
  try {
    const { data } = await api.get('/images/resolve', {
      params: { path: localPath }
    })
    
    const url = data?.cloudinary_url || localPath
    imageCache.set(localPath, url)
    return url
    
  } catch (e) {
    console.warn('Error resolving image:', localPath, e)
    return localPath
  }
}

/**
 * Resuelve múltiples imágenes a la vez
 * @param {string[]} paths - Array de rutas locales
 * @returns {Promise<Object>} Mapa de rutas a URLs
 */
export async function resolveImagesBatch(paths) {
  if (!paths?.length) return {}
  
  // Filtrar solo las que no están en cache
  const toResolve = paths.filter(p => !imageCache.has(p) && !p.startsWith('http'))
  
  if (toResolve.length === 0) {
    // Todas en cache
    return Object.fromEntries(paths.map(p => [p, imageCache.get(p) || p]))
  }
  
  try {
    const { data } = await api.post('/images/resolve-batch', toResolve)
    
    // Guardar en cache
    Object.entries(data?.mappings || {}).forEach(([path, url]) => {
      imageCache.set(path, url)
    })
    
    // Retornar todas (cacheadas + nuevas)
    return Object.fromEntries(paths.map(p => [p, imageCache.get(p) || p]))
    
  } catch (e) {
    console.warn('Error resolving batch:', e)
    return Object.fromEntries(paths.map(p => [p, p]))
  }
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
