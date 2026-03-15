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
    </section>
  </main>
</template>

<script setup>
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
  formatCurrency,
  load
} = useStatsPage()
</script>

<style scoped src="./commonAdminPage.css"></style>
<style scoped>
.stat-card { border: 1px solid color-mix(in srgb, var(--cds-light) 70%, white); border-radius: .9rem; background: var(--cds-white); padding: .8rem; display: grid; gap: .2rem; }
.stat-label { font-size: var(--cds-text-sm); color: var(--cds-text-muted); }
.stat-value { font-size: var(--cds-text-2xl); }
.cards-grid { display: grid; gap: .7rem; grid-template-columns: repeat(1,minmax(0,1fr)); }
.panel-grid { display: grid; gap: .7rem; grid-template-columns: repeat(1,minmax(0,1fr)); }
.panel-card h2 { margin: 0 0 .45rem; }
.panel-card ul { margin: 0; padding: 0; list-style: none; display: grid; gap: .35rem; }
.panel-card li { display: flex; justify-content: space-between; gap: .55rem; }
@media (min-width: 760px) { .cards-grid { grid-template-columns: repeat(3,minmax(0,1fr)); } .panel-grid { grid-template-columns: repeat(2,minmax(0,1fr)); } }
</style>
