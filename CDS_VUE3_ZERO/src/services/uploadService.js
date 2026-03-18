/**
 * Servicio de upload de imágenes
 * Usa Cloudinary directo si está disponible, fallback a backend
 */

import api from './api.js'
import { localPathToPublicId } from '@/utils/cloudinaryContract'

const DESTINATION_PREFIXES = {
  uploads: 'general',
  instrumentos: 'instrumentos',
  inventario: 'INVENTARIO',
}

function normalizeRelativeUploadPath(relativePath = '') {
  const normalized = String(relativePath || '').replace(/\\/g, '/').replace(/^\/+/, '')
  if (!normalized) return ''
  return normalized.replace(/^images\//i, '')
}

function buildSignatureUrl(destination, fileName, explicitPublicId = '') {
  const params = new URLSearchParams({
    destination,
    filename: fileName,
  })
  if (explicitPublicId) {
    params.set('public_id', explicitPublicId)
  }
  return `/uploads/signature?${params.toString()}`
}

function buildCloudinaryUploadForm(file, signatureData) {
  const cloudForm = new FormData()
  cloudForm.append('file', file)
  cloudForm.append('api_key', signatureData.api_key)
  cloudForm.append('timestamp', signatureData.timestamp)
  cloudForm.append('signature', signatureData.signature)
  cloudForm.append('public_id', signatureData.public_id)
  if (signatureData.asset_folder) cloudForm.append('asset_folder', signatureData.asset_folder)
  if (signatureData.overwrite) cloudForm.append('overwrite', 'true')
  if (signatureData.invalidate) cloudForm.append('invalidate', 'true')
  return cloudForm
}

async function requestUploadSignature(destination, fileName, publicId) {
  const signatureRes = await api.post(buildSignatureUrl(destination, fileName, publicId))
  return signatureRes.data?.data || null
}

async function uploadDirectToCloudinary(file, signatureData) {
  const cloudRes = await fetch(
    `https://api.cloudinary.com/v1_1/${signatureData.cloud_name}/image/upload`,
    { method: 'POST', body: buildCloudinaryUploadForm(file, signatureData) }
  )

  if (!cloudRes.ok) return null
  return cloudRes.json()
}

async function uploadViaBackend(file, destination = 'uploads') {
  const formData = new FormData()
  formData.append('file', file)
  const response = await api.post(`/uploads/images?destination=${encodeURIComponent(destination)}`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  // Mantener una sola semántica de URL consumible por el front:
  // Cloudinary devuelve secure_url y el fallback backend expone public_path.
  return response?.data?.public_path || response?.data?.path || null
}

function folderFromPublicId(publicId, destination = 'uploads') {
  if (!publicId) return destination
  return publicId.includes('/') ? publicId.split('/').slice(0, -1).join('/') : destination
}

export function resolveUploadPublicId(file, destination = 'uploads', relativePath = '') {
  const normalizedRelativePath =
    normalizeRelativeUploadPath(relativePath || file?.webkitRelativePath || '')

  if (normalizedRelativePath) {
    return localPathToPublicId(`/images/${normalizedRelativePath}`)
  }

  const normalizedDestination = String(destination || 'uploads').trim().replace(/^\/+|\/+$/g, '')
  const destinationPrefix = DESTINATION_PREFIXES[normalizedDestination] || DESTINATION_PREFIXES.uploads
  const fileName = String(file?.name || '').trim()
  if (!fileName) return ''
  return localPathToPublicId(`/images/${destinationPrefix}/${fileName}`)
}

/**
 * Sube una imagen y devuelve el objeto completo con metadatos.
 * Útil para registrar el asset en la BD después del upload.
 * @param {File} file
 * @param {string} destination
 * @param {string} explicitPublicId
 * @returns {Promise<{secure_url,public_id,folder,original_filename,format,bytes,width,height}|null>}
 */
export async function uploadImageWithMeta(file, destination = 'uploads', explicitPublicId = '') {
  if (!file) return null
  const resolvedPublicId = explicitPublicId || resolveUploadPublicId(file, destination)

  try {
    const sig = await requestUploadSignature(destination, file.name, resolvedPublicId)

    if (sig) {
      const uploaded = await uploadDirectToCloudinary(file, sig)

      if (uploaded) {
        return {
          secure_url: uploaded.secure_url,
          public_id: uploaded.public_id || sig.public_id,
          folder: sig.asset_folder || folderFromPublicId(uploaded.public_id || resolvedPublicId, destination),
          original_filename: file.name,
          format: uploaded.format,
          bytes: uploaded.bytes,
          width: uploaded.width,
          height: uploaded.height,
        }
      }
    }
  } catch {
    // fallback
  }

  // Fallback: backend tradicional
  const path = await uploadViaBackend(file, destination)
  if (!path) return null
  const fallbackPublicId = resolvedPublicId || file.name.replace(/\.[^.]+$/, '')
  return {
    secure_url: path,
    public_id: fallbackPublicId,
    folder: folderFromPublicId(fallbackPublicId, destination),
    original_filename: file.name,
    format: null,
    bytes: file.size,
    width: null,
    height: null,
  }
}

/**
 * Sube una imagen directo a Cloudinary (evita pasar por backend)
 * @param {File} file - Archivo a subir
 * @param {string} destination - Destino (uploads|instrumentos|inventario)
 * @param {string} explicitPublicId
 * @returns {Promise<string|null>} URL de la imagen o null
 */
export async function uploadImage(file, destination = 'uploads', explicitPublicId = '') {
  const meta = await uploadImageWithMeta(file, destination, explicitPublicId)
  return meta?.secure_url || null
}
