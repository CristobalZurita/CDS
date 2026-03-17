/**
 * useAdminDashboardPage
 *
 * Estado y carga de KPIs del dashboard administrativo.
 * Reutiliza los endpoints ya presentes en la page legacy, sin duplicarlos.
 */

import { ref, onMounted } from 'vue'
import api, { extractErrorMessage } from '@/services/api'
import { pickSettledData } from '@/utils/api-helpers'

export function useAdminDashboardPage() {
  const isLoading = ref(false)
  const error = ref('')
  
  // Datos de stats (contadores simples)
  const stats = ref({})
  
  // KPIs detallados
  const kpiSummary = ref({})
  const kpiDashboard = ref({})
  const kpiRevenue = ref({})
  const kpiInventory = ref({})
  const kpiClients = ref({})
  const kpiWarranty = ref({})
  
  // Cards del dashboard
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

      stats.value = pickSettledData(statsRes, {})
      kpiSummary.value = pickSettledData(summaryRes, {})
      kpiDashboard.value = pickSettledData(dashboardRes, {})
      kpiRevenue.value = pickSettledData(revenueRes, {})
      kpiInventory.value = pickSettledData(inventoryRes, {})
      kpiClients.value = pickSettledData(clientsRes, {})
      kpiWarranty.value = pickSettledData(warrantyRes, {})
    } catch (err) {
      error.value = extractErrorMessage(err)
    } finally {
      isLoading.value = false
    }
  }

  onMounted(loadDashboard)

  return {
    isLoading,
    error,
    stats,
    kpiSummary,
    kpiDashboard,
    kpiRevenue,
    kpiInventory,
    kpiClients,
    kpiWarranty,
    loadDashboard,
  }
}

export default useAdminDashboardPage
