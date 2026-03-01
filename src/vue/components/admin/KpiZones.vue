<template>
  <section class="kpi-zones">
    <article class="kpi-zone">
      <header class="zone-header">
        <h3>Zona OT</h3>
        <p>Seguimiento operativo de órdenes de trabajo</p>
      </header>
      <div class="zone-grid">
        <div class="kpi-card">
          <span class="kpi-label">OT totales</span>
          <strong class="kpi-value">{{ asInt(summary.total_repairs, dashboard.repairs) }}</strong>
        </div>
        <div class="kpi-card">
          <span class="kpi-label">OT activas</span>
          <strong class="kpi-value">{{ asInt(summary.active_repairs, dashboard.active_repairs) }}</strong>
        </div>
        <div class="kpi-card">
          <span class="kpi-label">OT este mes</span>
          <strong class="kpi-value">{{ asInt(summary.repairs_this_month, dashboard.repairs_this_month) }}</strong>
        </div>
        <div class="kpi-card">
          <span class="kpi-label">OT completadas</span>
          <strong class="kpi-value">{{ asInt(dashboard.completed_repairs, 0) }}</strong>
        </div>
      </div>
    </article>

    <article class="kpi-zone">
      <header class="zone-header">
        <h3>Zona Financiera</h3>
        <p>Facturación, cobranza y flujo de caja</p>
      </header>
      <div class="zone-grid">
        <div class="kpi-card">
          <span class="kpi-label">Facturado total</span>
          <strong class="kpi-value">{{ money(summary.revenue?.total_invoiced, revenue.total_invoiced) }}</strong>
        </div>
        <div class="kpi-card">
          <span class="kpi-label">Facturado mes</span>
          <strong class="kpi-value">{{ money(summary.revenue?.invoiced_this_month, revenue.total_paid) }}</strong>
        </div>
        <div class="kpi-card">
          <span class="kpi-label">Pendiente cobro</span>
          <strong class="kpi-value">{{ money(summary.revenue?.pending_collection, revenue.total_pending) }}</strong>
        </div>
        <div class="kpi-card">
          <span class="kpi-label">Tasa de cobro</span>
          <strong class="kpi-value">{{ percent(revenue.collection_rate) }}</strong>
        </div>
      </div>
    </article>

    <article class="kpi-zone">
      <header class="zone-header">
        <h3>Zona Inventario</h3>
        <p>Disponibilidad y riesgo de stock</p>
      </header>
      <div class="zone-grid">
        <div class="kpi-card">
          <span class="kpi-label">Items en stock</span>
          <strong class="kpi-value">{{ asInt(inventory.total_items, summary.total_items) }}</strong>
        </div>
        <div class="kpi-card warning">
          <span class="kpi-label">Stock bajo</span>
          <strong class="kpi-value">{{ asInt(summary.low_stock_alerts, inventory.low_stock_items) }}</strong>
        </div>
        <div class="kpi-card danger">
          <span class="kpi-label">Sin stock</span>
          <strong class="kpi-value">{{ asInt(summary.out_of_stock, inventory.out_of_stock) }}</strong>
        </div>
        <div class="kpi-card">
          <span class="kpi-label">Valor inventario</span>
          <strong class="kpi-value">{{ money(summary.inventory_value, inventory.total_inventory_value) }}</strong>
        </div>
      </div>
    </article>

    <article class="kpi-zone">
      <header class="zone-header">
        <h3>Zona Clientes y Garantía</h3>
        <p>Crecimiento de clientes y postventa</p>
      </header>
      <div class="zone-grid">
        <div class="kpi-card">
          <span class="kpi-label">Clientes totales</span>
          <strong class="kpi-value">{{ asInt(summary.total_clients, clients.total_clients) }}</strong>
        </div>
        <div class="kpi-card">
          <span class="kpi-label">Clientes nuevos mes</span>
          <strong class="kpi-value">{{ asInt(summary.new_clients_this_month, clients.new_this_month) }}</strong>
        </div>
        <div class="kpi-card">
          <span class="kpi-label">Garantías activas</span>
          <strong class="kpi-value">{{ asInt(summary.active_warranties, warranty.active_warranties) }}</strong>
        </div>
        <div class="kpi-card warning">
          <span class="kpi-label">Reclamos pendientes</span>
          <strong class="kpi-value">{{ pendingClaims }}</strong>
        </div>
      </div>
    </article>

    <article class="kpi-zone alerts-zone">
      <header class="zone-header">
        <h3>Zona Alertas</h3>
        <p>Eventos que requieren gestión inmediata</p>
      </header>
      <div v-if="alerts.length === 0" class="alerts-empty">
        Sin alertas activas.
      </div>
      <ul v-else class="alerts-list">
        <li
          v-for="alert in alerts"
          :key="`${alert.type}-${alert.count}`"
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

<style scoped lang="scss">
@use "@/scss/_theming.scss" as *;

.kpi-zones {
  display: grid;
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.kpi-zone {
  background: $color-white;
  border: 1px solid rgba($color-dark, 0.16);
  border-radius: 14px;
  padding: 1rem;
  box-shadow: 0 8px 18px rgba($color-dark, 0.08);
}

.zone-header h3 {
  margin: 0;
  color: $brand-text;
  font-size: 1rem;
}

.zone-header p {
  margin: 0.25rem 0 0;
  color: $text-muted;
  font-size: 0.82rem;
}

.zone-grid {
  margin-top: 0.75rem;
  display: grid;
  gap: 0.65rem;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.kpi-card {
  border-radius: 10px;
  border: 1px solid rgba($color-dark, 0.1);
  padding: 0.65rem;
  background: rgba($color-light, 0.75);
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.kpi-card.warning {
  border-color: rgba($color-warning, 0.4);
  background: rgba($color-warning, 0.12);
}

.kpi-card.danger {
  border-color: rgba($color-danger, 0.4);
  background: rgba($color-danger, 0.12);
}

.kpi-label {
  color: $text-muted;
  font-size: 0.78rem;
  line-height: 1.2;
}

.kpi-value {
  color: $brand-text;
  font-size: 1.1rem;
  line-height: 1.1;
}

.alerts-empty {
  margin-top: 0.75rem;
  color: $text-muted;
  font-size: 0.86rem;
}

.alerts-list {
  margin: 0.75rem 0 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 0.45rem;
}

.alert-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-radius: 8px;
  border: 1px solid rgba($color-dark, 0.12);
  padding: 0.5rem 0.65rem;
}

.alert-message {
  font-size: 0.83rem;
  color: $brand-text;
}

.alert-count {
  font-size: 0.8rem;
  min-width: 1.8rem;
  text-align: center;
  border-radius: 999px;
  background: rgba($color-dark, 0.08);
  padding: 0.1rem 0.35rem;
}

.severity-danger {
  border-color: rgba($color-danger, 0.4);
  background: rgba($color-danger, 0.1);
}

.severity-warning {
  border-color: rgba($color-warning, 0.4);
  background: rgba($color-warning, 0.12);
}

.severity-info {
  border-color: rgba($color-primary, 0.3);
  background: rgba($color-primary, 0.08);
}

@media (min-width: 768px) {
  .zone-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}
</style>
