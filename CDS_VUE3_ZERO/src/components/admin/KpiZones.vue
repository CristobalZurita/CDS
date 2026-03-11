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
/* 35% larger */
.kpi-section {
  margin-bottom: 2.7rem;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
  gap: 2rem;
}

.kpi-box {
  background: #fff;
  border-radius: 16px;
  padding: 1.7rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
  border: 1px solid #e8ecf1;
}

.kpi-header {
  display: flex;
  align-items: center;
  gap: 1.2rem;
  margin-bottom: 1.35rem;
  padding-bottom: 1.2rem;
  border-bottom: 1px solid #e8ecf1;
}

.kpi-icon {
  font-size: 2rem;
}

.kpi-title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: #1a1f36;
}

.kpi-desc {
  margin: 0.2rem 0 0;
  font-size: 1.25rem;
  color: #6b7280;
}

.kpi-metrics {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.2rem;
}

.metric {
  background: #f8fafc;
  border-radius: 11px;
  padding: 1rem;
  text-align: center;
}

.metric-value {
  display: block;
  font-size: 1.75rem;
  font-weight: 700;
  color: #1a1f36;
  margin-bottom: 0.4rem;
}

.metric-label {
  display: block;
  font-size: 1.15rem;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.metric.warning .metric-value {
  color: #b45309;
}

.metric.danger .metric-value {
  color: #dc2626;
}

/* Alertas - 35% larger */
.alerts-box {
  background: #fff;
  border-radius: 16px;
  padding: 1.7rem;
  margin-top: 2rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
  border: 1px solid #e8ecf1;
  border-left: 4px solid #ff6b35;
}

.alerts-header {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  margin-bottom: 1.2rem;
}

.alerts-header h3 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: #1a1f36;
}

.alerts-icon {
  font-size: 1.75rem;
}

.alerts-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.alert-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.35rem;
  background: #f8fafc;
  border-radius: 8px;
  border-left: 3px solid #6b7280;
}

.alert-item.alert-warning {
  border-left-color: #f59e0b;
  background: #fffbeb;
}

.alert-item.alert-danger {
  border-left-color: #dc2626;
  background: #fef2f2;
}

.alert-item.alert-success {
  border-left-color: #10b981;
  background: #ecfdf5;
}

.alert-text {
  font-size: 1.4rem;
  color: #374151;
}

.alert-badge {
  background: #fff;
  padding: 0.4rem 0.85rem;
  border-radius: 6px;
  font-size: 1.2rem;
  font-weight: 600;
  color: #1a1f36;
  min-width: 2rem;
  text-align: center;
}
</style>
