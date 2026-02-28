import { api } from '@/services/api'

export const resolveApiHost = () => {
  const base = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'
  return base.includes('/api/') ? base.split('/api/')[0] : base
}

export const toAbsoluteMediaUrl = (path) => {
  if (!path) return ''
  if (/^(blob:|data:|https?:)/.test(path)) return path
  const baseUrl = resolveApiHost()
  return `${baseUrl}${path.startsWith('/') ? '' : '/'}${path}`
}

export async function resolveRepairPhotoUrl(photo) {
  const path = photo?.photo_download_url || photo?.photo_url || ''
  if (!path) return ''

  if (photo?.photo_download_url) {
    const response = await api.get(toAbsoluteMediaUrl(path), { responseType: 'blob' })
    return URL.createObjectURL(response.data)
  }

  return toAbsoluteMediaUrl(path)
}

export async function hydrateRepairPhotos(photos = []) {
  return Promise.all(
    photos.map(async (photo) => ({
      ...photo,
      resolved_photo_url: await resolveRepairPhotoUrl(photo),
    }))
  )
}

export function revokeHydratedRepairPhotos(photos = []) {
  for (const photo of photos) {
    if (photo?.resolved_photo_url?.startsWith('blob:')) {
      URL.revokeObjectURL(photo.resolved_photo_url)
    }
  }
}
