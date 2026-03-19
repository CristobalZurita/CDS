import api from '@/services/api'
import { pickSettledData } from '@/utils/api-helpers'
import { formatCurrency } from '@/utils/format'

function formatCompactThousands(value) {
  return '$' + (value / 1000).toFixed(0) + 'k'
}

export function createEmptyStatsBundle() {
  return {
    stats: {},
    kpiSummary: {},
    kpiDashboard: {},
    kpiRevenue: {},
    kpiInventory: {},
    kpiClients: {},
    kpiWarranty: {},
    repairsTimeline: [],
    revenueTimeline: [],
    technicianPerformance: [],
    kpiTurnaround: {},
    kpiOverdue: {},
    kpiLeadConversion: {},
    kpiTopModels: [],
    kpiClientReturn: {}
  }
}

export async function fetchStatsPageBundle() {
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
    techniciansRes,
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
    api.get('/analytics/technicians'),
    api.get('/analytics/kpis/turnaround'),
    api.get('/analytics/kpis/overdue'),
    api.get('/analytics/kpis/lead-conversion'),
    api.get('/analytics/kpis/top-models', { params: { limit: 8 } }),
    api.get('/analytics/kpis/client-return'),
  ])

  return {
    stats: pickSettledData(statsRes, {}),
    kpiSummary: pickSettledData(summaryRes, {}),
    kpiDashboard: pickSettledData(dashboardRes, {}),
    kpiRevenue: pickSettledData(revenueRes, {}),
    kpiInventory: pickSettledData(inventoryRes, {}),
    kpiClients: pickSettledData(clientsRes, {}),
    kpiWarranty: pickSettledData(warrantyRes, {}),
    repairsTimeline: pickSettledData(repairsTimelineRes, []),
    revenueTimeline: pickSettledData(revenueTimelineRes, []),
    technicianPerformance: pickSettledData(techniciansRes, []),
    kpiTurnaround: pickSettledData(turnaroundRes, {}),
    kpiOverdue: pickSettledData(overdueRes, {}),
    kpiLeadConversion: pickSettledData(leadConvRes, {}),
    kpiTopModels: pickSettledData(topModelsRes, []),
    kpiClientReturn: pickSettledData(clientReturnRes, {})
  }
}

export function buildStatsCards(stats) {
  const source = stats || {}
  return [
    { id: 'users', label: 'Usuarios', value: Number(source.users || 0) },
    { id: 'clients', label: 'Clientes', value: Number(source.clients || 0) },
    { id: 'repairs', label: 'Reparaciones', value: Number(source.repairs || 0) },
    { id: 'products', label: 'Productos', value: Number(source.products || 0) },
    { id: 'pending', label: 'Pendientes', value: Number(source.pending_repairs || 0) },
    { id: 'active', label: 'Activas', value: Number(source.active_repairs || 0) }
  ]
}

export function buildStatsSummaryPanels(bundle) {
  const {
    kpiSummary = {},
    kpiDashboard = {},
    kpiRevenue = {},
    kpiInventory = {},
    kpiClients = {},
    kpiWarranty = {},
    kpiTurnaround = {},
    kpiOverdue = {},
    kpiLeadConversion = {},
    kpiClientReturn = {}
  } = bundle || {}

  return [
    {
      key: 'summary',
      title: 'Resumen KPIs',
      items: [
        { label: 'Reparaciones totales', value: kpiSummary.total_repairs || 0 },
        { label: 'Activas', value: kpiSummary.active_repairs || 0 },
        { label: 'Este mes', value: kpiSummary.repairs_this_month || 0 }
      ]
    },
    {
      key: 'dashboard',
      title: 'Dashboard',
      items: [
        { label: 'Alertas', value: kpiDashboard.alerts_count || 0 },
        { label: 'Pendientes', value: kpiDashboard.pending_repairs || 0 },
        { label: 'Completadas', value: kpiDashboard.completed_repairs || 0 }
      ]
    },
    {
      key: 'revenue',
      title: 'Ingresos',
      items: [
        { label: 'Mes actual', value: formatCurrency(kpiRevenue.current_month || 0) },
        { label: 'Mes anterior', value: formatCurrency(kpiRevenue.previous_month || 0) },
        { label: 'Total anual', value: formatCurrency(kpiRevenue.year_total || 0) }
      ]
    },
    {
      key: 'inventory',
      title: 'Inventario',
      items: [
        { label: 'Productos', value: kpiInventory.total_products || 0 },
        { label: 'Stock bajo', value: kpiInventory.low_stock || 0 },
        { label: 'Sin stock', value: kpiInventory.out_of_stock || 0 }
      ]
    },
    {
      key: 'clients',
      title: 'Clientes',
      items: [
        { label: 'Total', value: kpiClients.total_clients || 0 },
        { label: 'Nuevos mes', value: kpiClients.new_clients_month || 0 },
        { label: 'Activos', value: kpiClients.active_clients || 0 }
      ]
    },
    {
      key: 'warranty',
      title: 'Garantias',
      items: [
        { label: 'Activas', value: kpiWarranty.active_warranties || 0 },
        { label: 'Vencen pronto', value: kpiWarranty.expiring_soon || 0 },
        { label: 'Vencidas', value: kpiWarranty.expired || 0 }
      ]
    },
    {
      key: 'turnaround',
      title: 'Tiempo de resolución OT',
      items: [
        { label: 'Promedio', value: kpiTurnaround.avg_days != null ? `${kpiTurnaround.avg_days} días` : '—' },
        { label: 'Mínimo', value: kpiTurnaround.min_days != null ? `${kpiTurnaround.min_days} días` : '—' },
        { label: 'Máximo', value: kpiTurnaround.max_days != null ? `${kpiTurnaround.max_days} días` : '—' }
      ]
    },
    {
      key: 'overdue',
      title: 'OTs vencidas',
      items: [
        { label: `Vencidas (+${kpiOverdue.threshold_days || 30}d)`, value: kpiOverdue.overdue_count || 0 },
        { label: 'Total activas', value: kpiOverdue.total_active || 0 },
        { label: '% vencidas', value: `${kpiOverdue.overdue_pct || 0}%` }
      ]
    },
    {
      key: 'lead-conversion',
      title: 'Conversión de leads',
      items: [
        { label: 'Total leads', value: kpiLeadConversion.total_leads || 0 },
        { label: 'Convertidos', value: kpiLeadConversion.converted || 0 },
        { label: 'Tasa conversión', value: `${kpiLeadConversion.conversion_rate || 0}%` }
      ]
    },
    {
      key: 'client-return',
      title: 'Retorno de clientes',
      items: [
        { label: 'Clientes recurrentes', value: kpiClientReturn.returning_clients || 0 },
        { label: 'Primera vez', value: kpiClientReturn.first_time_clients || 0 },
        { label: 'Tasa retorno', value: `${kpiClientReturn.return_rate || 0}%` }
      ]
    }
  ]
}

export function buildStatsChartPanels(bundle) {
  const repairsTimeline = Array.isArray(bundle?.repairsTimeline) ? bundle.repairsTimeline : []
  const revenueTimeline = Array.isArray(bundle?.revenueTimeline) ? bundle.revenueTimeline : []
  const technicianPerformance = Array.isArray(bundle?.technicianPerformance) ? bundle.technicianPerformance : []
  const topModels = Array.isArray(bundle?.kpiTopModels) ? bundle.kpiTopModels : []

  return [
    repairsTimeline.length > 0
      ? {
          key: 'repairs',
          title: 'OTs últimos 30 días',
          type: 'area',
          options: {
            chart: { toolbar: { show: false }, sparkline: { enabled: false } },
            colors: ['var(--cds-primary)', 'var(--cds-light-5)'],
            stroke: { curve: 'smooth', width: 2 },
            fill: { opacity: 0.15 },
            xaxis: {
              categories: repairsTimeline.map((entry) => entry.period),
              labels: { style: { fontSize: '11px' } }
            },
            yaxis: { labels: { style: { fontSize: '11px' } } },
            legend: { position: 'top' },
            tooltip: { x: { show: true } },
          },
          series: [
            { name: 'Creadas', data: repairsTimeline.map((entry) => entry.created) },
            { name: 'Completadas', data: repairsTimeline.map((entry) => entry.completed) },
          ]
        }
      : null,
    revenueTimeline.length > 0
      ? {
          key: 'revenue',
          title: 'Ingresos últimos 12 meses',
          type: 'bar',
          options: {
            chart: { toolbar: { show: false } },
            colors: ['var(--cds-primary)', 'var(--cds-light-5)'],
            plotOptions: { bar: { borderRadius: 4, columnWidth: '55%' } },
            xaxis: {
              categories: revenueTimeline.map((entry) => entry.month),
              labels: { style: { fontSize: '11px' } }
            },
            yaxis: {
              labels: {
                style: { fontSize: '11px' },
                formatter: (value) => formatCompactThousands(value)
              }
            },
            legend: { position: 'top' },
            tooltip: {
              y: {
                formatter: (value) => formatCurrency(value)
              }
            },
          },
          series: [
            { name: 'Facturado', data: revenueTimeline.map((entry) => entry.invoiced) },
            { name: 'Cobrado', data: revenueTimeline.map((entry) => entry.paid) },
          ]
        }
      : null,
    technicianPerformance.length > 0
      ? {
          key: 'technicians',
          title: 'Productividad por tecnico',
          type: 'bar',
          options: {
            chart: { toolbar: { show: false } },
            colors: ['var(--cds-primary)', 'var(--cds-light-5)'],
            plotOptions: { bar: { borderRadius: 4, horizontal: true, barHeight: '62%' } },
            xaxis: {
              labels: { style: { fontSize: '11px' } }
            },
            yaxis: {
              categories: technicianPerformance.map((entry) => entry.name),
              labels: { style: { fontSize: '11px' } }
            },
            legend: { position: 'top' },
            tooltip: {
              y: {
                formatter: (value, { seriesIndex }) => seriesIndex === 0 ? `${value} OTs` : `${value}%`
              }
            },
          },
          series: [
            { name: 'OTs asignadas', data: technicianPerformance.map((entry) => entry.total_repairs) },
            { name: '% completadas', data: technicianPerformance.map((entry) => entry.completion_rate) },
          ]
        }
      : null,
    topModels.length > 0
      ? {
          key: 'top-models',
          title: 'Top modelos reparados',
          type: 'bar',
          options: {
            chart: { toolbar: { show: false } },
            colors: ['var(--cds-primary)'],
            plotOptions: { bar: { horizontal: true, borderRadius: 4, barHeight: '65%' } },
            xaxis: { labels: { style: { fontSize: '11px' } } },
            yaxis: {
              categories: topModels.map((model) => model.model),
              labels: { style: { fontSize: '11px' } }
            },
            tooltip: { y: { formatter: (value) => `${value} OTs` } },
          },
          series: [
            { name: 'Reparaciones', data: topModels.map((model) => model.repair_count) },
          ]
        }
      : null,
  ].filter(Boolean)
}

export async function downloadRepairsExportCsv() {
  const response = await api.get('/analytics/repairs/export', {
    responseType: 'blob'
  })

  const blob = new Blob([response.data], { type: 'text/csv;charset=utf-8' })
  const blobUrl = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = blobUrl
  link.download = 'repairs_export.csv'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(blobUrl)
}
