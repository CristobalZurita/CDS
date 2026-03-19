import api from '@/services/api'
import { pickSettledData } from '@/utils/api-helpers'

export const ADMIN_DASHBOARD_QUERY_KEY = ['admin', 'dashboard']

export async function fetchAdminDashboardSnapshot() {
  const settled = await Promise.allSettled([
    api.get('/stats', { params: { extended: true } }),
    api.get('/analytics/kpis/summary'),
    api.get('/analytics/dashboard'),
    api.get('/analytics/revenue'),
    api.get('/analytics/inventory'),
    api.get('/analytics/clients'),
    api.get('/analytics/warranties'),
  ])

  const firstRejected = settled.find((entry) => entry.status === 'rejected')
  const successCount = settled.filter((entry) => entry.status === 'fulfilled').length

  if (!successCount && firstRejected?.reason) {
    throw firstRejected.reason
  }

  const [
    statsRes,
    summaryRes,
    dashboardRes,
    revenueRes,
    inventoryRes,
    clientsRes,
    warrantyRes,
  ] = settled

  return {
    stats: pickSettledData(statsRes, {}),
    kpiSummary: pickSettledData(summaryRes, {}),
    kpiDashboard: pickSettledData(dashboardRes, {}),
    kpiRevenue: pickSettledData(revenueRes, {}),
    kpiInventory: pickSettledData(inventoryRes, {}),
    kpiClients: pickSettledData(clientsRes, {}),
    kpiWarranty: pickSettledData(warrantyRes, {}),
  }
}
