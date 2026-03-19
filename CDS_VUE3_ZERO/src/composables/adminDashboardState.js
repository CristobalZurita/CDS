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

export function buildAdminDashboardAlerts({ kpiSummary = {}, kpiDashboard = {} } = {}) {
  const summaryAlerts = Array.isArray(kpiSummary?.alerts) ? kpiSummary.alerts : []
  const dashboardAlerts = Array.isArray(kpiDashboard?.alerts) ? kpiDashboard.alerts : []
  const source = summaryAlerts.length ? summaryAlerts : dashboardAlerts

  return source.map((alert, index) => ({
    key: alert.type || alert.message || `alert-${index}`,
    text: alert.message || alert.type || 'Alerta',
    count: asInt(alert.count, 0),
    tone: alert.severity || 'info'
  }))
}

export function resolveAdminDashboardPendingClaims({ kpiSummary = {}, kpiWarranty = {} } = {}) {
  if (kpiSummary?.pending_claims != null) {
    return asInt(kpiSummary.pending_claims, 0)
  }

  const total = asInt(kpiWarranty?.total_claims, 0)
  const approved = asInt(kpiWarranty?.approved_claims, 0)
  const rejected = asInt(kpiWarranty?.rejected_claims, 0)
  return Math.max(total - approved - rejected, 0)
}

export function buildAdminDashboardZoneCards({
  kpiSummary = {},
  kpiDashboard = {},
  kpiRevenue = {},
  kpiInventory = {},
  kpiClients = {},
  kpiWarranty = {},
  pendingClaims = 0
} = {}) {
  return [
    {
      key: 'work-orders',
      icon: '📋',
      title: 'Órdenes de Trabajo',
      description: 'Seguimiento operativo',
      metrics: [
        { key: 'total', value: asInt(kpiSummary?.total_repairs, kpiDashboard?.repairs), label: 'Totales' },
        { key: 'active', value: asInt(kpiSummary?.active_repairs, kpiDashboard?.active_repairs), label: 'Activas' },
        { key: 'month', value: asInt(kpiSummary?.repairs_this_month, kpiDashboard?.repairs_this_month), label: 'Este mes' },
        { key: 'completed', value: asInt(kpiDashboard?.completed_repairs, 0), label: 'Completadas' }
      ]
    },
    {
      key: 'finance',
      icon: '💰',
      title: 'Finanzas',
      description: 'Facturación y cobranza',
      metrics: [
        { key: 'invoiced', value: money(kpiSummary?.revenue?.total_invoiced, kpiRevenue?.total_invoiced), label: 'Facturado' },
        { key: 'month', value: money(kpiSummary?.revenue?.invoiced_this_month, kpiRevenue?.total_paid), label: 'Este mes' },
        { key: 'pending', value: money(kpiSummary?.revenue?.pending_collection, kpiRevenue?.total_pending), label: 'Pendiente', tone: 'warning' },
        { key: 'collection', value: percent(kpiRevenue?.collection_rate), label: 'Cobranza' }
      ]
    },
    {
      key: 'inventory',
      icon: '📦',
      title: 'Inventario',
      description: 'Stock y disponibilidad',
      metrics: [
        { key: 'items', value: asInt(kpiInventory?.total_items, kpiSummary?.total_items), label: 'Items' },
        { key: 'low-stock', value: asInt(kpiSummary?.low_stock_alerts, kpiInventory?.low_stock_items), label: 'Stock bajo', tone: 'warning' },
        { key: 'out-of-stock', value: asInt(kpiSummary?.out_of_stock, kpiInventory?.out_of_stock), label: 'Sin stock', tone: 'danger' },
        { key: 'value', value: moneyCompact(kpiSummary?.inventory_value, kpiInventory?.total_inventory_value), label: 'Valor' }
      ]
    },
    {
      key: 'clients',
      icon: '👥',
      title: 'Clientes',
      description: 'Base y garantías',
      metrics: [
        { key: 'clients', value: asInt(kpiSummary?.total_clients, kpiClients?.total_clients), label: 'Totales' },
        { key: 'new', value: asInt(kpiSummary?.new_clients_this_month, kpiClients?.new_this_month), label: 'Nuevos' },
        { key: 'warranties', value: asInt(kpiSummary?.active_warranties, kpiWarranty?.active_warranties), label: 'Garantías' },
        pendingClaims > 0
          ? { key: 'claims', value: pendingClaims, label: 'Reclamos', tone: 'warning' }
          : null
      ].filter(Boolean)
    }
  ]
}
