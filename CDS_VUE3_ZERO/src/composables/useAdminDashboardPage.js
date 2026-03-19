/**
 * useAdminDashboardPage
 *
 * Estado y carga de KPIs del dashboard administrativo.
 * Reutiliza los endpoints ya presentes en la page legacy, sin duplicarlos.
 */

import { computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import {
  buildAdminDashboardAlerts,
  buildAdminDashboardZoneCards,
  resolveAdminDashboardPendingClaims
} from '@/composables/adminDashboardState'
import { extractErrorMessage } from '@/services/api'
import {
  ADMIN_DASHBOARD_QUERY_KEY,
  fetchAdminDashboardSnapshot,
} from '@/services/adminDashboardService'

export function useAdminDashboardPage() {
  const dashboardQuery = useQuery({
    queryKey: ADMIN_DASHBOARD_QUERY_KEY,
    queryFn: fetchAdminDashboardSnapshot,
  })

  const isLoading = computed(() => dashboardQuery.isPending.value)
  const error = computed(() => {
    if (!dashboardQuery.error.value) return ''
    return extractErrorMessage(dashboardQuery.error.value)
  })

  const stats = computed(() => dashboardQuery.data.value?.stats || {})
  const kpiSummary = computed(() => dashboardQuery.data.value?.kpiSummary || {})
  const kpiDashboard = computed(() => dashboardQuery.data.value?.kpiDashboard || {})
  const kpiRevenue = computed(() => dashboardQuery.data.value?.kpiRevenue || {})
  const kpiInventory = computed(() => dashboardQuery.data.value?.kpiInventory || {})
  const kpiClients = computed(() => dashboardQuery.data.value?.kpiClients || {})
  const kpiWarranty = computed(() => dashboardQuery.data.value?.kpiWarranty || {})

  const normalizedAlerts = computed(() => {
    return buildAdminDashboardAlerts({
      kpiSummary: kpiSummary.value,
      kpiDashboard: kpiDashboard.value
    })
  })

  const pendingClaims = computed(() => {
    return resolveAdminDashboardPendingClaims({
      kpiSummary: kpiSummary.value,
      kpiWarranty: kpiWarranty.value
    })
  })

  const zoneCards = computed(() => {
    return buildAdminDashboardZoneCards({
      kpiSummary: kpiSummary.value,
      kpiDashboard: kpiDashboard.value,
      kpiRevenue: kpiRevenue.value,
      kpiInventory: kpiInventory.value,
      kpiClients: kpiClients.value,
      kpiWarranty: kpiWarranty.value,
      pendingClaims: pendingClaims.value
    })
  })
  
  async function loadDashboard() {
    await dashboardQuery.refetch()
  }

  return {
    isLoading,
    error,
    stats,
    zoneCards,
    normalizedAlerts,
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
