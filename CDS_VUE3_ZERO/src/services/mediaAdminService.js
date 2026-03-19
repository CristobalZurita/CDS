import api from '@/services/api.js'
import { resolveUploadPublicId, uploadImageWithMeta } from '@/services/uploadService.js'

export const MEDIA_MAX_FILE_SIZE = 10 * 1024 * 1024

export function normalizeMediaAssetGroup(asset) {
  const source = String(asset?.folder || asset?.public_id || '').toLowerCase()
  if (source.startsWith('instrumentos/') || source.includes('/instrumentos/')) return 'instrumentos'
  if (source.startsWith('inventario/') || source.startsWith('inventario') || source.includes('/inventario/')) return 'inventario'
  if (source.startsWith('inventa') || String(asset?.folder || asset?.public_id || '').startsWith('INVENTARIO')) return 'inventario'
  return 'general'
}

export function filterMediaAssets(images, { folderFilter = '', search = '' } = {}) {
  let list = Array.isArray(images) ? images : []
  if (folderFilter) {
    list = list.filter((img) => normalizeMediaAssetGroup(img) === folderFilter)
  }
  if (search) {
    const q = String(search).toLowerCase()
    list = list.filter((img) => img.public_id?.toLowerCase().includes(q))
  }
  return list
}

export function countMediaAssetsByGroup(images, group) {
  return (Array.isArray(images) ? images : []).filter((img) => normalizeMediaAssetGroup(img) === group).length
}

export function filterBindingPickerAssets(images, search, selectedId) {
  const q = String(search || '').toLowerCase()
  const base = q
    ? images.filter((img) => img.public_id?.toLowerCase().includes(q))
    : images
  const limited = base.slice(0, 40)
  if (!selectedId) return limited

  const selected = images.find((img) => img.id === selectedId)
  if (!selected) return limited
  if (limited.some((img) => img.id === selected.id)) return limited

  return [selected, ...limited.slice(0, 39)]
}

export function createMediaBindingForm() {
  return { slot_key: '', label: '', asset_id: null }
}

export function createMediaQueueItem(file, destination, relativePath = '') {
  const normalizedPath = String(relativePath || '')
    .replace(/\\/g, '/')
    .replace(/^\/+/, '')
    .replace(/^images\//i, '')

  return {
    file,
    name: file.name,
    size: file.size,
    relativePath: normalizedPath,
    publicId: resolveUploadPublicId(file, destination, normalizedPath),
    status: 'pending',
  }
}

export async function listMediaAssets() {
  const { data } = await api.get('/media/assets')
  return data || []
}

export async function importMediaAssetsFromCloudinary() {
  const { data } = await api.post('/media/assets/import-from-cloudinary')
  return data || {}
}

export async function listMediaBindings() {
  const { data } = await api.get('/media/bindings')
  return data || []
}

export async function saveMediaBinding(slotKey, payload) {
  const { data } = await api.put(`/media/bindings/${slotKey}`, {
    asset_id: payload.asset_id,
    label: payload.label || null,
  })
  return data
}

export async function removeMediaBinding(slotKey) {
  await api.delete(`/media/bindings/${slotKey}`)
}

export async function registerUploadedMediaAsset(meta) {
  await api.post('/media/assets', meta)
}

export async function uploadMediaQueueItem(item, destination) {
  const explicitPublicId = item.publicId || resolveUploadPublicId(item.file, destination, item.relativePath)
  const meta = await uploadImageWithMeta(item.file, destination, explicitPublicId)
  if (!meta?.secure_url) return null
  await registerUploadedMediaAsset(meta).catch(() => {})
  return meta
}
