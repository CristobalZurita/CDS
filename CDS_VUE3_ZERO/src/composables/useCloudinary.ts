/**
 * Composable Cloudinary ZERO
 * Resuelve rutas locales /images/* a URLs Cloudinary.
 */

import mapping from '../../../image-mapping.json'

const CLOUDINARY_BASE_URL = 'https://res.cloudinary.com/dgwwi77ic/image/upload'

// Índice local -> cloudinary
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
  
  // Mapeo exacto
  const url = URLS[localPath]
  if (url) return url
  
  // Fallback robusto por nombre de archivo
  const fileName = String(localPath).split('/').pop()
  if (!fileName) return localPath
  return `${CLOUDINARY_BASE_URL}/${encodeURIComponent(fileName)}`
}

export default useCloudinaryImage
