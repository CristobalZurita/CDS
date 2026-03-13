import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api, { extractErrorMessage } from '@/services/api'
import { formatDate, formatCurrency } from '@/utils/format'

const STATUS_OPTIONS = [
  'draft',
  'suggested',
  'approved',
  'requested',
  'pending_payment',
  'proof_submitted',
  'paid_client',
  'purchased_admin',
  'received',
  'applied_ot',
  'cancelled'
]

function normalizeClient(entry) {
  return {
    id: Number(entry?.id || 0),
    name: String(entry?.name || ''),
    client_code: String(entry?.client_code || '')
  }
}

function normalizeRepair(entry) {
  return {
    id: Number(entry?.id || 0),
    repair_code: String(entry?.repair_code || entry?.repair_number || ''),
    client_name: String(entry?.client_name || ''),
    problem_reported: String(entry?.problem_reported || '')
  }
}

function baseCreateForm() {
  return {
    client_id: '',
    repair_id: '',
    notes: '',
    item_name: '',
    item_sku: '',
    item_qty: 1,
    item_price: 0,
    item_url: ''
  }
}

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
  if (!path) return '#'
  if (path.startsWith('http://') || path.startsWith('https://')) return path
  if (path.startsWith('/')) return `${API_HOST}${path}`
  return `${API_HOST}/${path}`
}

export function usePurchaseRequestsPage() {
  const route = useRoute()
  const router = useRouter()

  const requests = ref([])
  const clients = ref([])
  const repairs = ref([])

  const loading = ref(false)
  const error = ref('')
  const busyIds = ref(new Set())

  const showForm = ref(false)
  const createForm = ref(baseCreateForm())
  const paymentDraft = ref({})

  const activeRepairFilter = computed(() => {
    const value = Number(route.query?.repair_id || 0)
    return Number.isFinite(value) && value > 0 ? value : null
  })

  function resetCreateForm() {
    createForm.value = baseCreateForm()
  }

  function toggleForm() {
    showForm.value = !showForm.value
    if (!showForm.value) resetCreateForm()
  }

  function isBusy(requestId) {
    return busyIds.value.has(Number(requestId))
  }

  function setBusy(requestId, value) {
    const id = Number(requestId)
    const next = new Set(busyIds.value)
    if (value) next.add(id)
    else next.delete(id)
    busyIds.value = next
  }

  function ensureDraft(requestItem) {
    const id = Number(requestItem?.id || 0)
    if (!id) return

    if (!paymentDraft.value[id]) {
      paymentDraft.value[id] = {
        amount: Math.max(1, Number(requestItem.requested_amount || requestItem.total_items_amount || 1)),
        dueDays: 3,
        instruction: 'Deposita el monto solicitado y sube comprobante en tu panel.'
      }
    }
  }

  async function loadSupportData() {
    try {
      const [clientsResponse, repairsResponse] = await Promise.all([
        api.get('/clients/').catch(() => ({ data: [] })),
        api.get('/repairs/').catch(() => ({ data: [] }))
      ])

      const clientsPayload = Array.isArray(clientsResponse?.data) ? clientsResponse.data : []
      const repairsPayload = Array.isArray(repairsResponse?.data) ? repairsResponse.data : []

      clients.value = clientsPayload.map(normalizeClient)
      repairs.value = repairsPayload.map(normalizeRepair)
    } catch {
      clients.value = []
      repairs.value = []
    }
  }

  async function loadRequests() {
    loading.value = true
    error.value = ''

    try {
      const params = {}
      if (activeRepairFilter.value) {
        params.repair_id = activeRepairFilter.value
      }

      const response = await api.get('/purchase-requests/board', { params })
      const payload = Array.isArray(response?.data?.requests) ? response.data.requests : []
      requests.value = payload

      requests.value.forEach(ensureDraft)
    } catch (requestError) {
      requests.value = []
      error.value = extractErrorMessage(requestError)
    } finally {
      loading.value = false
    }
  }

  async function createRequest() {
    error.value = ''

    const itemName = String(createForm.value.item_name || '').trim()
    if (!itemName) {
      error.value = 'Debes indicar al menos un item.'
      return
    }

    const payload = {
      client_id: createForm.value.client_id ? Number(createForm.value.client_id) : null,
      repair_id: createForm.value.repair_id ? Number(createForm.value.repair_id) : null,
      notes: String(createForm.value.notes || '').trim() || null,
      items: [
        {
          name: itemName,
          sku: String(createForm.value.item_sku || '').trim() || null,
          quantity: Math.max(1, Number(createForm.value.item_qty || 1)),
          unit_price: Math.max(0, Number(createForm.value.item_price || 0)),
          external_url: String(createForm.value.item_url || '').trim() || null
        }
      ]
    }

    loading.value = true

    try {
      await api.post('/purchase-requests/', payload)
      showForm.value = false
      resetCreateForm()
      await loadRequests()
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      loading.value = false
    }
  }

  async function requestPayment(requestItem) {
    const id = Number(requestItem?.id || 0)
    if (!id) return

    setBusy(id, true)
    error.value = ''

    try {
      ensureDraft(requestItem)
      const draft = paymentDraft.value[id]
      await api.post(`/purchase-requests/${id}/request-payment`, {
        amount: Number(draft.amount || requestItem.requested_amount || requestItem.total_items_amount || 1),
        due_days: Number(draft.dueDays || 3),
        instruction: String(draft.instruction || '').trim() || null
      })
      await loadRequests()
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      setBusy(id, false)
    }
  }

  async function confirmPayment(requestItem) {
    const id = Number(requestItem?.id || 0)
    if (!id) return

    setBusy(id, true)
    error.value = ''

    try {
      await api.post(`/purchase-requests/${id}/confirm-payment`, {
        admin_notes: 'Pago validado por administracion'
      })
      await loadRequests()
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      setBusy(id, false)
    }
  }

  async function setStatus(requestItem, status) {
    const id = Number(requestItem?.id || 0)
    if (!id || !status) return

    setBusy(id, true)
    error.value = ''

    try {
      await api.patch(`/purchase-requests/${id}`, {
        status: String(status)
      })
      await loadRequests()
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      setBusy(id, false)
    }
  }

  async function deleteRequest(requestItem) {
    const id = Number(requestItem?.id || 0)
    if (!id) return

    setBusy(id, true)
    error.value = ''

    try {
      await api.delete(`/purchase-requests/${id}`)
      await loadRequests()
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      setBusy(id, false)
    }
  }

  async function clearRepairFilter() {
    const nextQuery = { ...route.query }
    delete nextQuery.repair_id
    await router.replace({ name: 'admin-purchase-requests', query: nextQuery })
  }

  watch(
    () => route.query?.repair_id,
    () => {
      loadRequests()
    }
  )

  onMounted(async () => {
    await Promise.all([loadSupportData(), loadRequests()])
  })

  return {
    requests,
    clients,
    repairs,
    loading,
    error,
    showForm,
    createForm,
    paymentDraft,
    activeRepairFilter,
    statusOptions: STATUS_OPTIONS,
    toggleForm,
    isBusy,
    formatCurrency,
    formatDate,
    toApiPath: toAbsoluteUrl,
    loadRequests,
    createRequest,
    requestPayment,
    confirmPayment,
    setStatus,
    deleteRequest,
    clearRepairFilter
  }
}
