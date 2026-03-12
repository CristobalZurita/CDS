/**
 * Composable Cloudinary - Versión debug
 */

import mapping from '../../../image-mapping.json'

// Crear mapa
const URLS: Record<string, string> = {}
if (Array.isArray(mapping)) {
  for (const item of mapping) {
    if (item.local && item.cloudinary) {
      URLS[item.local] = item.cloudinary
    }
  }
}

export function useCloudinaryImage(localPath: string): string {
  if (!localPath) return ''
  if (localPath.startsWith('http')) return localPath
  
  // Buscar directamente
  const url = URLS[localPath]
  if (url) return url
  
  // Log para debug
  console.warn('[Cloudinary] No encontrado:', localPath)
  return localPath
}

export default useCloudinaryImage
