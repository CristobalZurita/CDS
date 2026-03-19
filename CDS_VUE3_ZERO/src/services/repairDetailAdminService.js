import api from '@/services/api'
import { uploadImage } from '@/services/uploadService'

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
    status_code: String(entry?.status_code || ''),
    allowed_status_ids: Array.isArray(entry?.allowed_status_ids)
      ? entry.allowed_status_ids.map((value) => Number(value || 0)).filter((value) => value > 0)
      : [],
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
    warranty_days: Number(entry?.warranty_days || 0),
    warranty_until: entry?.warranty_until || null,
    signature_ingreso_path: String(entry?.signature_ingreso_path || ''),
    signature_retiro_path: String(entry?.signature_retiro_path || ''),
    client: entry?.client || null,
    device: entry?.device || null
  }
}

function diffDaysUntil(dateValue) {
  if (!dateValue) return 0
  const end = new Date(dateValue)
  if (Number.isNaN(end.getTime())) return 0
  const deltaMs = end.getTime() - Date.now()
  return Math.max(0, Math.ceil(deltaMs / (1000 * 60 * 60 * 24)))
}

function normalizeWarranty(entry) {
  if (!entry || typeof entry !== 'object') return null

  const status = String(entry?.status || '')
  const endDate = entry?.end_date || null

  return {
    id: Number(entry?.id || 0),
    repair_id: Number(entry?.repair_id || 0),
    warranty_type: String(entry?.warranty_type || ''),
    status,
    start_date: entry?.start_date || null,
    end_date: endDate,
    duration_days: Number(entry?.duration_days || 0),
    claims_used: Number(entry?.claims_used || 0),
    max_claims: Number(entry?.max_claims || 0),
    coverage_description: String(entry?.coverage_description || ''),
    exclusions: String(entry?.exclusions || ''),
    max_claim_amount: Number(entry?.max_claim_amount || 0),
    days_remaining: diffDaysUntil(endDate),
    is_active: status === 'active' && diffDaysUntil(endDate) > 0
  }
}

function normalizeInvoice(entry) {
  if (!entry || typeof entry !== 'object') return null

  return {
    id: Number(entry?.id || 0),
    repair_id: Number(entry?.repair_id || 0),
    invoice_number: String(entry?.invoice_number || ''),
    invoice_type: String(entry?.invoice_type || ''),
    status: String(entry?.status || ''),
    issue_date: entry?.issue_date || null,
    due_date: entry?.due_date || null,
    total: Number(entry?.total || 0),
    subtotal: Number(entry?.subtotal || 0),
    tax_amount: Number(entry?.tax_amount || 0),
    amount_paid: Number(entry?.amount_paid || 0),
    amount_due: Number(entry?.amount_due || 0),
    client_name: String(entry?.client_name || '')
  }
}

function normalizeRepairStatusOption(entry) {
  if (!entry || typeof entry !== 'object') return null

  const id = Number(entry?.id || 0)
  if (!id) return null

  return {
    id,
    code: String(entry?.code || ''),
    label: String(entry?.name || entry?.label || entry?.code || `Estado ${id}`),
    color: String(entry?.color || '')
  }
}

export function buildFallbackRepairStatusOption(repair) {
  const id = Number(repair?.status_id || 0)
  if (!id) return null
  return {
    id,
    code: String(repair?.status_code || ''),
    label: String(repair?.status || `Estado ${id}`),
    color: ''
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
  const [repairResponse, photosResponse, notesResponse, warranty, invoice] = await Promise.all([
    api.get(`/repairs/${repairId}`).catch(() => null),
    api.get(`/repairs/${repairId}/photos`).catch(() => ({ data: [] })),
    api.get(`/repairs/${repairId}/notes`).catch(() => ({ data: [] })),
    fetchRepairWarranty(repairId).catch(() => null),
    fetchRepairInvoice(repairId).catch(() => null)
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
    notes: sortNotes(notesPayload.map(normalizeNote)),
    warranty,
    invoice
  }
}

export async function fetchRepairStatusOptions() {
  const response = await api.get('/repair-statuses/')
  const payload = Array.isArray(response?.data) ? response.data : []
  return payload.map(normalizeRepairStatusOption).filter(Boolean)
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

export async function fetchRepairWarranty(repairId) {
  try {
    const response = await api.get(`/warranties/by-repair/${repairId}`)
    return normalizeWarranty(response?.data)
  } catch (requestError) {
    if (Number(requestError?.response?.status || 0) === 404) {
      return null
    }
    throw requestError
  }
}

export async function createRepairWarranty(repairId) {
  const response = await api.post(`/warranties/auto-create/${repairId}`)
  return normalizeWarranty(response?.data)
}

export async function fetchRepairInvoice(repairId) {
  const response = await api.get('/invoices/', {
    params: {
      repair_id: Number(repairId || 0),
      limit: 1
    }
  })
  const payload = Array.isArray(response?.data) ? response.data : []
  return normalizeInvoice(payload[0] || null)
}

export async function createRepairInvoice(repairId) {
  const response = await api.post(`/invoices/from-repair/${repairId}`)
  return normalizeInvoice(response?.data)
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
