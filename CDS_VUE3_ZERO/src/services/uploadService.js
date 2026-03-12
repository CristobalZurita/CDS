/**
 * Servicio de upload de imágenes
 * Usa Cloudinary directo si está disponible, fallback a backend
 */

import api from './api.js'

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
    const signatureRes = await api.post(`/uploads/signature?destination=${destination}`)
    const sig = signatureRes.data?.data
    
    if (sig) {
      const cloudForm = new FormData()
      cloudForm.append('file', file)
      cloudForm.append('api_key', sig.api_key)
      cloudForm.append('timestamp', sig.timestamp)
      cloudForm.append('signature', sig.signature)
      cloudForm.append('folder', sig.folder)
      
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
