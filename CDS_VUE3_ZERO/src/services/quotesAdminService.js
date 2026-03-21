import api from '@/services/api'

export const STATUS_OPTIONS = [
  { value: 'pending', label: 'Pendiente' },
  { value: 'sent', label: 'Enviada' },
  { value: 'approved', label: 'Aprobada' },
  { value: 'denied', label: 'Rechazada' },
  { value: 'canceled', label: 'Cancelada' }
]

export const COLUMN_DEFS = [
  { key: 'draft_pending', label: 'Borrador / Pendiente' },
  { key: 'waiting_response', label: 'En espera de respuesta' },
  { key: 'closed', label: 'Cerradas' }
]

const QUOTES_BASE_PATH = '/quotations/quotes'

function toPayload(response) {
  if (!response) return {}
  if (response?.data?.data) return response.data.data
  if (response?.data) return response.data
  return response
}

function normalizeBoardPayload(payload) {
  const board = payload?.board || {}
  const counts = payload?.counts || {}
  const metrics = payload?.metrics || {}

  return {
    board: {
      draft_pending: Array.isArray(board.draft_pending) ? board.draft_pending : [],
      waiting_response: Array.isArray(board.waiting_response) ? board.waiting_response : [],
      closed: Array.isArray(board.closed) ? board.closed : []
    },
    counts: {
      draft_pending: Number(counts.draft_pending || 0),
      waiting_response: Number(counts.waiting_response || 0),
      closed: Number(counts.closed || 0),
      total: Number(counts.total || 0)
    },
    metrics: {
      pending: Number(metrics.pending || 0),
      sent: Number(metrics.sent || 0),
      approved: Number(metrics.approved || 0),
      denied: Number(metrics.denied || 0),
      canceled: Number(metrics.canceled || 0),
      expired_open: Number(metrics.expired_open || 0),
      expiring_3d: Number(metrics.expiring_3d || 0),
      open_total: Number(metrics.open_total || 0)
    }
  }
}

function defaultValidUntil() {
  const date = new Date()
  date.setDate(date.getDate() + 30)
  return date.toISOString().split('T')[0]
}

export function createEmptyQuoteDraft() {
  return {
    client_name: '',
    client_email: '',
    client_phone: '',
    problem_description: '',
    diagnosis: '',
    estimated_parts_cost: 0,
    estimated_labor_cost: 0,
    estimated_total: 0,
    valid_until: defaultValidUntil()
  }
}

export function formatQuoteCurrency(value) {
  const amount = Number(value || 0)
  return new Intl.NumberFormat('es-CL', {
    style: 'currency',
    currency: 'CLP',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(amount)
}

export function formatQuoteDate(value) {
  if (!value) return 'SIN_DATO'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return 'SIN_DATO'
  return new Intl.DateTimeFormat('es-CL', { dateStyle: 'medium' }).format(date)
}

export async function fetchQuotesBoard({ searchQuery = '', statusFilter = '', limit = 300 } = {}) {
  const params = { limit }
  const query = String(searchQuery || '').trim()
  if (query) params.q = query
  if (statusFilter) params.status = statusFilter

  const response = await api.get(`${QUOTES_BASE_PATH}/board`, { params })
  return normalizeBoardPayload(toPayload(response))
}

export async function sendQuoteToClient(quoteId, { sendWhatsapp = true, message = '' } = {}) {
  await api.post(`${QUOTES_BASE_PATH}/${quoteId}/send`, {
    send_whatsapp: Boolean(sendWhatsapp),
    message: String(message || '').trim() || null
  })
}

export async function updateQuoteStatus(quoteId, status) {
  await api.post(`${QUOTES_BASE_PATH}/${quoteId}/status`, {
    status,
    client_response: status === 'approved' ? 'Aprobada por administracion' : 'Rechazada por administracion'
  })
}

export async function createRepairFromQuoteData(quote) {
  const payload = {
    client_id: Number(quote.client_id),
    device_id: Number(quote.device_id),
    quote_id: Number(quote.id),
    title: quote.quote_number ? `OT ${quote.quote_number}` : `OT ${quote.id}`,
    description: String(quote.problem_description || 'Sin descripcion'),
    diagnosis: quote.diagnosis || null,
    parts_cost: Number(quote.estimated_parts_cost || 0),
    labor_cost: Number(quote.estimated_labor_cost || 0),
    total_cost: Number(quote.estimated_total || 0)
  }

  const response = await api.post('/repairs/', payload)
  return Number(response?.data?.id || 0)
}

export async function removeQuoteById(quoteId) {
  await api.delete(`${QUOTES_BASE_PATH}/${quoteId}`)
}

export async function createQuoteDraft(quoteData) {
  const payload = {
    client_name: quoteData.client_name,
    client_email: quoteData.client_email,
    client_phone: quoteData.client_phone || null,
    problem_description: quoteData.problem_description,
    estimated_total: Number(quoteData.estimated_total) || 0,
    estimated_parts_cost: Number(quoteData.estimated_parts_cost) || 0,
    estimated_labor_cost: Number(quoteData.estimated_labor_cost) || 0,
    diagnosis: quoteData.diagnosis || null,
    valid_until: quoteData.valid_until || null
  }

  const response = await api.post(QUOTES_BASE_PATH, payload)
  return response?.data || {}
}
