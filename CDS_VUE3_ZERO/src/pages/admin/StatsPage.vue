<template>
  <main class="admin-page">
    <header class="admin-header">
      <div>
        <h1>Estadisticas</h1>
        <p>Indicadores y metricas del sistema.</p>
      </div>
      <button class="btn-secondary" :disabled="isLoading" @click="load">
        {{ isLoading ? 'Actualizando...' : 'Actualizar' }}
      </button>
    </header>

    <p v-if="error" class="admin-error">{{ error }}</p>

    <section class="cards-grid">
      <article v-for="card in cards" :key="card.id" class="stat-card">
        <span class="stat-label">{{ card.label }}</span>
        <strong class="stat-value">{{ card.value }}</strong>
      </article>
    </section>

    <section class="panel-grid">
      <article class="panel-card">
        <h2>Resumen KPIs</h2>
        <ul>
          <li><span>Reparaciones totales</span><strong>{{ kpiSummary.total_repairs || 0 }}</strong></li>
          <li><span>Activas</span><strong>{{ kpiSummary.active_repairs || 0 }}</strong></li>
          <li><span>Este mes</span><strong>{{ kpiSummary.repairs_this_month || 0 }}</strong></li>
        </ul>
      </article>

      <article class="panel-card">
        <h2>Dashboard</h2>
        <ul>
          <li><span>Alertas</span><strong>{{ kpiDashboard.alerts_count || 0 }}</strong></li>
          <li><span>Pendientes</span><strong>{{ kpiDashboard.pending_repairs || 0 }}</strong></li>
          <li><span>Completadas</span><strong>{{ kpiDashboard.completed_repairs || 0 }}</strong></li>
        </ul>
      </article>

      <article class="panel-card">
        <h2>Ingresos</h2>
        <ul>
          <li><span>Mes actual</span><strong>{{ formatCurrency(kpiRevenue.current_month || 0) }}</strong></li>
          <li><span>Mes anterior</span><strong>{{ formatCurrency(kpiRevenue.previous_month || 0) }}</strong></li>
          <li><span>Total anual</span><strong>{{ formatCurrency(kpiRevenue.year_total || 0) }}</strong></li>
        </ul>
      </article>

      <article class="panel-card">
        <h2>Inventario</h2>
        <ul>
          <li><span>Productos</span><strong>{{ kpiInventory.total_products || 0 }}</strong></li>
          <li><span>Stock bajo</span><strong>{{ kpiInventory.low_stock || 0 }}</strong></li>
          <li><span>Sin stock</span><strong>{{ kpiInventory.out_of_stock || 0 }}</strong></li>
        </ul>
      </article>

      <article class="panel-card">
        <h2>Clientes</h2>
        <ul>
          <li><span>Total</span><strong>{{ kpiClients.total_clients || 0 }}</strong></li>
          <li><span>Nuevos mes</span><strong>{{ kpiClients.new_clients_month || 0 }}</strong></li>
          <li><span>Activos</span><strong>{{ kpiClients.active_clients || 0 }}</strong></li>
        </ul>
      </article>

      <article class="panel-card">
        <h2>Garantias</h2>
        <ul>
          <li><span>Activas</span><strong>{{ kpiWarranty.active_warranties || 0 }}</strong></li>
          <li><span>Vencen pronto</span><strong>{{ kpiWarranty.expiring_soon || 0 }}</strong></li>
          <li><span>Vencidas</span><strong>{{ kpiWarranty.expired || 0 }}</strong></li>
        </ul>
      </article>

      <!-- KPIs de taller -->
      <article class="panel-card">
        <h2>Tiempo de resolución OT</h2>
        <ul>
          <li><span>Promedio</span><strong>{{ kpiTurnaround.avg_days != null ? kpiTurnaround.avg_days + ' días' : '—' }}</strong></li>
          <li><span>Mínimo</span><strong>{{ kpiTurnaround.min_days != null ? kpiTurnaround.min_days + ' días' : '—' }}</strong></li>
          <li><span>Máximo</span><strong>{{ kpiTurnaround.max_days != null ? kpiTurnaround.max_days + ' días' : '—' }}</strong></li>
        </ul>
      </article>

      <article class="panel-card">
        <h2>OTs vencidas</h2>
        <ul>
          <li><span>Vencidas (+{{ kpiOverdue.threshold_days || 30 }}d)</span><strong>{{ kpiOverdue.overdue_count || 0 }}</strong></li>
          <li><span>Total activas</span><strong>{{ kpiOverdue.total_active || 0 }}</strong></li>
          <li><span>% vencidas</span><strong>{{ kpiOverdue.overdue_pct || 0 }}%</strong></li>
        </ul>
      </article>

      <article class="panel-card">
        <h2>Conversión de leads</h2>
        <ul>
          <li><span>Total leads</span><strong>{{ kpiLeadConversion.total_leads || 0 }}</strong></li>
          <li><span>Convertidos</span><strong>{{ kpiLeadConversion.converted || 0 }}</strong></li>
          <li><span>Tasa conversión</span><strong>{{ kpiLeadConversion.conversion_rate || 0 }}%</strong></li>
        </ul>
      </article>

      <article class="panel-card">
        <h2>Retorno de clientes</h2>
        <ul>
          <li><span>Clientes recurrentes</span><strong>{{ kpiClientReturn.returning_clients || 0 }}</strong></li>
          <li><span>Primera vez</span><strong>{{ kpiClientReturn.first_time_clients || 0 }}</strong></li>
          <li><span>Tasa retorno</span><strong>{{ kpiClientReturn.return_rate || 0 }}%</strong></li>
        </ul>
      </article>
    </section>

    <!-- Gráficos -->
    <section class="charts-grid">
      <article class="panel-card chart-card" v-if="repairsTimeline.length > 0">
        <h2>OTs últimos 30 días</h2>
        <VueApexCharts
          type="area"
          height="220"
          :options="repairsChartOptions"
          :series="repairsChartSeries"
        />
      </article>

      <article class="panel-card chart-card" v-if="revenueTimeline.length > 0">
        <h2>Ingresos últimos 12 meses</h2>
        <VueApexCharts
          type="bar"
          height="220"
          :options="revenueChartOptions"
          :series="revenueChartSeries"
        />
      </article>

      <article class="panel-card chart-card" v-if="kpiTopModels.length > 0">
        <h2>Top modelos reparados</h2>
        <VueApexCharts
          type="bar"
          height="220"
          :options="topModelsChartOptions"
          :series="topModelsChartSeries"
        />
      </article>
    </section>
  </main>
</template>

<script setup>
import { computed } from 'vue'
import VueApexCharts from 'vue3-apexcharts'
import { useStatsPage } from '@/composables/useStatsPage'

const {
  isLoading,
  error,
  cards,
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
} = useStatsPage()

// ── Chart: OTs timeline (area) ───────────────────────────────────────────────
const repairsChartOptions = computed(() => ({
  chart: { toolbar: { show: false }, sparkline: { enabled: false } },
  colors: ['var(--cds-primary)', 'var(--cds-light-5)'],
  stroke: { curve: 'smooth', width: 2 },
  fill: { opacity: 0.15 },
  xaxis: {
    categories: repairsTimeline.value.map(d => d.period),
    labels: { style: { fontSize: '11px' } }
  },
  yaxis: { labels: { style: { fontSize: '11px' } } },
  legend: { position: 'top' },
  tooltip: { x: { show: true } },
}))

const repairsChartSeries = computed(() => [
  { name: 'Creadas', data: repairsTimeline.value.map(d => d.created) },
  { name: 'Completadas', data: repairsTimeline.value.map(d => d.completed) },
])

// ── Chart: Revenue timeline (bar) ────────────────────────────────────────────
const revenueChartOptions = computed(() => ({
  chart: { toolbar: { show: false } },
  colors: ['var(--cds-primary)', 'var(--cds-light-5)'],
  plotOptions: { bar: { borderRadius: 4, columnWidth: '55%' } },
  xaxis: {
    categories: revenueTimeline.value.map(d => d.month),
    labels: { style: { fontSize: '11px' } }
  },
  yaxis: {
    labels: {
      style: { fontSize: '11px' },
      formatter: v => '$' + (v / 1000).toFixed(0) + 'k'
    }
  },
  legend: { position: 'top' },
  tooltip: {
    y: { formatter: v => new Intl.NumberFormat('es-CL', { style: 'currency', currency: 'CLP', minimumFractionDigits: 0 }).format(v) }
  },
}))

const revenueChartSeries = computed(() => [
  { name: 'Facturado', data: revenueTimeline.value.map(d => d.invoiced) },
  { name: 'Cobrado', data: revenueTimeline.value.map(d => d.paid) },
])

// ── Chart: Top modelos (bar horizontal) ──────────────────────────────────────
const topModelsChartOptions = computed(() => ({
  chart: { toolbar: { show: false } },
  colors: ['var(--cds-primary)'],
  plotOptions: { bar: { horizontal: true, borderRadius: 4, barHeight: '65%' } },
  xaxis: { labels: { style: { fontSize: '11px' } } },
  yaxis: {
    categories: kpiTopModels.value.map(m => m.model),
    labels: { style: { fontSize: '11px' } }
  },
  tooltip: { y: { formatter: v => v + ' OTs' } },
}))

const topModelsChartSeries = computed(() => [
  { name: 'Reparaciones', data: kpiTopModels.value.map(m => m.repair_count) },
])
</script>

<style scoped src="./commonAdminPage.css"></style>
<style scoped>
.stat-label { font-size: var(--cds-text-sm); color: var(--cds-text-muted); }
.stat-value { font-size: var(--cds-text-2xl); }
.panel-card h2 { margin: 0 0 .45rem; }
.panel-card ul { margin: 0; padding: 0; list-style: none; display: grid; gap: .35rem; }
.panel-card li { display: flex; justify-content: space-between; gap: .55rem; }
.charts-grid { display: grid; gap: .7rem; grid-template-columns: repeat(1,minmax(0,1fr)); margin-top: .7rem; }
.chart-card { overflow: hidden; }
@media (min-width: 760px) { .cards-grid { grid-template-columns: repeat(3,minmax(0,1fr)); } .panel-grid { grid-template-columns: repeat(2,minmax(0,1fr)); } .charts-grid { grid-template-columns: repeat(2,minmax(0,1fr)); } }
</style>
