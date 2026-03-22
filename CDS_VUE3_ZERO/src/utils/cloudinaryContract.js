/**
 * Contrato canónico Cloudinary para ZERO.
 *
 * Regla principal:
 *   /images/carpeta/nombre.ext -> public_id = carpeta/nombre
 *
 * La misma convención debe usarse en front, plugin de build y backend.
 */

const LOCAL_IMAGE_PREFIX = '/images/'

export function normalizeLocalImagePath(localPath) {
  if (!localPath) return ''
  if (localPath.startsWith('http')) return localPath
  if (localPath.startsWith('/')) return localPath
  return `/${localPath}`
}

export function localPathToPublicId(localPath) {
  const normalized = normalizeLocalImagePath(localPath)
  if (!normalized || normalized.startsWith('http')) return normalized

  const withoutPrefix = normalized.startsWith(LOCAL_IMAGE_PREFIX)
    ? normalized.slice(LOCAL_IMAGE_PREFIX.length)
    : normalized.replace(/^\/+/, '')

  return withoutPrefix.replace(/(\.[^.]+)+$/, '')
}

export function encodePublicId(publicId) {
  return String(publicId)
    .split('/')
    .map(segment => encodeURIComponent(segment))
    .join('/')
}

export function publicIdToBaseDeliveryUrl(publicId, cloudName) {
  if (!publicId || !cloudName) return ''
  return `https://res.cloudinary.com/${cloudName}/image/upload/${encodePublicId(publicId)}`
}

export function localPathToBaseDeliveryUrl(localPath, cloudName) {
  const publicId = localPathToPublicId(localPath)
  if (!publicId || publicId.startsWith('http')) return publicId
  return publicIdToBaseDeliveryUrl(publicId, cloudName)
}

