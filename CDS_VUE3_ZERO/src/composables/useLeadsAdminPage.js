import { computed, onMounted, ref } from 'vue'
import api, { extractErrorMessage } from '@/services/api'
import { formatDate } from '@/utils/format'

const VALID_STATUSES = ['new', 'contacted', 'converted']

const STATUS_LABEL = {
  new: 'Nuevo',
  contacted: 'Contactado',
  converted: 'Convertido'
}

function normalizeLead(entry) {
  return {
    id: Number(entry?.id || 0),
    nombre: String(entry?.nombre || ''),
    email: String(entry?.email || ''),
    telefono: String(entry?.telefono || ''),
    equipment_brand: String(entry?.equipment_brand || ''),
    equipment_model: String(entry?.equipment_model || ''),
    quote_result: entry?.quote_result || null,
    source: String(entry?.source || ''),
    status: String(entry?.status || 'new'),
    created_at: entry?.created_at || null
  }
}

export function useLeadsAdminPage() {
  const leads = ref([])
  const isLoading = ref(false)
  const error = ref('')
  const search = ref('')
  const busyIds = ref(new Set())

  const filteredLeads = computed(() => {
    const query = String(search.value || '').trim().toLowerCase()
    if (!query) return leads.value
    return leads.value.filter(l =>
      l.nombre.toLowerCase().includes(query) ||
      l.email.toLowerCase().includes(query) ||
      l.equipment_brand.toLowerCase().includes(query) ||
      l.equipment_model.toLowerCase().includes(query)
    )
  })

  function isBusy(id) {
    return busyIds.value.has(Number(id))
  }

  function setBusy(id, value) {
    const next = new Set(busyIds.value)
    if (value) next.add(Number(id))
    else next.delete(Number(id))
    busyIds.value = next
  }

  function statusLabel(status) {
    return STATUS_LABEL[status] || status
  }

  function nextStatus(status) {
    const idx = VALID_STATUSES.indexOf(status)
    return idx >= 0 && idx < VALID_STATUSES.length - 1
      ? VALID_STATUSES[idx + 1]
      : null
  }

  async function loadLeads() {
    isLoading.value = true
    error.value = ''
    try {
      const { data } = await api.get('/leads')
      const payload = Array.isArray(data) ? data : []
      leads.value = payload.map(normalizeLead)
    } catch (e) {
      error.value = extractErrorMessage(e)
      leads.value = []
    } finally {
      isLoading.value = false
    }
  }

  async function advanceStatus(lead) {
    const next = nextStatus(lead.status)
    if (!next) return
    setBusy(lead.id, true)
    error.value = ''
    try {
      await api.patch(`/leads/${lead.id}/status?status=${next}`)
      lead.status = next
    } catch (e) {
      error.value = extractErrorMessage(e)
    } finally {
      setBusy(lead.id, false)
    }
  }

  function formatFinalCost(quoteResult) {
    const cost = quoteResult?.final_cost
    if (!cost) return '—'
    return new Intl.NumberFormat('es-CL', {
      style: 'currency',
      currency: 'CLP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(Number(cost))
  }

  onMounted(loadLeads)

  return {
    leads,
    isLoading,
    error,
    search,
    filteredLeads,
    VALID_STATUSES,
    isBusy,
    statusLabel,
    nextStatus,
    loadLeads,
    advanceStatus,
    formatDate,
    formatFinalCost
  }
}
