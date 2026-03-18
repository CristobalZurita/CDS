import { computed, onMounted, ref } from 'vue'
import api, { extractErrorMessage } from '@/services/api'
import { pickSettledData } from '@/utils/api-helpers'
import { formatCurrency } from '@/utils/format'

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

  const summaryPanels = computed(() => ([
    {
      key: 'summary',
      title: 'Resumen KPIs',
      items: [
        { label: 'Reparaciones totales', value: kpiSummary.value.total_repairs || 0 },
        { label: 'Activas', value: kpiSummary.value.active_repairs || 0 },
        { label: 'Este mes', value: kpiSummary.value.repairs_this_month || 0 }
      ]
    },
    {
      key: 'dashboard',
      title: 'Dashboard',
      items: [
        { label: 'Alertas', value: kpiDashboard.value.alerts_count || 0 },
        { label: 'Pendientes', value: kpiDashboard.value.pending_repairs || 0 },
        { label: 'Completadas', value: kpiDashboard.value.completed_repairs || 0 }
      ]
    },
    {
      key: 'revenue',
      title: 'Ingresos',
      items: [
        { label: 'Mes actual', value: formatCurrency(kpiRevenue.value.current_month || 0) },
        { label: 'Mes anterior', value: formatCurrency(kpiRevenue.value.previous_month || 0) },
        { label: 'Total anual', value: formatCurrency(kpiRevenue.value.year_total || 0) }
      ]
    },
    {
      key: 'inventory',
      title: 'Inventario',
      items: [
        { label: 'Productos', value: kpiInventory.value.total_products || 0 },
        { label: 'Stock bajo', value: kpiInventory.value.low_stock || 0 },
        { label: 'Sin stock', value: kpiInventory.value.out_of_stock || 0 }
      ]
    },
    {
      key: 'clients',
      title: 'Clientes',
      items: [
        { label: 'Total', value: kpiClients.value.total_clients || 0 },
        { label: 'Nuevos mes', value: kpiClients.value.new_clients_month || 0 },
        { label: 'Activos', value: kpiClients.value.active_clients || 0 }
      ]
    },
    {
      key: 'warranty',
      title: 'Garantias',
      items: [
        { label: 'Activas', value: kpiWarranty.value.active_warranties || 0 },
        { label: 'Vencen pronto', value: kpiWarranty.value.expiring_soon || 0 },
        { label: 'Vencidas', value: kpiWarranty.value.expired || 0 }
      ]
    },
    {
      key: 'turnaround',
      title: 'Tiempo de resolución OT',
      items: [
        { label: 'Promedio', value: kpiTurnaround.value.avg_days != null ? `${kpiTurnaround.value.avg_days} días` : '—' },
        { label: 'Mínimo', value: kpiTurnaround.value.min_days != null ? `${kpiTurnaround.value.min_days} días` : '—' },
        { label: 'Máximo', value: kpiTurnaround.value.max_days != null ? `${kpiTurnaround.value.max_days} días` : '—' }
      ]
    },
    {
      key: 'overdue',
      title: 'OTs vencidas',
      items: [
        { label: `Vencidas (+${kpiOverdue.value.threshold_days || 30}d)`, value: kpiOverdue.value.overdue_count || 0 },
        { label: 'Total activas', value: kpiOverdue.value.total_active || 0 },
        { label: '% vencidas', value: `${kpiOverdue.value.overdue_pct || 0}%` }
      ]
    },
    {
      key: 'lead-conversion',
      title: 'Conversión de leads',
      items: [
        { label: 'Total leads', value: kpiLeadConversion.value.total_leads || 0 },
        { label: 'Convertidos', value: kpiLeadConversion.value.converted || 0 },
        { label: 'Tasa conversión', value: `${kpiLeadConversion.value.conversion_rate || 0}%` }
      ]
    },
    {
      key: 'client-return',
      title: 'Retorno de clientes',
      items: [
        { label: 'Clientes recurrentes', value: kpiClientReturn.value.returning_clients || 0 },
        { label: 'Primera vez', value: kpiClientReturn.value.first_time_clients || 0 },
        { label: 'Tasa retorno', value: `${kpiClientReturn.value.return_rate || 0}%` }
      ]
    }
  ]))

  const repairsChartOptions = computed(() => ({
    chart: { toolbar: { show: false }, sparkline: { enabled: false } },
    colors: ['var(--cds-primary)', 'var(--cds-light-5)'],
    stroke: { curve: 'smooth', width: 2 },
    fill: { opacity: 0.15 },
    xaxis: {
      categories: repairsTimeline.value.map((entry) => entry.period),
      labels: { style: { fontSize: '11px' } }
    },
    yaxis: { labels: { style: { fontSize: '11px' } } },
    legend: { position: 'top' },
    tooltip: { x: { show: true } },
  }))

  const repairsChartSeries = computed(() => [
    { name: 'Creadas', data: repairsTimeline.value.map((entry) => entry.created) },
    { name: 'Completadas', data: repairsTimeline.value.map((entry) => entry.completed) },
  ])

  const revenueChartOptions = computed(() => ({
    chart: { toolbar: { show: false } },
    colors: ['var(--cds-primary)', 'var(--cds-light-5)'],
    plotOptions: { bar: { borderRadius: 4, columnWidth: '55%' } },
    xaxis: {
      categories: revenueTimeline.value.map((entry) => entry.month),
      labels: { style: { fontSize: '11px' } }
    },
    yaxis: {
      labels: {
        style: { fontSize: '11px' },
        formatter: (value) => '$' + (value / 1000).toFixed(0) + 'k'
      }
    },
    legend: { position: 'top' },
    tooltip: {
      y: {
        formatter: (value) => new Intl.NumberFormat('es-CL', {
          style: 'currency',
          currency: 'CLP',
          minimumFractionDigits: 0
        }).format(value)
      }
    },
  }))

  const revenueChartSeries = computed(() => [
    { name: 'Facturado', data: revenueTimeline.value.map((entry) => entry.invoiced) },
    { name: 'Cobrado', data: revenueTimeline.value.map((entry) => entry.paid) },
  ])

  const topModelsChartOptions = computed(() => ({
    chart: { toolbar: { show: false } },
    colors: ['var(--cds-primary)'],
    plotOptions: { bar: { horizontal: true, borderRadius: 4, barHeight: '65%' } },
    xaxis: { labels: { style: { fontSize: '11px' } } },
    yaxis: {
      categories: kpiTopModels.value.map((model) => model.model),
      labels: { style: { fontSize: '11px' } }
    },
    tooltip: { y: { formatter: (value) => `${value} OTs` } },
  }))

  const topModelsChartSeries = computed(() => [
    { name: 'Reparaciones', data: kpiTopModels.value.map((model) => model.repair_count) },
  ])

  const chartPanels = computed(() => ([
    repairsTimeline.value.length > 0
      ? {
          key: 'repairs',
          title: 'OTs últimos 30 días',
          type: 'area',
          options: repairsChartOptions.value,
          series: repairsChartSeries.value
        }
      : null,
    revenueTimeline.value.length > 0
      ? {
          key: 'revenue',
          title: 'Ingresos últimos 12 meses',
          type: 'bar',
          options: revenueChartOptions.value,
          series: revenueChartSeries.value
        }
      : null,
    kpiTopModels.value.length > 0
      ? {
          key: 'top-models',
          title: 'Top modelos reparados',
          type: 'bar',
          options: topModelsChartOptions.value,
          series: topModelsChartSeries.value
        }
      : null,
  ].filter(Boolean)))

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

      stats.value = pickSettledData(statsRes, {})
      kpiSummary.value = pickSettledData(summaryRes, {})
      kpiDashboard.value = pickSettledData(dashboardRes, {})
      kpiRevenue.value = pickSettledData(revenueRes, {})
      kpiInventory.value = pickSettledData(inventoryRes, {})
      kpiClients.value = pickSettledData(clientsRes, {})
      kpiWarranty.value = pickSettledData(warrantyRes, {})
      repairsTimeline.value = pickSettledData(repairsTimelineRes, [])
      revenueTimeline.value = pickSettledData(revenueTimelineRes, [])
      kpiTurnaround.value = pickSettledData(turnaroundRes, {})
      kpiOverdue.value = pickSettledData(overdueRes, {})
      kpiLeadConversion.value = pickSettledData(leadConvRes, {})
      kpiTopModels.value = pickSettledData(topModelsRes, [])
      kpiClientReturn.value = pickSettledData(clientReturnRes, {})
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
    summaryPanels,
    chartPanels,
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
