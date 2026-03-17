/**
 * Servicio de upload de imágenes
 * Usa Cloudinary directo si está disponible, fallback a backend
 */

import api from './api.js'

/**
 * Sube una imagen y devuelve el objeto completo con metadatos.
 * Útil para registrar el asset en la BD después del upload.
 * @param {File} file
 * @param {string} destination
 * @returns {Promise<{secure_url,public_id,folder,original_filename,format,bytes,width,height}|null>}
 */
export async function uploadImageWithMeta(file, destination = 'uploads') {
  if (!file) return null

  try {
    const signatureRes = await api.post(
      `/uploads/signature?destination=${encodeURIComponent(destination)}&filename=${encodeURIComponent(file.name)}`
    )
    const sig = signatureRes.data?.data

    if (sig) {
      const cloudForm = new FormData()
      cloudForm.append('file', file)
      cloudForm.append('api_key', sig.api_key)
      cloudForm.append('timestamp', sig.timestamp)
      cloudForm.append('signature', sig.signature)
      cloudForm.append('public_id', sig.public_id)
      if (sig.asset_folder) cloudForm.append('asset_folder', sig.asset_folder)
      if (sig.overwrite) cloudForm.append('overwrite', 'true')
      if (sig.invalidate) cloudForm.append('invalidate', 'true')

      const cloudRes = await fetch(
        `https://api.cloudinary.com/v1_1/${sig.cloud_name}/image/upload`,
        { method: 'POST', body: cloudForm }
      )

      if (cloudRes.ok) {
        const d = await cloudRes.json()
        return {
          secure_url: d.secure_url,
          public_id: d.public_id || sig.public_id,
          folder: sig.asset_folder || (d.public_id ? d.public_id.split('/').slice(0, -1).join('/') : destination),
          original_filename: file.name,
          format: d.format,
          bytes: d.bytes,
          width: d.width,
          height: d.height,
        }
      }
    }
  } catch {
    // fallback
  }

  // Fallback: backend tradicional
  const formData = new FormData()
  formData.append('file', file)
  const response = await api.post('/uploads/images', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  const path = response?.data?.path || null
  if (!path) return null
  return {
    secure_url: path,
    public_id: file.name.replace(/\.[^.]+$/, ''),
    folder: destination,
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
 * @returns {Promise<string|null>} URL de la imagen o null
 */
export async function uploadImage(file, destination = 'uploads') {
  if (!file) return null
  
  // Intentar upload directo a Cloudinary
  try {
    const signatureRes = await api.post(
      `/uploads/signature?destination=${encodeURIComponent(destination)}&filename=${encodeURIComponent(file.name)}`
    )
    const sig = signatureRes.data?.data
    
    if (sig) {
      const cloudForm = new FormData()
      cloudForm.append('file', file)
      cloudForm.append('api_key', sig.api_key)
      cloudForm.append('timestamp', sig.timestamp)
      cloudForm.append('signature', sig.signature)
      cloudForm.append('public_id', sig.public_id)
      if (sig.asset_folder) cloudForm.append('asset_folder', sig.asset_folder)
      if (sig.overwrite) cloudForm.append('overwrite', 'true')
      if (sig.invalidate) cloudForm.append('invalidate', 'true')
      
      const cloudRes = await fetch(
        `https://api.cloudinary.com/v1_1/${sig.cloud_name}/image/upload`,
        { method: 'POST', body: cloudForm }
      )
      
      if (cloudRes.ok) {
        const cloudData = await cloudRes.json()
        return cloudData.secure_url
      }
    }
  } catch (e) {
    // Silencioso - fallback a backend
  }
  
  // Fallback: upload tradicional por backend
  const formData = new FormData()
  formData.append('file', file)
  const response = await api.post('/uploads/images', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return response?.data?.path || null
}
