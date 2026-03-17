/**
 * Utilidad para construir URLs de Cloudinary.
 * Deriva el public_id directamente desde la ruta local — sin JSON, sin mapeo estático.
 */

import { Cloudinary } from '@cloudinary/url-gen'
import { scale, thumbnail as cldThumbnail } from '@cloudinary/url-gen/actions/resize'
import { quality } from '@cloudinary/url-gen/actions/delivery'
import { auto as autoQuality } from '@cloudinary/url-gen/qualifiers/quality'
import { localPathToPublicId } from '@/utils/cloudinaryContract'

const CLOUDINARY_CLOUD_NAME = import.meta.env.VITE_CLOUDINARY_CLOUD_NAME || 'dgwwi77ic'

const _cld = new Cloudinary({ cloud: { cloudName: CLOUDINARY_CLOUD_NAME } })

/**
 * Construye una URL de Cloudinary desde un public_id usando el SDK.
 * Usar en código nuevo — el public_id es el identificador canónico en Cloudinary.
 *
 * @param {string} publicId  Ej: 'personales/marimba' o 'instrumentos/KORG_WAVESTATE'
 * @param {Object} options   { width, height, crop }
 * @returns {string}
 */
export function buildUrl(publicId, options = {}) {
  if (!publicId) return ''
  const img = _cld.image(publicId)
  if (options.width || options.height) {
    const action = options.crop === 'thumb'
      ? cldThumbnail().width(options.width || 200).height(options.height || 200)
      : scale().width(options.width).height(options.height)
    img.resize(action)
  }
  img.delivery(quality(autoQuality()))
  return img.toURL()
}

/**
 * Convierte una ruta local a URL de Cloudinary.
 * Acepta /images/... (ruta local) o public_id directo.
 *
 * @param {string} localPath  /images/personales/marimba.webp o personales/marimba
 * @param {Object} options    { width, height, crop }
 * @returns {string}
 */
export function toCloudinaryUrl(localPath, options = {}) {
  if (!localPath) return ''
  if (localPath.startsWith('http')) return localPath
  const publicId = localPathToPublicId(localPath)
  return buildUrl(publicId, options)
}

/**
 * Genera URL de thumbnail.
 */
export function toThumbnail(localPath, width = 200) {
  return toCloudinaryUrl(localPath, { width, crop: 'thumb' })
}

/**
 * Genera URL de imagen completa optimizada.
 */
export function toOptimized(localPath, width = 800) {
  return toCloudinaryUrl(localPath, { width })
}

/**
 * Mantiene la firma anterior para compatibilidad.
 * Ahora deriva el public_id en vez de buscar en un JSON.
 */
export function getCloudinaryUrlFromMapping(localPath) {
  if (!localPath) return null
  if (localPath.startsWith('http')) return localPath
  return toCloudinaryUrl(localPath)
}
