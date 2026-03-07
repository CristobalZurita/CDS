import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api, { extractErrorMessage } from '@new/services/api'

const STATUS_OPTIONS = [
  { value: 'pending', label: 'Pendiente' },
  { value: 'sent', label: 'Enviada' },
  { value: 'approved', label: 'Aprobada' },
  { value: 'denied', label: 'Rechazada' },
  { value: 'canceled', label: 'Cancelada' }
]

const COLUMN_DEFS = [
  { key: 'draft_pending', label: 'Borrador / Pendiente' },
  { key: 'waiting_response', label: 'En espera de respuesta' },
  { key: 'closed', label: 'Cerradas' }
]

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

export function useQuotesAdminPage() {
  const route = useRoute()
  const router = useRouter()

  const loading = ref(false)
  const error = ref('')
  const searchQuery = ref('')
  const statusFilter = ref('')
  const customMessage = ref('')
  const sendWhatsapp = ref(true)
  const busyIds = ref(new Set())

  const board = ref({ draft_pending: [], waiting_response: [], closed: [] })
  const counts = ref({ draft_pending: 0, waiting_response: 0, closed: 0, total: 0 })
  const metrics = ref({ pending: 0, sent: 0, approved: 0, denied: 0, canceled: 0, expired_open: 0, expiring_3d: 0, open_total: 0 })

  const highlightedQuoteId = computed(() => {
    const value = Number(route.query?.quote_id || 0)
    return Number.isFinite(value) && value > 0 ? value : null
  })

  function isBusy(quoteId) {
    return busyIds.value.has(Number(quoteId))
  }

  function setBusy(quoteId, value) {
    const id = Number(quoteId)
    const next = new Set(busyIds.value)
    if (value) {
      next.add(id)
    } else {
      next.delete(id)
    }
    busyIds.value = next
  }

  function toPayload(response) {
    if (!response) return {}
    if (response?.data?.data) return response.data.data
    if (response?.data) return response.data
    return response
  }

  function filterBySearch(items) {
    const query = String(searchQuery.value || '').trim().toLowerCase()
    if (!query) return items

    return items.filter((quote) => {
      const text = [
        quote?.quote_number,
        quote?.client?.name,
        quote?.client_name,
        quote?.problem_description,
        quote?.status
      ]
        .filter(Boolean)
        .join(' ')
        .toLowerCase()

      return text.includes(query)
    })
  }

  function getColumnItems(columnKey) {
    return filterBySearch(board.value[columnKey] || [])
  }

  function getColumnCount(columnKey) {
    return getColumnItems(columnKey).length
  }

  function formatCurrency(value) {
    const amount = Number(value || 0)
    return new Intl.NumberFormat('es-CL', {
      style: 'currency',
      currency: 'CLP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount)
  }

  function formatDate(value) {
    if (!value) return 'SIN_DATO'
    const date = new Date(value)
    if (Number.isNaN(date.getTime())) return 'SIN_DATO'
    return new Intl.DateTimeFormat('es-CL', { dateStyle: 'medium' }).format(date)
  }

  async function loadBoard() {
    loading.value = true
    error.value = ''

    try {
      const params = { limit: 300 }

      const q = String(searchQuery.value || '').trim()
      if (q) params.q = q

      if (statusFilter.value) params.status = statusFilter.value

      const response = await api.get('/diagnostic/quotes/board', { params })
      const normalized = normalizeBoardPayload(toPayload(response))
      board.value = normalized.board
      counts.value = normalized.counts
      metrics.value = normalized.metrics
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
      board.value = { draft_pending: [], waiting_response: [], closed: [] }
    } finally {
      loading.value = false
    }
  }

  async function sendQuote(quote) {
    setBusy(quote.id, true)
    error.value = ''

    try {
      await api.post(`/diagnostic/quotes/${quote.id}/send`, {
        send_whatsapp: Boolean(sendWhatsapp.value),
        message: String(customMessage.value || '').trim() || null
      })
      await loadBoard()
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      setBusy(quote.id, false)
    }
  }

  async function changeStatus(quote, status) {
    setBusy(quote.id, true)
    error.value = ''

    try {
      await api.post(`/diagnostic/quotes/${quote.id}/status`, {
        status,
        client_response: status === 'approved' ? 'Aprobada por administracion' : 'Rechazada por administracion'
      })
      await loadBoard()
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      setBusy(quote.id, false)
    }
  }

  async function createRepairFromQuote(quote) {
    if (!quote?.id || !quote?.client_id) {
      error.value = 'No se pudo crear OT: faltan datos de cliente o cotizacion.'
      return
    }

    setBusy(quote.id, true)
    error.value = ''

    try {
      const payload = {
        client_id: Number(quote.client_id),
        quote_id: Number(quote.id),
        title: quote.quote_number ? `OT ${quote.quote_number}` : `OT ${quote.id}`,
        description: String(quote.problem_description || 'Sin descripcion'),
        model: String(quote.device_model || quote?.device?.model || quote?.client?.name || 'SIN_MODELO'),
        diagnosis: quote.diagnosis || null,
        parts_cost: Number(quote.estimated_parts_cost || 0),
        labor_cost: Number(quote.estimated_labor_cost || 0),
        total_cost: Number(quote.estimated_total || 0)
      }

      const response = await api.post('/repairs/', payload)
      const repairId = Number(response?.data?.id || 0)

      await loadBoard()

      if (repairId > 0) {
        router.push({ name: 'admin-repair-detail', params: { id: repairId } })
      }
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      setBusy(quote.id, false)
    }
  }

  function openRepair(repairId) {
    const id = Number(repairId || 0)
    if (!id) return
    router.push({ name: 'admin-repair-detail', params: { id } })
  }

  async function deleteQuote(quote) {
    const id = Number(quote?.id || 0)
    if (!id) return

    setBusy(id, true)
    error.value = ''

    try {
      await api.delete(`/diagnostic/quotes/${id}`)
      await loadBoard()
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      setBusy(id, false)
    }
  }

  onMounted(loadBoard)

  return {
    loading,
    error,
    searchQuery,
    statusFilter,
    customMessage,
    sendWhatsapp,
    statusOptions: STATUS_OPTIONS,
    columnDefs: COLUMN_DEFS,
    counts,
    metrics,
    highlightedQuoteId,
    isBusy,
    getColumnItems,
    getColumnCount,
    formatCurrency,
    formatDate,
    loadBoard,
    sendQuote,
    changeStatus,
    createRepairFromQuote,
    openRepair,
    deleteQuote
  }
}
