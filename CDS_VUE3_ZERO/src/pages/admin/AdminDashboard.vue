<template>
  <main class="admin-page">
    <header class="admin-header">
      <div>
        <h1>Admin Dashboard</h1>
        <p>Panel de control administrativo.</p>
      </div>
      <button class="btn-secondary" :disabled="isLoading" @click="loadDashboard">
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
        <h2>KPIs</h2>
        <ul>
          <li><span>Reparaciones totales</span><strong>{{ kpiSummary.total_repairs || 0 }}</strong></li>
          <li><span>Activas</span><strong>{{ kpiSummary.active_repairs || 0 }}</strong></li>
          <li><span>Ingresos mes</span><strong>{{ formatCurrency(kpiRevenue.current_month || 0) }}</strong></li>
        </ul>
      </article>

      <article class="panel-card">
        <h2>Accesos rapidos</h2>
        <div class="quick-links">
          <router-link to="/admin/stats" class="link-chip">Stats</router-link>
          <router-link to="/admin/categories" class="link-chip">Categorias</router-link>
          <router-link to="/admin/newsletter" class="link-chip">Newsletter</router-link>
          <router-link to="/admin/contact" class="link-chip">Contacto</router-link>
          <router-link to="/admin/appointments" class="link-chip">Citas</router-link>
          <router-link to="/admin/repairs" class="link-chip">Reparaciones</router-link>
        </div>
      </article>
    </section>

    <section class="panel-card">
      <h2>Ultimas reparaciones</h2>
      <div v-if="recentRepairs.length === 0" class="empty-state">Sin reparaciones recientes.</div>
      <div v-else class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>OT</th>
              <th>Cliente</th>
              <th>Instrumento</th>
              <th>Estado</th>
              <th>Costo</th>
              <th>Fecha</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="repair in recentRepairs" :key="repair.id">
              <td>{{ repair.id }}</td>
              <td>{{ repair.repair_number || '—' }}</td>
              <td>{{ repair.client_name || '—' }}</td>
              <td>{{ repair.instrument || '—' }}</td>
              <td>{{ repair.status_normalized || repair.status || '—' }}</td>
              <td>{{ formatCurrency(repair.total_cost || 0) }}</td>
              <td>{{ formatDate(repair.updated_at || repair.intake_date) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </main>
</template>

<script setup>
import { useAdminDashboardPage } from '@new/composables/useAdminDashboardPage'

const {
  isLoading,
  error,
  cards,
  kpiSummary,
  kpiRevenue,
  recentRepairs,
  formatDate,
  formatCurrency,
  loadDashboard
} = useAdminDashboardPage()
</script>

<style scoped>
.admin-page { padding: 1rem; display: grid; gap: 1rem; }
.admin-header, .stat-card, .panel-card { border: 1px solid color-mix(in srgb, var(--cds-light) 70%, white); border-radius: .9rem; background: var(--cds-white); }
.admin-header { padding: .9rem; display: flex; flex-wrap: wrap; gap: .75rem; justify-content: space-between; align-items: center; }
.admin-header h1 { margin: 0; font-size: var(--cds-text-3xl); }
.admin-header p { margin: .3rem 0 0; color: var(--cds-text-muted); }
.btn-secondary { min-height: 44px; padding: .65rem .9rem; border-radius: .55rem; border: 1px solid color-mix(in srgb, var(--cds-light) 65%, white); background: var(--cds-white); color: var(--cds-text-normal); font-size: var(--cds-text-base); }
.admin-error { margin: 0; border: 1px solid #f4c7c3; background: #fef3f2; color: #b42318; border-radius: .6rem; padding: .75rem; }
.cards-grid { display: grid; gap: .7rem; grid-template-columns: repeat(1,minmax(0,1fr)); }
.stat-card { padding: .8rem; display: grid; gap: .2rem; }
.stat-label { font-size: var(--cds-text-sm); color: var(--cds-text-muted); }
.stat-value { font-size: var(--cds-text-2xl); }
.panel-grid { display: grid; gap: .7rem; grid-template-columns: repeat(1,minmax(0,1fr)); }
.panel-card { padding: .9rem; }
.panel-card h2 { margin: 0 0 .5rem; font-size: var(--cds-text-xl); }
.panel-card ul { margin: 0; padding: 0; list-style: none; display: grid; gap: .35rem; }
.panel-card li { display: flex; justify-content: space-between; gap: .5rem; }
.quick-links { display: flex; flex-wrap: wrap; gap: .45rem; }
.link-chip { min-height: 40px; padding: .55rem .75rem; border-radius: .55rem; border: 1px solid color-mix(in srgb, var(--cds-light) 65%, white); text-decoration: none; color: var(--cds-text-normal); display: inline-flex; align-items: center; }
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
th, td { text-align: left; padding: .6rem; border-bottom: 1px solid color-mix(in srgb, var(--cds-light) 70%, white); }
th { font-size: var(--cds-text-sm); color: var(--cds-text-muted); }
.empty-state { border: 1px dashed color-mix(in srgb, var(--cds-light) 70%, white); border-radius: .7rem; padding: .9rem; }
@media (min-width: 760px) { .cards-grid { grid-template-columns: repeat(3,minmax(0,1fr)); } .panel-grid { grid-template-columns: repeat(2,minmax(0,1fr)); } }
</style>
