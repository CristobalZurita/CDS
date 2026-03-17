/**
 * Composable Cloudinary ZERO
 * Resuelve rutas locales /images/* a URLs Cloudinary via SDK.
 * Sin JSON, sin mapeo estático.
 */

import { toCloudinaryUrl } from '@/utils/cloudinary'

export function useCloudinaryImage(localPath: string): string {
  if (!localPath) return ''
  if (localPath.startsWith('http')) return localPath
  return toCloudinaryUrl(localPath)
}

export default useCloudinaryImage
