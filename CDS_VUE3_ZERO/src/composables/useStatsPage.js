import { computed, onMounted, ref } from 'vue'
import api, { extractErrorMessage } from '@/services/api'
import { formatCurrency } from '@/utils/format'

function safeData(result, fallback = {}) {
  if (result.status !== 'fulfilled') return fallback
  return result.value?.data || fallback
}

export function useStatsPage() {
  const isLoading = ref(false)
  const error = ref('')

  const stats = ref({})
  const kpiSummary = ref({})
  const kpiDashboard = ref({})
  const kpiRevenue = ref({})
  const kpiInventory = ref({})
  const kpiClients = ref({})
  const kpiWarranty = ref({})
  const repairsTimeline = ref([])
  const revenueTimeline = ref([])
  const kpiTurnaround = ref({})
  const kpiOverdue = ref({})
  const kpiLeadConversion = ref({})
  const kpiTopModels = ref([])
  const kpiClientReturn = ref({})

  const cards = computed(() => {
    const s = stats.value || {}
    return [
      { id: 'users', label: 'Usuarios', value: Number(s.users || 0) },
      { id: 'clients', label: 'Clientes', value: Number(s.clients || 0) },
      { id: 'repairs', label: 'Reparaciones', value: Number(s.repairs || 0) },
      { id: 'products', label: 'Productos', value: Number(s.products || 0) },
      { id: 'pending', label: 'Pendientes', value: Number(s.pending_repairs || 0) },
      { id: 'active', label: 'Activas', value: Number(s.active_repairs || 0) }
    ]
  })

  async function load() {
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
        repairsTimelineRes,
        revenueTimelineRes,
        turnaroundRes,
        overdueRes,
        leadConvRes,
        topModelsRes,
        clientReturnRes,
      ] = await Promise.allSettled([
        api.get('/stats', { params: { extended: true } }),
        api.get('/analytics/kpis/summary'),
        api.get('/analytics/dashboard'),
        api.get('/analytics/revenue'),
        api.get('/analytics/inventory'),
        api.get('/analytics/clients'),
        api.get('/analytics/warranties'),
        api.get('/analytics/repairs/timeline', { params: { days: 30, group_by: 'day' } }),
        api.get('/analytics/revenue/timeline', { params: { months: 12 } }),
        api.get('/analytics/kpis/turnaround'),
        api.get('/analytics/kpis/overdue'),
        api.get('/analytics/kpis/lead-conversion'),
        api.get('/analytics/kpis/top-models', { params: { limit: 8 } }),
        api.get('/analytics/kpis/client-return'),
      ])

      stats.value = safeData(statsRes, {})
      kpiSummary.value = safeData(summaryRes, {})
      kpiDashboard.value = safeData(dashboardRes, {})
      kpiRevenue.value = safeData(revenueRes, {})
      kpiInventory.value = safeData(inventoryRes, {})
      kpiClients.value = safeData(clientsRes, {})
      kpiWarranty.value = safeData(warrantyRes, {})
      repairsTimeline.value = safeData(repairsTimelineRes, [])
      revenueTimeline.value = safeData(revenueTimelineRes, [])
      kpiTurnaround.value = safeData(turnaroundRes, {})
      kpiOverdue.value = safeData(overdueRes, {})
      kpiLeadConversion.value = safeData(leadConvRes, {})
      kpiTopModels.value = safeData(topModelsRes, [])
      kpiClientReturn.value = safeData(clientReturnRes, {})
    } catch (loadError) {
      error.value = extractErrorMessage(loadError)
    } finally {
      isLoading.value = false
    }
  }

  onMounted(load)

  return {
    isLoading,
    error,
    cards,
    stats,
    kpiSummary,
    kpiDashboard,
    kpiRevenue,
    kpiInventory,
    kpiClients,
    kpiWarranty,
    repairsTimeline,
    revenueTimeline,
    kpiTurnaround,
    kpiOverdue,
    kpiLeadConversion,
    kpiTopModels,
    kpiClientReturn,
    formatCurrency,
    load
  }
}
