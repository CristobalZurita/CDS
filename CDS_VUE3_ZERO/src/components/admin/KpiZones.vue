<template>
  <section class="kpi-zones">
    <!-- Zona OT -->
    <article class="kpi-zone">
      <header class="zone-header">
        <h3>📋 Zona OT</h3>
        <p>Seguimiento operativo de órdenes de trabajo</p>
      </header>
      <div class="zone-grid">
        <div class="kpi-card">
          <span class="kpi-label">OT totales</span>
          <strong class="kpi-value">{{ asInt(summary?.total_repairs, dashboard?.repairs) }}</strong>
        </div>
        <div class="kpi-card">
          <span class="kpi-label">OT activas</span>
          <strong class="kpi-value">{{ asInt(summary?.active_repairs, dashboard?.active_repairs) }}</strong>
        </div>
        <div class="kpi-card">
          <span class="kpi-label">OT este mes</span>
          <strong class="kpi-value">{{ asInt(summary?.repairs_this_month, dashboard?.repairs_this_month) }}</strong>
        </div>
        <div class="kpi-card">
          <span class="kpi-label">OT completadas</span>
          <strong class="kpi-value">{{ asInt(dashboard?.completed_repairs, 0) }}</strong>
        </div>
      </div>
    </article>

    <!-- Zona Financiera -->
    <article class="kpi-zone">
      <header class="zone-header">
        <h3>💰 Zona Financiera</h3>
        <p>Facturación, cobranza y flujo de caja</p>
      </header>
      <div class="zone-grid">
        <div class="kpi-card">
          <span class="kpi-label">Facturado total</span>
          <strong class="kpi-value">{{ money(summary?.revenue?.total_invoiced, revenue?.total_invoiced) }}</strong>
        </div>
        <div class="kpi-card">
          <span class="kpi-label">Facturado mes</span>
          <strong class="kpi-value">{{ money(summary?.revenue?.invoiced_this_month, revenue?.total_paid) }}</strong>
        </div>
        <div class="kpi-card">
          <span class="kpi-label">Pendiente cobro</span>
          <strong class="kpi-value">{{ money(summary?.revenue?.pending_collection, revenue?.total_pending) }}</strong>
        </div>
        <div class="kpi-card">
          <span class="kpi-label">Tasa de cobro</span>
          <strong class="kpi-value">{{ percent(revenue?.collection_rate) }}</strong>
        </div>
      </div>
    </article>

    <!-- Zona Inventario -->
    <article class="kpi-zone">
      <header class="zone-header">
        <h3>📦 Zona Inventario</h3>
        <p>Disponibilidad y riesgo de stock</p>
      </header>
      <div class="zone-grid">
        <div class="kpi-card">
          <span class="kpi-label">Items en stock</span>
          <strong class="kpi-value">{{ asInt(inventory?.total_items, summary?.total_items) }}</strong>
        </div>
        <div class="kpi-card warning">
          <span class="kpi-label">Stock bajo</span>
          <strong class="kpi-value">{{ asInt(summary?.low_stock_alerts, inventory?.low_stock_items) }}</strong>
        </div>
        <div class="kpi-card danger">
          <span class="kpi-label">Sin stock</span>
          <strong class="kpi-value">{{ asInt(summary?.out_of_stock, inventory?.out_of_stock) }}</strong>
        </div>
        <div class="kpi-card">
          <span class="kpi-label">Valor inventario</span>
          <strong class="kpi-value">{{ money(summary?.inventory_value, inventory?.total_inventory_value) }}</strong>
        </div>
      </div>
    </article>

    <!-- Zona Clientes y Garantía -->
    <article class="kpi-zone">
      <header class="zone-header">
        <h3>👥 Zona Clientes y Garantía</h3>
        <p>Crecimiento de clientes y postventa</p>
      </header>
      <div class="zone-grid">
        <div class="kpi-card">
          <span class="kpi-label">Clientes totales</span>
          <strong class="kpi-value">{{ asInt(summary?.total_clients, clients?.total_clients) }}</strong>
        </div>
        <div class="kpi-card">
          <span class="kpi-label">Clientes nuevos mes</span>
          <strong class="kpi-value">{{ asInt(summary?.new_clients_this_month, clients?.new_this_month) }}</strong>
        </div>
        <div class="kpi-card">
          <span class="kpi-label">Garantías activas</span>
          <strong class="kpi-value">{{ asInt(summary?.active_warranties, warranty?.active_warranties) }}</strong>
        </div>
        <div class="kpi-card warning">
          <span class="kpi-label">Reclamos pendientes</span>
          <strong class="kpi-value">{{ pendingClaims }}</strong>
        </div>
      </div>
    </article>

    <!-- Zona Alertas -->
    <article class="kpi-zone alerts-zone">
      <header class="zone-header">
        <h3>🚨 Zona Alertas</h3>
        <p>Eventos que requieren gestión inmediata</p>
      </header>
      <div v-if="alerts.length === 0" class="alerts-empty">
        ✅ Sin alertas activas
      </div>
      <ul v-else class="alerts-list">
        <li
          v-for="(alert, index) in alerts"
          :key="`${alert.type}-${index}`"
          :class="['alert-item', `severity-${alert.severity || 'info'}`]"
        >
          <span class="alert-message">{{ alert.message || alert.type }}</span>
          <span class="alert-count">{{ asInt(alert.count, 0) }}</span>
        </li>
      </ul>
    </article>
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

const percent = (value) => {
  const normalized = Number(value)
  const amount = Number.isFinite(normalized) ? normalized : 0
  return `${amount.toFixed(1)}%`
}
</script>

<style scoped>
.kpi-zones {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.kpi-zone {
  background: var(--color-white, #fff);
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.zone-header {
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid var(--color-light, #e0e0e0);
}

.zone-header h3 {
  margin: 0 0 0.25rem 0;
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--color-dark, #1a1a2e);
}

.zone-header p {
  margin: 0;
  font-size: 0.875rem;
  color: var(--color-gray-600, #666);
}

.zone-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 1rem;
}

.kpi-card {
  background: var(--color-bg, #f5f5f5);
  border-radius: 8px;
  padding: 1rem;
  text-align: center;
  border: 2px solid transparent;
  transition: transform 0.2s;
}

.kpi-card:hover {
  transform: translateY(-2px);
}

.kpi-card.warning {
  background: rgba(255, 193, 7, 0.15);
  border-color: rgba(255, 193, 7, 0.3);
}

.kpi-card.danger {
  background: rgba(220, 53, 69, 0.15);
  border-color: rgba(220, 53, 69, 0.3);
}

.kpi-label {
  display: block;
  font-size: 0.75rem;
  color: var(--color-gray-600, #666);
  text-transform: uppercase;
  letter-spacing: 0.03em;
  margin-bottom: 0.5rem;
}

.kpi-value {
  display: block;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-dark, #1a1a2e);
}

.kpi-card.warning .kpi-value {
  color: #856404;
}

.kpi-card.danger .kpi-value {
  color: #721c24;
}

.alerts-zone {
  border-left: 4px solid var(--color-primary, #ff6b35);
}

.alerts-empty {
  padding: 2rem;
  text-align: center;
  color: var(--color-gray-600, #666);
  font-style: italic;
}

.alerts-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.alert-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  background: var(--color-bg, #f5f5f5);
  border-left: 3px solid var(--color-info, #17a2b8);
}

.alert-item.severity-warning {
  border-left-color: #ffc107;
  background: rgba(255, 193, 7, 0.1);
}

.alert-item.severity-danger {
  border-left-color: #dc3545;
  background: rgba(220, 53, 69, 0.1);
}

.alert-item.severity-success {
  border-left-color: #28a745;
  background: rgba(40, 167, 69, 0.1);
}

.alert-count {
  font-weight: 700;
  color: var(--color-dark, #1a1a2e);
  background: var(--color-white, #fff);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  min-width: 2rem;
  text-align: center;
}

@media (max-width: 768px) {
  .zone-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
