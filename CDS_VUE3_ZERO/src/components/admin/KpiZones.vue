<template>
  <section class="kpi-section">
    <div class="kpi-grid">
      <!-- Zona OT -->
      <div class="kpi-box">
        <div class="kpi-header">
          <span class="kpi-icon">📋</span>
          <div>
            <h3 class="kpi-title">Órdenes de Trabajo</h3>
            <p class="kpi-desc">Seguimiento operativo</p>
          </div>
        </div>
        <div class="kpi-metrics">
          <div class="metric">
            <span class="metric-value">{{ asInt(summary?.total_repairs, dashboard?.repairs) }}</span>
            <span class="metric-label">Totales</span>
          </div>
          <div class="metric">
            <span class="metric-value">{{ asInt(summary?.active_repairs, dashboard?.active_repairs) }}</span>
            <span class="metric-label">Activas</span>
          </div>
          <div class="metric">
            <span class="metric-value">{{ asInt(summary?.repairs_this_month, dashboard?.repairs_this_month) }}</span>
            <span class="metric-label">Este mes</span>
          </div>
          <div class="metric">
            <span class="metric-value">{{ asInt(dashboard?.completed_repairs, 0) }}</span>
            <span class="metric-label">Completadas</span>
          </div>
        </div>
      </div>

      <!-- Zona Financiera -->
      <div class="kpi-box">
        <div class="kpi-header">
          <span class="kpi-icon">💰</span>
          <div>
            <h3 class="kpi-title">Finanzas</h3>
            <p class="kpi-desc">Facturación y cobranza</p>
          </div>
        </div>
        <div class="kpi-metrics">
          <div class="metric">
            <span class="metric-value">{{ money(summary?.revenue?.total_invoiced, revenue?.total_invoiced) }}</span>
            <span class="metric-label">Facturado</span>
          </div>
          <div class="metric">
            <span class="metric-value">{{ money(summary?.revenue?.invoiced_this_month, revenue?.total_paid) }}</span>
            <span class="metric-label">Este mes</span>
          </div>
          <div class="metric warning">
            <span class="metric-value">{{ money(summary?.revenue?.pending_collection, revenue?.total_pending) }}</span>
            <span class="metric-label">Pendiente</span>
          </div>
          <div class="metric">
            <span class="metric-value">{{ percent(revenue?.collection_rate) }}</span>
            <span class="metric-label">Cobranza</span>
          </div>
        </div>
      </div>

      <!-- Zona Inventario -->
      <div class="kpi-box">
        <div class="kpi-header">
          <span class="kpi-icon">📦</span>
          <div>
            <h3 class="kpi-title">Inventario</h3>
            <p class="kpi-desc">Stock y disponibilidad</p>
          </div>
        </div>
        <div class="kpi-metrics">
          <div class="metric">
            <span class="metric-value">{{ asInt(inventory?.total_items, summary?.total_items) }}</span>
            <span class="metric-label">Items</span>
          </div>
          <div class="metric warning">
            <span class="metric-value">{{ asInt(summary?.low_stock_alerts, inventory?.low_stock_items) }}</span>
            <span class="metric-label">Stock bajo</span>
          </div>
          <div class="metric danger">
            <span class="metric-value">{{ asInt(summary?.out_of_stock, inventory?.out_of_stock) }}</span>
            <span class="metric-label">Sin stock</span>
          </div>
          <div class="metric">
            <span class="metric-value">{{ moneyCompact(summary?.inventory_value, inventory?.total_inventory_value) }}</span>
            <span class="metric-label">Valor</span>
          </div>
        </div>
      </div>

      <!-- Zona Clientes -->
      <div class="kpi-box">
        <div class="kpi-header">
          <span class="kpi-icon">👥</span>
          <div>
            <h3 class="kpi-title">Clientes</h3>
            <p class="kpi-desc">Base y garantías</p>
          </div>
        </div>
        <div class="kpi-metrics">
          <div class="metric">
            <span class="metric-value">{{ asInt(summary?.total_clients, clients?.total_clients) }}</span>
            <span class="metric-label">Totales</span>
          </div>
          <div class="metric">
            <span class="metric-value">{{ asInt(summary?.new_clients_this_month, clients?.new_this_month) }}</span>
            <span class="metric-label">Nuevos</span>
          </div>
          <div class="metric">
            <span class="metric-value">{{ asInt(summary?.active_warranties, warranty?.active_warranties) }}</span>
            <span class="metric-label">Garantías</span>
          </div>
          <div class="metric warning" v-if="pendingClaims > 0">
            <span class="metric-value">{{ pendingClaims }}</span>
            <span class="metric-label">Reclamos</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Alertas -->
    <div v-if="alerts.length > 0" class="alerts-box">
      <div class="alerts-header">
        <span class="alerts-icon">🚨</span>
        <h3>Alertas que requieren atención</h3>
      </div>
      <ul class="alerts-list">
        <li
          v-for="(alert, index) in alerts"
          :key="index"
          :class="['alert-item', `alert-${alert.severity || 'info'}`]"
        >
          <span class="alert-text">{{ alert.message || alert.type }}</span>
          <span class="alert-badge">{{ asInt(alert.count, 0) }}</span>
        </li>
      </ul>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  summary: { type: Object, default: () => ({}) },
  dashboard: { type: Object, default: () => ({}) },
  revenue: { type: Object, default: () => ({}) },
  inventory: { type: Object, default: () => ({}) },
  clients: { type: Object, default: () => ({}) },
  warranty: { type: Object, default: () => ({}) }
})

const alerts = computed(() => {
  if (Array.isArray(props.summary?.alerts) && props.summary.alerts.length) {
    return props.summary.alerts
  }
  if (Array.isArray(props.dashboard?.alerts) && props.dashboard.alerts.length) {
    return props.dashboard.alerts
  }
  return []
})

const pendingClaims = computed(() => {
  if (props.summary?.pending_claims != null) {
    return asInt(props.summary.pending_claims, 0)
  }
  const total = asInt(props.warranty?.total_claims, 0)
  const approved = asInt(props.warranty?.approved_claims, 0)
  const rejected = asInt(props.warranty?.rejected_claims, 0)
  return Math.max(total - approved - rejected, 0)
})

const asInt = (value, fallback = 0) => {
  const raw = value != null ? value : fallback
  const normalized = Number(raw)
  if (!Number.isFinite(normalized)) return 0
  return Math.round(normalized)
}

const money = (value, fallback = 0) => {
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

const moneyCompact = (value, fallback = 0) => {
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

const percent = (value) => {
  const normalized = Number(value)
  const amount = Number.isFinite(normalized) ? normalized : 0
  return `${amount.toFixed(0)}%`
}
</script>

<style scoped>
.kpi-section {
  margin-bottom: var(--admin-space-xl, 2.4rem);
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(420px, 1fr));
  gap: var(--admin-space-lg, 1.8rem);
}

.kpi-box {
  background: var(--cds-white);
  border-radius: var(--cds-radius-lg);
  padding: var(--admin-space-lg, 1.8rem);
  box-shadow: var(--cds-shadow-sm);
  border: 1px solid var(--cds-border-card);
}

.kpi-header {
  display: flex;
  align-items: center;
  gap: var(--admin-space-md, 1.2rem);
  margin-bottom: var(--admin-space-md, 1.2rem);
  padding-bottom: var(--admin-space-md, 1.2rem);
  border-bottom: 1px solid var(--cds-border-card);
}

.kpi-icon {
  font-size: var(--cds-text-2xl);
}

.kpi-title {
  margin: 0;
  font-size: var(--cds-text-xl);
  font-weight: 600;
  color: var(--cds-dark);
}

.kpi-desc {
  margin: 0.2rem 0 0;
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
}

.kpi-metrics {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--admin-space-md, 1.2rem);
}

.metric {
  background: var(--cds-light-1);
  border-radius: var(--cds-radius-md);
  padding: var(--admin-space-md, 1.2rem);
  text-align: center;
}

.metric-value {
  display: block;
  font-size: var(--cds-text-2xl);
  font-weight: 700;
  color: var(--cds-dark);
  margin-bottom: 0.5rem;
  line-height: 1.05;
}

.metric-label {
  display: block;
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.metric.warning .metric-value {
  color: var(--cds-warning-text);
}

.metric.danger .metric-value {
  color: var(--cds-danger);
}

.alerts-box {
  background: var(--cds-white);
  border-radius: var(--cds-radius-lg);
  padding: var(--admin-space-lg, 1.8rem);
  margin-top: var(--admin-space-lg, 1.8rem);
  box-shadow: var(--cds-shadow-sm);
  border: 1px solid var(--cds-border-card);
  border-left: 4px solid var(--cds-primary);
}

.alerts-header {
  display: flex;
  align-items: center;
  gap: var(--admin-space-xs, 0.66rem);
  margin-bottom: var(--admin-space-md, 1.2rem);
}

.alerts-header h3 {
  margin: 0;
  font-size: var(--cds-text-xl);
  font-weight: 600;
  color: var(--cds-dark);
}

.alerts-icon {
  font-size: var(--cds-text-xl);
}

.alerts-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: var(--admin-space-sm, 0.96rem);
}

.alert-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--admin-space-md, 1.2rem) var(--admin-space-lg, 1.8rem);
  background: var(--cds-light-1);
  border-radius: var(--cds-radius-sm);
  border-left: 3px solid var(--cds-text-muted);
}

.alert-item.alert-warning {
  border-left-color: var(--cds-warning);
  background: var(--cds-warning-bg);
}

.alert-item.alert-danger {
  border-left-color: var(--cds-danger);
  background: var(--cds-invalid-bg);
}

.alert-item.alert-success {
  border-left-color: var(--cds-success);
  background: var(--cds-valid-bg);
}

.alert-text {
  font-size: var(--cds-text-base);
  color: var(--cds-light-7);
}

.alert-badge {
  background: var(--cds-white);
  padding: var(--cds-space-xs) var(--cds-space-md);
  border-radius: var(--cds-radius-sm);
  font-size: var(--cds-text-sm);
  font-weight: 600;
  color: var(--cds-dark);
  min-width: 2.6rem;
  text-align: center;
}
</style>
