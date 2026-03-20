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

function normalizeAuditEntry(entry) {
  const details = entry?.details && typeof entry.details === 'object' ? entry.details : {}
  return {
    id: Number(entry?.id || 0),
    event_type: String(entry?.event_type || ''),
    user_id: entry?.user_id || null,
    ip_address: String(entry?.ip_address || ''),
    message: String(entry?.message || ''),
    created_at: entry?.created_at || null,
    details,
    fields: Array.isArray(details?.fields)
      ? details.fields.map((value) => String(value || '').trim()).filter(Boolean)
      : [],
    from_status: String(details?.from_status || ''),
    to_status: String(details?.to_status || ''),
    status_notes: String(details?.notes || '').trim()
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
    ot_parent_id: Number(entry?.ot_parent_id || 0),
    ot_sequence: Number(entry?.ot_sequence || 0),
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
    intake_date: entry?.intake_date || null,
    diagnosis_date: entry?.diagnosis_date || null,
    approval_date: entry?.approval_date || null,
    start_date: entry?.start_date || null,
    completion_date: entry?.completion_date || null,
    delivery_date: entry?.delivery_date || null,
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

function normalizeWarrantyClaim(entry) {
  if (!entry || typeof entry !== 'object') return null

  return {
    id: Number(entry?.id || 0),
    warranty_id: Number(entry?.warranty_id || 0),
    new_repair_id: Number(entry?.new_repair_id || 0),
    claim_number: String(entry?.claim_number || ''),
    status: String(entry?.status || ''),
    problem_description: String(entry?.problem_description || ''),
    fault_type: String(entry?.fault_type || ''),
    is_covered: entry?.is_covered == null ? null : Boolean(entry.is_covered),
    rejection_reason: String(entry?.rejection_reason || ''),
    evaluation_notes: String(entry?.evaluation_notes || ''),
    estimated_cost: Number(entry?.estimated_cost || 0),
    actual_cost: Number(entry?.actual_cost || 0),
    customer_copay: Number(entry?.customer_copay || 0),
    submitted_at: entry?.submitted_at || null,
    evaluated_at: entry?.evaluated_at || null,
    resolved_at: entry?.resolved_at || null
  }
}

function normalizeRepairPayment(entry) {
  if (!entry || typeof entry !== 'object') return null

  return {
    id: Number(entry?.id || 0),
    invoice_id: Number(entry?.invoice_id || 0),
    repair_id: Number(entry?.repair_id || 0),
    amount: Number(entry?.amount || 0),
    payment_method: String(entry?.payment_method || ''),
    transaction_id: String(entry?.transaction_id || ''),
    status: String(entry?.status || ''),
    notes: String(entry?.notes || ''),
    created_at: entry?.created_at || null,
    updated_at: entry?.updated_at || null
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
    payment_status: 'pending',
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
  const repairResponse = await api.get(`/repairs/${repairId}`)
  const [photosResponse, notesResponse, auditResponse, warranty, invoice, payments] = await Promise.all([
    api.get(`/repairs/${repairId}/photos`).catch(() => ({ data: [] })),
    api.get(`/repairs/${repairId}/notes`).catch(() => ({ data: [] })),
    api.get(`/repairs/${repairId}/audit`).catch(() => ({ data: [] })),
    fetchRepairWarranty(repairId).catch(() => null),
    fetchRepairInvoice(repairId).catch(() => null),
    fetchRepairPayments(repairId).catch(() => [])
  ])

  const repair = normalizeRepair(repairResponse?.data)

  const photosPayload = Array.isArray(photosResponse?.data) ? photosResponse.data : []
  const notesPayload = Array.isArray(notesResponse?.data) ? notesResponse.data : []
  const auditPayload = Array.isArray(auditResponse?.data) ? auditResponse.data : []
  const claims = warranty?.id
    ? await fetchWarrantyClaims(warranty.id).catch(() => [])
    : []

  return {
    repair,
    photos: photosPayload.map(normalizePhoto),
    notes: sortNotes(notesPayload.map(normalizeNote)),
    audit: auditPayload.map(normalizeAuditEntry),
    warranty,
    invoice,
    claims,
    payments
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
    payment_status: String(editForm.payment_status || 'pending').trim() || 'pending',
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

export async function fetchWarrantyClaims(warrantyId) {
  const response = await api.get(`/warranties/${warrantyId}/claims`)
  const payload = Array.isArray(response?.data) ? response.data : []
  return payload.map(normalizeWarrantyClaim).filter(Boolean)
}

export async function createWarrantyClaim(warrantyId, claimDraft) {
  const response = await api.post(`/warranties/${warrantyId}/claims`, {
    problem_description: String(claimDraft?.problemDescription || '').trim(),
    fault_type: String(claimDraft?.faultType || '').trim() || null
  })
  return normalizeWarrantyClaim(response?.data)
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

export async function fetchRepairPayments(repairId) {
  const response = await api.get('/payments/', {
    params: {
      repair_id: Number(repairId || 0)
    }
  })
  const payload = Array.isArray(response?.data) ? response.data : []
  return payload.map(normalizeRepairPayment).filter(Boolean)
}

export async function recordInvoicePayment(invoiceId, paymentDraft) {
  const response = await api.post(`/invoices/${invoiceId}/payments`, {
    amount: Number(paymentDraft?.amount || 0),
    payment_method: String(paymentDraft?.paymentMethod || 'cash').trim() || 'cash',
    transaction_id: String(paymentDraft?.transactionId || '').trim() || null
  })
  return normalizeRepairPayment(response?.data)
}

export async function notifyRepairClient(repairId) {
  await api.post(`/repairs/${repairId}/notify`)
}

export async function requestRepairSignatureLink(repairId, type, { expiresMinutes = 5 } = {}) {
  const response = await api.post('/signatures/requests', {
    repair_id: Number(repairId),
    request_type: String(type || 'ingreso'),
    expires_minutes: Number(expiresMinutes || 5)
  })

  const payload = response?.data || response || {}
  const token = payload?.token || ''

  return {
    id: Number(payload?.id || 0),
    repair_id: Number(payload?.repair_id || repairId || 0),
    request_type: String(payload?.request_type || type || ''),
    status: String(payload?.status || 'pending'),
    token,
    expires_at: payload?.expires_at || null,
    url: token ? buildAppUrl(`/signature/${token}`) : ''
  }
}

export async function requestRepairPhotoUploadLink(
  repairId,
  { photoType = 'client', expiresMinutes = 10 } = {}
) {
  const response = await api.post('/photo-requests/', null, {
    params: {
      repair_id: Number(repairId),
      photo_type: String(photoType || 'client'),
      expires_minutes: Number(expiresMinutes || 10)
    }
  })

  const payload = response?.data || response || {}
  const token = payload?.token || ''

  return {
    id: Number(payload?.id || 0),
    repair_id: Number(payload?.repair_id || repairId || 0),
    photo_type: String(payload?.photo_type || photoType || 'client'),
    status: String(payload?.status || 'pending'),
    token,
    expires_at: payload?.expires_at || null,
    url: token ? buildAppUrl(`/photo-upload/${token}`) : ''
  }
}

export async function cancelRepairSignatureRequest(requestId) {
  await api.post(`/signatures/requests/${requestId}/cancel`)
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
