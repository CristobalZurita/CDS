import { computed, onMounted, ref } from 'vue'
import api, { extractErrorMessage } from '@new/services/api'

function safeData(result, fallback = {}) {
  if (result.status !== 'fulfilled') return fallback
  return result.value?.data || fallback
}

function normalizeRepair(entry) {
  return {
    id: entry?.id,
    repair_number: String(entry?.repair_number || ''),
    status: String(entry?.status || ''),
    status_normalized: String(entry?.status_normalized || entry?.status || ''),
    total_cost: Number(entry?.total_cost || 0),
    intake_date: entry?.intake_date || null,
    updated_at: entry?.updated_at || null,
    client_name: entry?.client_name || entry?.cliente || '—',
    instrument: entry?.instrument || entry?.device_label || '—'
  }
}

export function useAdminDashboardPage() {
  const isLoading = ref(false)
  const error = ref('')

  const stats = ref({})
  const kpiSummary = ref({})
  const kpiDashboard = ref({})
  const kpiRevenue = ref({})
  const kpiInventory = ref({})
  const kpiClients = ref({})
  const kpiWarranty = ref({})
  const recentRepairs = ref([])

  const cards = computed(() => {
    const s = stats.value || {}
    return [
      { id: 'users', label: 'Usuarios', value: Number(s.users || 0) },
      { id: 'clients', label: 'Clientes', value: Number(s.clients || 0) },
      { id: 'repairs', label: 'Reparaciones', value: Number(s.repairs || 0) },
      { id: 'products', label: 'Productos', value: Number(s.products || 0) },
      { id: 'alerts', label: 'Alertas', value: Number(s.alerts_count || kpiDashboard.value?.alerts_count || 0) }
    ]
  })

  function formatDate(value) {
    if (!value) return '—'
    const date = new Date(value)
    if (Number.isNaN(date.getTime())) return '—'
    return new Intl.DateTimeFormat('es-CL', { dateStyle: 'medium' }).format(date)
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

  async function loadDashboard() {
    isLoading.value = true
    error.value = ''

    try {
      const [
        statsRes,
        summaryRes,
        dashboardRes,
        revenueRes,
        inventoryRes,
        clientsRes,
        warrantyRes,
        repairsRes
      ] = await Promise.allSettled([
        api.get('/stats', { params: { extended: true } }),
        api.get('/analytics/kpis/summary'),
        api.get('/analytics/dashboard'),
        api.get('/analytics/revenue'),
        api.get('/analytics/inventory'),
        api.get('/analytics/clients'),
        api.get('/analytics/warranties'),
        api.get('/repairs/', { params: { page: 1, per_page: 8 } })
      ])

      stats.value = safeData(statsRes, {})
      kpiSummary.value = safeData(summaryRes, {})
      kpiDashboard.value = safeData(dashboardRes, {})
      kpiRevenue.value = safeData(revenueRes, {})
      kpiInventory.value = safeData(inventoryRes, {})
      kpiClients.value = safeData(clientsRes, {})
      kpiWarranty.value = safeData(warrantyRes, {})

      const repairsPayload = safeData(repairsRes, [])
      if (Array.isArray(repairsPayload)) {
        recentRepairs.value = repairsPayload.map(normalizeRepair)
      } else if (Array.isArray(repairsPayload?.items)) {
        recentRepairs.value = repairsPayload.items.map(normalizeRepair)
      } else if (Array.isArray(repairsPayload?.data)) {
        recentRepairs.value = repairsPayload.data.map(normalizeRepair)
      } else {
        recentRepairs.value = []
      }
    } catch (loadError) {
      error.value = extractErrorMessage(loadError)
      recentRepairs.value = []
    } finally {
      isLoading.value = false
    }
  }

  onMounted(loadDashboard)

  return {
    isLoading,
    error,
    cards,
    kpiSummary,
    kpiDashboard,
    kpiRevenue,
    kpiInventory,
    kpiClients,
    kpiWarranty,
    recentRepairs,
    formatDate,
    formatCurrency,
    loadDashboard
  }
}
