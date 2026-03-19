import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { extractErrorMessage } from '@/services/api'
import {
  COLUMN_DEFS,
  createEmptyQuoteDraft,
  createQuoteDraft,
  createRepairFromQuoteData,
  fetchQuotesBoard,
  formatQuoteCurrency,
  formatQuoteDate,
  removeQuoteById,
  sendQuoteToClient,
  STATUS_OPTIONS,
  updateQuoteStatus
} from '@/services/quotesAdminService'

function createEmptyBoard() {
  return { draft_pending: [], waiting_response: [], closed: [] }
}

function createEmptyCounts() {
  return { draft_pending: 0, waiting_response: 0, closed: 0, total: 0 }
}

function createEmptyMetrics() {
  return { pending: 0, sent: 0, approved: 0, denied: 0, canceled: 0, expired_open: 0, expiring_3d: 0, open_total: 0 }
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

  const board = ref(createEmptyBoard())
  const counts = ref(createEmptyCounts())
  const metrics = ref(createEmptyMetrics())

  const showCreateModal = ref(false)
  const isCreating = ref(false)
  const newQuote = reactive(createEmptyQuoteDraft())

  const highlightedQuoteId = computed(() => {
    const value = Number(route.query?.quote_id || 0)
    return Number.isFinite(value) && value > 0 ? value : null
  })

  function resetBoard() {
    board.value = createEmptyBoard()
    counts.value = createEmptyCounts()
    metrics.value = createEmptyMetrics()
  }

  function resetCreateForm() {
    Object.assign(newQuote, createEmptyQuoteDraft())
  }

  function openCreateModal() {
    showCreateModal.value = true
  }

  function closeCreateModal() {
    showCreateModal.value = false
    resetCreateForm()
  }

  function updateNewQuoteField({ field, value }) {
    if (!field || !(field in newQuote)) return
    newQuote[field] = value
  }

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

  async function loadBoard() {
    loading.value = true
    error.value = ''

    try {
      const normalized = await fetchQuotesBoard({
        searchQuery: searchQuery.value,
        statusFilter: statusFilter.value,
      })
      board.value = normalized.board
      counts.value = normalized.counts
      metrics.value = normalized.metrics
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
      resetBoard()
    } finally {
      loading.value = false
    }
  }

  async function sendQuote(quote) {
    setBusy(quote.id, true)
    error.value = ''

    try {
      await sendQuoteToClient(quote.id, {
        sendWhatsapp: sendWhatsapp.value,
        message: customMessage.value,
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
      await updateQuoteStatus(quote.id, status)
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
      const repairId = await createRepairFromQuoteData(quote)
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
      await removeQuoteById(id)
      await loadBoard()
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      setBusy(id, false)
    }
  }

  async function submitNewQuote() {
    if (isCreating.value) return { success: false, error: null }

    isCreating.value = true
    error.value = ''

    try {
      const data = await createQuoteDraft(newQuote)
      await loadBoard()
      closeCreateModal()
      return { success: true, data }
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
      return { success: false, error: error.value }
    } finally {
      isCreating.value = false
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
    showCreateModal,
    isCreating,
    newQuote,
    isBusy,
    getColumnItems,
    getColumnCount,
    formatCurrency: formatQuoteCurrency,
    formatDate: formatQuoteDate,
    loadBoard,
    sendQuote,
    changeStatus,
    createRepairFromQuote,
    openRepair,
    deleteQuote,
    openCreateModal,
    closeCreateModal,
    updateNewQuoteField,
    submitNewQuote
  }
}
