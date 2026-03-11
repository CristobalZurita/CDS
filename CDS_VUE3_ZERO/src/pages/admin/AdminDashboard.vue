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

    <!-- Stats Cards -->
    <section class="stats-grid">
      <article class="stat-card">
        <span class="stat-label">Usuarios</span>
        <strong class="stat-value">{{ stats.users || 0 }}</strong>
      </article>
      <article class="stat-card">
        <span class="stat-label">Clientes</span>
        <strong class="stat-value">{{ stats.clients || 0 }}</strong>
      </article>
      <article class="stat-card">
        <span class="stat-label">Reparaciones</span>
        <strong class="stat-value">{{ stats.repairs || 0 }}</strong>
      </article>
    </section>

    <!-- KPI Zones -->
    <section class="kpi-grid">
      <!-- KPIs Reparaciones -->
      <article class="kpi-card">
        <h3>Reparaciones</h3>
        <ul>
          <li><span>Total</span><strong>{{ kpiSummary.total_repairs || 0 }}</strong></li>
          <li><span>Activas</span><strong>{{ kpiSummary.active_repairs || 0 }}</strong></li>
          <li><span>Este mes</span><strong>{{ kpiSummary.repairs_this_month || 0 }}</strong></li>
        </ul>
      </article>

      <!-- KPIs Clientes -->
      <article class="kpi-card">
        <h3>Clientes</h3>
        <ul>
          <li><span>Total</span><strong>{{ kpiSummary.total_clients || 0 }}</strong></li>
          <li><span>Nuevos este mes</span><strong>{{ kpiSummary.new_clients_this_month || 0 }}</strong></li>
        </ul>
      </article>

      <!-- KPIs Ingresos -->
      <article class="kpi-card">
        <h3>Ingresos</h3>
        <ul>
          <li><span>Mes actual</span><strong>{{ formatCurrency(kpiRevenue.current_month || 0) }}</strong></li>
          <li><span>Mes anterior</span><strong>{{ formatCurrency(kpiRevenue.previous_month || 0) }}</strong></li>
        </ul>
      </article>

      <!-- KPIs Inventario -->
      <article class="kpi-card">
        <h3>Inventario</h3>
        <ul>
          <li><span>Stock bajo</span><strong :class="{ warning: (kpiSummary.low_stock_alerts || 0) > 0 }">{{ kpiSummary.low_stock_alerts || 0 }}</strong></li>
          <li><span>Sin stock</span><strong :class="{ danger: (kpiSummary.out_of_stock || 0) > 0 }">{{ kpiSummary.out_of_stock || 0 }}</strong></li>
          <li><span>Valor total</span><strong>{{ formatCurrency(kpiSummary.inventory_value || 0) }}</strong></li>
        </ul>
      </article>
    </section>

    <!-- Alertas -->
    <section v-if="kpiSummary.alerts && kpiSummary.alerts.length > 0" class="alerts-section">
      <h3>⚠️ Alertas del sistema</h3>
      <div class="alerts-list">
        <div 
          v-for="alert in kpiSummary.alerts" 
          :key="alert.id"
          class="alert-item"
          :class="alert.severity || 'warning'"
        >
          <span class="alert-message">{{ alert.message }}</span>
          <span class="alert-time">{{ formatDate(alert.created_at) }}</span>
        </div>
      </div>
    </section>

    <!-- Accesos rápidos -->
    <section class="panel-grid">
      <article class="panel-card">
        <h2>Accesos rápidos</h2>
        <div class="quick-links">
          <router-link to="/admin/stats" class="link-chip">Stats</router-link>
          <router-link to="/admin/quotes" class="link-chip">Cotizaciones</router-link>
          <router-link to="/admin/intake" class="link-chip link-highlight">+ Nuevo Ingreso</router-link>
          <router-link to="/admin/repairs" class="link-chip">Reparaciones</router-link>
          <router-link to="/admin/clients" class="link-chip">Clientes</router-link>
          <router-link to="/admin/inventory" class="link-chip">Inventario</router-link>
          <router-link to="/admin/categories" class="link-chip">Categorías</router-link>
          <router-link to="/admin/wizards" class="link-chip">Wizards</router-link>
        </div>
      </article>
    </section>

    <!-- Últimas reparaciones -->
    <section class="panel-card">
      <h2>Últimas reparaciones</h2>
      <div v-if="recentRepairs.length === 0" class="empty-state">Sin reparaciones recientes.</div>
      <div v-else class="table-wrap">
        <table>
          <thead>
            <tr>
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
              <td>
                <router-link :to="{ name: 'admin-repair-detail', params: { id: repair.id } }" class="link">
                  {{ repair.repair_code || repair.repair_number || `#${repair.id}` }}
                </router-link>
              </td>
              <td>{{ repair.client_name || '—' }}</td>
              <td>{{ repair.device_model || repair.instrument || '—' }}</td>
              <td>
                <span class="status-badge" :class="repair.status || 'pending'">
                  {{ repair.status || 'pending' }}
                </span>
              </td>
              <td>{{ formatCurrency(repair.total_cost || 0) }}</td>
              <td>{{ formatDate(repair.created_at || repair.intake_date) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </main>
</template>

<script setup>
import { useAdminDashboardPage } from '@/composables/useAdminDashboardPage'

const {
  isLoading,
  error,
  stats,
  kpiSummary,
  kpiRevenue,
  recentRepairs,
  loadDashboard,
  formatDate,
  formatCurrency
} = useAdminDashboardPage()
</script>

<style scoped>
.admin-page { 
  padding: 1rem; 
  display: grid; 
  gap: 1rem; 
}

.admin-header, .panel-card, .stat-card, .kpi-card { 
  border: 1px solid color-mix(in srgb, var(--cds-light) 70%, white); 
  border-radius: .9rem; 
  background: var(--cds-white); 
}

.admin-header { 
  padding: .9rem; 
  display: flex; 
  flex-wrap: wrap; 
  gap: .75rem; 
  justify-content: space-between; 
  align-items: center; 
}

.admin-header h1 { 
  margin: 0; 
  font-size: var(--cds-text-3xl); 
}

.admin-header p { 
  margin: .3rem 0 0; 
  color: var(--cds-text-muted); 
}

.btn-secondary { 
  min-height: 44px; 
  padding: .65rem .9rem; 
  border-radius: .55rem; 
  border: 1px solid color-mix(in srgb, var(--cds-light) 65%, white); 
  background: var(--cds-white); 
  color: var(--cds-text-normal); 
  font-size: var(--cds-text-base);
  cursor: pointer;
}

.btn-secondary:hover {
  border-color: var(--cds-primary);
  color: var(--cds-primary);
}

.admin-error { 
  margin: 0; 
  border: 1px solid #f4c7c3; 
  background: #fef3f2; 
  color: #b42318; 
  border-radius: .6rem; 
  padding: .75rem; 
}

/* Stats Grid */
.stats-grid { 
  display: grid; 
  gap: .7rem; 
  grid-template-columns: repeat(1, minmax(0, 1fr)); 
}

.stat-card { 
  padding: .8rem; 
  display: grid; 
  gap: .2rem; 
}

.stat-label { 
  font-size: var(--cds-text-sm); 
  color: var(--cds-text-muted); 
}

.stat-value { 
  font-size: var(--cds-text-2xl);
  color: var(--cds-text-normal);
}

/* KPI Grid */
.kpi-grid {
  display: grid;
  gap: .7rem;
  grid-template-columns: repeat(1, minmax(0, 1fr));
}

.kpi-card {
  padding: .9rem;
}

.kpi-card h3 {
  margin: 0 0 .5rem;
  font-size: var(--cds-text-lg);
  color: var(--cds-text-normal);
}

.kpi-card ul {
  margin: 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: .35rem;
}

.kpi-card li {
  display: flex;
  justify-content: space-between;
  gap: .5rem;
  font-size: var(--cds-text-sm);
}

.kpi-card li span:first-child {
  color: var(--cds-text-muted);
}

.kpi-card li strong {
  color: var(--cds-text-normal);
}

.kpi-card li strong.warning {
  color: var(--cds-warning);
}

.kpi-card li strong.danger {
  color: var(--cds-danger);
}

/* Alerts */
.alerts-section {
  background: #fef9c3;
  border: 1px solid #fcd34d;
  border-radius: .9rem;
  padding: .9rem;
}

.alerts-section h3 {
  margin: 0 0 .5rem;
  font-size: var(--cds-text-lg);
  color: #92400e;
}

.alerts-list {
  display: grid;
  gap: .5rem;
}

.alert-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: .5rem .75rem;
  background: var(--cds-white);
  border-radius: .55rem;
  font-size: var(--cds-text-sm);
}

.alert-item.critical {
  background: #fee2e2;
  border-left: 3px solid #dc2626;
}

.alert-item.warning {
  background: #fef3c7;
  border-left: 3px solid #f59e0b;
}

.alert-time {
  color: var(--cds-text-muted);
  font-size: var(--cds-text-xs);
}

/* Panel Grid */
.panel-grid { 
  display: grid; 
  gap: .7rem; 
  grid-template-columns: repeat(1, minmax(0, 1fr)); 
}

.panel-card { 
  padding: .9rem; 
}

.panel-card h2 { 
  margin: 0 0 .5rem; 
  font-size: var(--cds-text-xl); 
}

.quick-links { 
  display: flex; 
  flex-wrap: wrap; 
  gap: .45rem; 
}

.link-chip { 
  min-height: 40px; 
  padding: .55rem .75rem; 
  border-radius: .55rem; 
  border: 1px solid color-mix(in srgb, var(--cds-light) 65%, white); 
  text-decoration: none; 
  color: var(--cds-text-normal); 
  display: inline-flex; 
  align-items: center;
  font-size: var(--cds-text-sm);
  transition: all 0.2s ease;
}

.link-chip:hover {
  border-color: var(--cds-primary);
  color: var(--cds-primary);
  background: color-mix(in srgb, var(--cds-primary) 5%, white);
}

.link-chip.link-highlight {
  background: var(--cds-primary);
  border-color: var(--cds-primary);
  color: var(--cds-white);
  font-weight: 500;
}

.link-chip.link-highlight:hover {
  background: color-mix(in srgb, var(--cds-primary) 90%, black);
}

/* Table */
.table-wrap { 
  overflow-x: auto; 
}

table { 
  width: 100%; 
  border-collapse: collapse; 
}

th, td { 
  text-align: left; 
  padding: .6rem; 
  border-bottom: 1px solid color-mix(in srgb, var(--cds-light) 70%, white); 
}

th { 
  font-size: var(--cds-text-sm); 
  color: var(--cds-text-muted);
  font-weight: 500;
}

tbody tr:hover {
  background: color-mix(in srgb, var(--cds-light) 5%, white);
}

.link {
  color: var(--cds-primary);
  text-decoration: none;
  font-weight: 500;
}

.link:hover {
  text-decoration: underline;
}

.status-badge {
  display: inline-block;
  padding: .2rem .55rem;
  border-radius: 999px;
  font-size: var(--cds-text-xs);
  text-transform: uppercase;
  font-weight: 500;
}

.status-badge.pending {
  background: #fef3c7;
  color: #92400e;
}

.status-badge.in_progress {
  background: #dbeafe;
  color: #1e40af;
}

.status-badge.completed {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.delivered {
  background: #e0e7ff;
  color: #3730a3;
}

.empty-state { 
  border: 1px dashed color-mix(in srgb, var(--cds-light) 70%, white); 
  border-radius: .7rem; 
  padding: .9rem;
  color: var(--cds-text-muted);
  text-align: center;
}

@media (min-width: 760px) { 
  .stats-grid { 
    grid-template-columns: repeat(3, minmax(0, 1fr)); 
  } 
  .kpi-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .panel-grid { 
    grid-template-columns: repeat(1, minmax(0, 1fr)); 
  } 
}

@media (min-width: 1024px) {
  .kpi-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}
</style>
