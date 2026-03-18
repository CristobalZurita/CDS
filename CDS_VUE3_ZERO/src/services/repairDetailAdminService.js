import api from '@/services/api'
import { uploadImage } from '@/services/uploadService'

export const REPAIR_DETAIL_STATUS_OPTIONS = [
  { id: 1, label: 'Ingreso' },
  { id: 2, label: 'Diagnostico' },
  { id: 3, label: 'Presupuesto' },
  { id: 4, label: 'Aprobado' },
  { id: 5, label: 'En trabajo' },
  { id: 6, label: 'Listo' },
  { id: 7, label: 'Entregado' },
  { id: 8, label: 'Noventena' },
  { id: 9, label: 'Archivado' },
  { id: 10, label: 'Rechazado' }
]

function buildApiHost() {
  const rawBase = String(import.meta.env.VITE_API_URL || '/api/v1').trim()

  if (rawBase.startsWith('http://') || rawBase.startsWith('https://')) {
    const baseWithoutApi = rawBase.includes('/api/') ? rawBase.split('/api/')[0] : rawBase
    return baseWithoutApi.replace(/\/+$/, '')
  }

  if (typeof window !== 'undefined' && window.location?.origin) {
    return window.location.origin
  }

  return ''
}

const API_HOST = buildApiHost()

function toAbsoluteUrl(value) {
  const path = String(value || '').trim()
  if (!path) return ''
  if (path.startsWith('http://') || path.startsWith('https://')) return path
  if (path.startsWith('/')) return `${API_HOST}${path}`
  return `${API_HOST}/${path}`
}

function buildAppUrl(path) {
  if (typeof window === 'undefined' || !window.location?.origin) return ''
  return `${window.location.origin}${path}`
}

function normalizePhoto(entry) {
  const relative = entry?.photo_url || entry?.photo_download_url || ''
  return {
    id: Number(entry?.id || 0),
    photo_type: String(entry?.photo_type || 'general'),
    caption: String(entry?.caption || ''),
    created_at: entry?.created_at || null,
    resolved_photo_url: toAbsoluteUrl(relative)
  }
}

function normalizeNote(entry) {
  return {
    id: Number(entry?.id || 0),
    note: String(entry?.note || ''),
    note_type: String(entry?.note_type || 'internal'),
    created_at: entry?.created_at || null,
    user_id: entry?.user_id || null
  }
}

function sortNotes(entries) {
  return entries.sort((a, b) => new Date(b.created_at || 0).getTime() - new Date(a.created_at || 0).getTime())
}

function normalizeRepair(entry) {
  if (!entry || typeof entry !== 'object') return null
  return {
    id: Number(entry?.id || 0),
    repair_code: String(entry?.repair_code || entry?.repair_number || ''),
    repair_number: String(entry?.repair_number || ''),
    status_id: Number(entry?.status_id || 0),
    status: String(entry?.status || ''),
    priority: Number(entry?.priority || 2),
    archived_at: entry?.archived_at || null,
    problem_reported: String(entry?.problem_reported || ''),
    diagnosis: String(entry?.diagnosis || ''),
    work_performed: String(entry?.work_performed || ''),
    parts_cost: Number(entry?.parts_cost || 0),
    labor_cost: Number(entry?.labor_cost || 0),
    additional_cost: Number(entry?.additional_cost || 0),
    discount: Number(entry?.discount || 0),
    total_cost: Number(entry?.total_cost || 0),
    paid_amount: Number(entry?.paid_amount || 0),
    payment_status: String(entry?.payment_status || ''),
    payment_method: String(entry?.payment_method || ''),
    signature_ingreso_path: String(entry?.signature_ingreso_path || ''),
    signature_retiro_path: String(entry?.signature_retiro_path || ''),
    client: entry?.client || null,
    device: entry?.device || null
  }
}

export function baseRepairDetailEditForm() {
  return {
    diagnosis: '',
    work_performed: '',
    parts_cost: 0,
    labor_cost: 0,
    additional_cost: 0,
    discount: 0,
    total_cost: 0,
    paid_amount: 0,
    payment_method: ''
  }
}

export function noteTypeClass(noteType) {
  const key = String(noteType || '').toLowerCase()
  if (key === 'public') return 'note-public'
  if (key === 'technical') return 'note-technical'
  return 'note-internal'
}

export async function fetchRepairDetailBundle(repairId) {
  const [repairResponse, photosResponse, notesResponse] = await Promise.all([
    api.get(`/repairs/${repairId}`).catch(() => null),
    api.get(`/repairs/${repairId}/photos`).catch(() => ({ data: [] })),
    api.get(`/repairs/${repairId}/notes`).catch(() => ({ data: [] }))
  ])

  let repair = repairResponse?.data ? normalizeRepair(repairResponse.data) : null
  if (!repair) {
    const listResponse = await api.get('/repairs/')
    const listPayload = Array.isArray(listResponse?.data) ? listResponse.data : []
    const found = listPayload.find((entry) => Number(entry?.id || 0) === Number(repairId || 0))
    repair = normalizeRepair(found)
  }

  const photosPayload = Array.isArray(photosResponse?.data) ? photosResponse.data : []
  const notesPayload = Array.isArray(notesResponse?.data) ? notesResponse.data : []

  return {
    repair,
    photos: photosPayload.map(normalizePhoto),
    notes: sortNotes(notesPayload.map(normalizeNote))
  }
}

export async function updateRepairStatus(repairId, statusId) {
  await api.put(`/repairs/${repairId}`, {
    status_id: Number(statusId || 1)
  })
}

export async function saveRepairDetailFields(repairId, editForm) {
  const payload = {
    diagnosis: String(editForm.diagnosis || '').trim() || null,
    work_performed: String(editForm.work_performed || '').trim() || null,
    parts_cost: Number(editForm.parts_cost || 0),
    labor_cost: Number(editForm.labor_cost || 0),
    additional_cost: Number(editForm.additional_cost || 0),
    discount: Number(editForm.discount || 0),
    total_cost: Number(editForm.total_cost || 0),
    paid_amount: Number(editForm.paid_amount || 0),
    payment_method: String(editForm.payment_method || '').trim() || null
  }

  await api.put(`/repairs/${repairId}`, payload)
}

export async function archiveRepairById(repairId) {
  await api.post(`/repairs/${repairId}/archive`)
}

export async function reactivateRepairById(repairId) {
  await api.post(`/repairs/${repairId}/reactivate`)
}

export async function notifyRepairClient(repairId) {
  await api.post(`/repairs/${repairId}/notify`)
}

export async function requestRepairSignatureLink(repairId, type) {
  const response = await api.post('/signatures/requests', {
    repair_id: Number(repairId),
    request_type: String(type || 'ingreso'),
    expires_minutes: 5
  })

  const token = response?.data?.token || response?.token || ''
  return token ? buildAppUrl(`/signature/${token}`) : ''
}

export async function requestRepairPhotoUploadLink(repairId) {
  const response = await api.post('/photo-requests/', null, {
    params: {
      repair_id: Number(repairId),
      photo_type: 'client',
      expires_minutes: 10
    }
  })

  const token = response?.data?.token || response?.token || ''
  return token ? buildAppUrl(`/photo-upload/${token}`) : ''
}

export async function uploadRepairPhoto(repairId, file, { photoType = 'general', caption = '' } = {}) {
  const photoPath = await uploadImage(file, 'uploads')
  if (!photoPath) {
    throw new Error('No se recibio path de la imagen.')
  }

  await api.post(`/repairs/${repairId}/photos`, {
    photo_url: photoPath,
    photo_type: String(photoType || 'general'),
    caption: String(caption || '').trim() || null
  })

  const response = await api.get(`/repairs/${repairId}/photos`)
  const payload = Array.isArray(response?.data) ? response.data : []
  return payload.map(normalizePhoto)
}

export async function addRepairNote(repairId, { note, noteType = 'internal' }) {
  await api.post(`/repairs/${repairId}/notes`, {
    note,
    note_type: String(noteType || 'internal')
  })

  const response = await api.get(`/repairs/${repairId}/notes`)
  const payload = Array.isArray(response?.data) ? response.data : []
  return sortNotes(payload.map(normalizeNote))
}

export async function downloadRepairClosurePdf(repairId, repair) {
  const response = await api.get(`/repairs/${repairId}/closure-pdf`, {
    responseType: 'blob'
  })

  const blob = new Blob([response.data], { type: 'application/pdf' })
  const blobUrl = window.URL.createObjectURL(blob)
  const code = String(repair?.repair_code || repair?.repair_number || `OT_${repairId}`)
  const filename = `CIERRE_${code.replace(/[^a-zA-Z0-9._-]+/g, '_')}.pdf`

  const link = document.createElement('a')
  link.href = blobUrl
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(blobUrl)
}
