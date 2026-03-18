/**
 * useAdminDashboardPage
 *
 * Estado y carga de KPIs del dashboard administrativo.
 * Reutiliza los endpoints ya presentes en la page legacy, sin duplicarlos.
 */

import { computed, onMounted, ref } from 'vue'
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

  const normalizedAlerts = computed(() => {
    const summaryAlerts = Array.isArray(kpiSummary.value?.alerts) ? kpiSummary.value.alerts : []
    const dashboardAlerts = Array.isArray(kpiDashboard.value?.alerts) ? kpiDashboard.value.alerts : []
    const source = summaryAlerts.length ? summaryAlerts : dashboardAlerts

    return source.map((alert, index) => ({
      key: alert.type || alert.message || `alert-${index}`,
      text: alert.message || alert.type || 'Alerta',
      count: asInt(alert.count, 0),
      tone: alert.severity || 'info'
    }))
  })

  const pendingClaims = computed(() => {
    if (kpiSummary.value?.pending_claims != null) {
      return asInt(kpiSummary.value.pending_claims, 0)
    }
    const total = asInt(kpiWarranty.value?.total_claims, 0)
    const approved = asInt(kpiWarranty.value?.approved_claims, 0)
    const rejected = asInt(kpiWarranty.value?.rejected_claims, 0)
    return Math.max(total - approved - rejected, 0)
  })

  const zoneCards = computed(() => ([
    {
      key: 'work-orders',
      icon: '📋',
      title: 'Órdenes de Trabajo',
      description: 'Seguimiento operativo',
      metrics: [
        { key: 'total', value: asInt(kpiSummary.value?.total_repairs, kpiDashboard.value?.repairs), label: 'Totales' },
        { key: 'active', value: asInt(kpiSummary.value?.active_repairs, kpiDashboard.value?.active_repairs), label: 'Activas' },
        { key: 'month', value: asInt(kpiSummary.value?.repairs_this_month, kpiDashboard.value?.repairs_this_month), label: 'Este mes' },
        { key: 'completed', value: asInt(kpiDashboard.value?.completed_repairs, 0), label: 'Completadas' }
      ]
    },
    {
      key: 'finance',
      icon: '💰',
      title: 'Finanzas',
      description: 'Facturación y cobranza',
      metrics: [
        { key: 'invoiced', value: money(kpiSummary.value?.revenue?.total_invoiced, kpiRevenue.value?.total_invoiced), label: 'Facturado' },
        { key: 'month', value: money(kpiSummary.value?.revenue?.invoiced_this_month, kpiRevenue.value?.total_paid), label: 'Este mes' },
        { key: 'pending', value: money(kpiSummary.value?.revenue?.pending_collection, kpiRevenue.value?.total_pending), label: 'Pendiente', tone: 'warning' },
        { key: 'collection', value: percent(kpiRevenue.value?.collection_rate), label: 'Cobranza' }
      ]
    },
    {
      key: 'inventory',
      icon: '📦',
      title: 'Inventario',
      description: 'Stock y disponibilidad',
      metrics: [
        { key: 'items', value: asInt(kpiInventory.value?.total_items, kpiSummary.value?.total_items), label: 'Items' },
        { key: 'low-stock', value: asInt(kpiSummary.value?.low_stock_alerts, kpiInventory.value?.low_stock_items), label: 'Stock bajo', tone: 'warning' },
        { key: 'out-of-stock', value: asInt(kpiSummary.value?.out_of_stock, kpiInventory.value?.out_of_stock), label: 'Sin stock', tone: 'danger' },
        { key: 'value', value: moneyCompact(kpiSummary.value?.inventory_value, kpiInventory.value?.total_inventory_value), label: 'Valor' }
      ]
    },
    {
      key: 'clients',
      icon: '👥',
      title: 'Clientes',
      description: 'Base y garantías',
      metrics: [
        { key: 'clients', value: asInt(kpiSummary.value?.total_clients, kpiClients.value?.total_clients), label: 'Totales' },
        { key: 'new', value: asInt(kpiSummary.value?.new_clients_this_month, kpiClients.value?.new_this_month), label: 'Nuevos' },
        { key: 'warranties', value: asInt(kpiSummary.value?.active_warranties, kpiWarranty.value?.active_warranties), label: 'Garantías' },
        pendingClaims.value > 0
          ? { key: 'claims', value: pendingClaims.value, label: 'Reclamos', tone: 'warning' }
          : null
      ].filter(Boolean)
    }
  ]))
  
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

  function asInt(value, fallback = 0) {
    const raw = value != null ? value : fallback
    const normalized = Number(raw)
    if (!Number.isFinite(normalized)) return 0
    return Math.round(normalized)
  }

  function money(value, fallback = 0) {
    const raw = value != null ? value : fallback
    const normalized = Number(raw)
    const amount = Number.isFinite(normalized) ? normalized : 0
    return new Intl.NumberFormat('es-CL', {
      style: 'currency',
      currency: 'CLP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount)
  }

  function moneyCompact(value, fallback = 0) {
    const raw = value != null ? value : fallback
    const normalized = Number(raw)
    const amount = Number.isFinite(normalized) ? normalized : 0
    if (amount >= 1000000) {
      return '$' + (amount / 1000000).toFixed(1) + 'M'
    }
    if (amount >= 1000) {
      return '$' + (amount / 1000).toFixed(0) + 'k'
    }
    return money(value, fallback)
  }

  function percent(value) {
    const normalized = Number(value)
    const amount = Number.isFinite(normalized) ? normalized : 0
    return `${amount.toFixed(0)}%`
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
