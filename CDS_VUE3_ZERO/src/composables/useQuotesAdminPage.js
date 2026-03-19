import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { extractErrorMessage } from '@/services/api'
import {
  createEmptyQuotesBoard,
  createEmptyQuotesCounts,
  createEmptyQuotesMetrics,
  filterQuotesBySearch,
  isQuoteBusy,
  setQuoteBusyState,
  updateQuoteDraftField
} from '@/composables/quotesAdminState'
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

  const board = ref(createEmptyQuotesBoard())
  const counts = ref(createEmptyQuotesCounts())
  const metrics = ref(createEmptyQuotesMetrics())

  const showCreateModal = ref(false)
  const isCreating = ref(false)
  const newQuote = reactive(createEmptyQuoteDraft())

  const highlightedQuoteId = computed(() => {
    const value = Number(route.query?.quote_id || 0)
    return Number.isFinite(value) && value > 0 ? value : null
  })

  function resetBoard() {
    board.value = createEmptyQuotesBoard()
    counts.value = createEmptyQuotesCounts()
    metrics.value = createEmptyQuotesMetrics()
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
    updateQuoteDraftField(newQuote, { field, value })
  }

  function isBusy(quoteId) {
    return isQuoteBusy(busyIds.value, quoteId)
  }

  function setBusy(quoteId, value) {
    busyIds.value = setQuoteBusyState(busyIds.value, quoteId, value)
  }

  function getColumnItems(columnKey) {
    return filterQuotesBySearch(board.value[columnKey] || [], searchQuery.value)
  }

  function getColumnCount(columnKey) {
    return getColumnItems(columnKey).length
  }

  function applyBoardState(normalized) {
    board.value = normalized?.board || createEmptyQuotesBoard()
    counts.value = normalized?.counts || createEmptyQuotesCounts()
    metrics.value = normalized?.metrics || createEmptyQuotesMetrics()
  }

  async function runBusyQuoteTask(quoteId, task, { reload = true, onSuccess = null } = {}) {
    setBusy(quoteId, true)
    error.value = ''

    try {
      const result = await task()

      if (reload) {
        await loadBoard()
      }

      if (typeof onSuccess === 'function') {
        await onSuccess(result)
      }

      return result
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
      return null
    } finally {
      setBusy(quoteId, false)
    }
  }

  async function runCreateQuoteTask(task) {
    if (isCreating.value) return { success: false, error: null }

    isCreating.value = true
    error.value = ''

    try {
      const data = await task()
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

  async function loadBoard() {
    loading.value = true
    error.value = ''

    try {
      const normalized = await fetchQuotesBoard({
        searchQuery: searchQuery.value,
        statusFilter: statusFilter.value,
      })
      applyBoardState(normalized)
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
      resetBoard()
    } finally {
      loading.value = false
    }
  }

  async function sendQuote(quote) {
    await runBusyQuoteTask(quote.id, () => sendQuoteToClient(quote.id, {
        sendWhatsapp: sendWhatsapp.value,
        message: customMessage.value,
      }))
  }

  async function changeStatus(quote, status) {
    await runBusyQuoteTask(quote.id, () => updateQuoteStatus(quote.id, status))
  }

  async function createRepairFromQuote(quote) {
    if (!quote?.id || !quote?.client_id) {
      error.value = 'No se pudo crear OT: faltan datos de cliente o cotizacion.'
      return
    }

    await runBusyQuoteTask(quote.id, () => createRepairFromQuoteData(quote), {
      onSuccess: async (repairId) => {
        if (repairId > 0) {
          await router.push({ name: 'admin-repair-detail', params: { id: repairId } })
        }
      }
    })
  }

  function openRepair(repairId) {
    const id = Number(repairId || 0)
    if (!id) return
    router.push({ name: 'admin-repair-detail', params: { id } })
  }

  async function deleteQuote(quote) {
    const id = Number(quote?.id || 0)
    if (!id) return

    await runBusyQuoteTask(id, () => removeQuoteById(id))
  }

  async function submitNewQuote() {
    return runCreateQuoteTask(() => createQuoteDraft(newQuote))
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
