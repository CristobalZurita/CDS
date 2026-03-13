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
        warrantyRes
      ] = await Promise.allSettled([
        api.get('/stats', { params: { extended: true } }),
        api.get('/analytics/kpis/summary'),
        api.get('/analytics/dashboard'),
        api.get('/analytics/revenue'),
        api.get('/analytics/inventory'),
        api.get('/analytics/clients'),
        api.get('/analytics/warranties')
      ])

      stats.value = safeData(statsRes, {})
      kpiSummary.value = safeData(summaryRes, {})
      kpiDashboard.value = safeData(dashboardRes, {})
      kpiRevenue.value = safeData(revenueRes, {})
      kpiInventory.value = safeData(inventoryRes, {})
      kpiClients.value = safeData(clientsRes, {})
      kpiWarranty.value = safeData(warrantyRes, {})
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
    formatCurrency,
    load
  }
}
