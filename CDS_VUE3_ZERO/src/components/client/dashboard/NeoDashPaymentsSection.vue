<template>
  <NeoDashActiveSection
    eyebrow="Payments"
    title="Pagos y comprobantes"
    description="Solicitudes reales del sistema con foco en movimiento pendiente y seguimiento rapido."
  >
    <template #actions>
      <router-link class="neo-dash-inline-link" to="/ot-payments">Abrir centro de pagos</router-link>
    </template>

    <div class="neo-dash-mini-grid">
      <article class="neo-dash-mini-card">
        <span class="neo-dash-stat-label">Pendientes</span>
        <strong class="neo-dash-stat-value">{{ paymentSummary.pending }}</strong>
      </article>
      <article class="neo-dash-mini-card">
        <span class="neo-dash-stat-label">Comprobantes</span>
        <strong class="neo-dash-stat-value">{{ paymentSummary.proofs }}</strong>
      </article>
      <article class="neo-dash-mini-card">
        <span class="neo-dash-stat-label">Pagadas</span>
        <strong class="neo-dash-stat-value">{{ paymentSummary.paid }}</strong>
      </article>
      <article class="neo-dash-mini-card">
        <span class="neo-dash-stat-label">Monto visible</span>
        <strong class="neo-dash-stat-value">{{ formatCurrency(paymentSummary.visibleAmount) }}</strong>
      </article>
    </div>

    <div class="neo-dash-chip-row">
      <button
        v-for="filter in filters"
        :key="filter.key"
        type="button"
        class="neo-dash-chip"
        :class="{ 'neo-dash-chip--active': filter.key === activeFilter }"
        @click="$emit('update:active-filter', filter.key)"
      >
        {{ filter.label }}
      </button>
    </div>

    <p v-if="error" class="neo-dash-error">{{ error }}</p>
    <p v-else-if="loading" class="neo-dash-note">Cargando solicitudes de pago...</p>

    <div v-else-if="requests.length > 0" class="neo-dash-list">
      <article v-for="request in requests" :key="request.id" class="neo-dash-item">
        <div class="neo-dash-item-head">
          <div>
            <h3 class="neo-dash-item-title">Solicitud #{{ request.id }}</h3>
            <p class="neo-dash-item-meta">
              {{ request.repair_code || request.repair_number ? `OT ${request.repair_code || request.repair_number}` : 'Tienda / sin OT' }}
            </p>
          </div>
          <span class="neo-dash-status" :class="normalizeStatus(request.status)">{{ request.status }}</span>
        </div>

        <div class="neo-dash-mini-grid">
          <article class="neo-dash-mini-card">
            <span class="neo-dash-stat-label">Monto</span>
            <strong class="neo-dash-stat-value">{{ formatCurrency(request.requested_amount || request.total_items_amount || 0) }}</strong>
          </article>
          <article class="neo-dash-mini-card">
            <span class="neo-dash-stat-label">Vence</span>
            <strong class="neo-dash-stat-value">{{ formatDate(request.payment_due_date) }}</strong>
          </article>
        </div>

        <p v-if="request.latest_payment?.admin_notes" class="neo-dash-note">
          <strong>Indicaciones:</strong> {{ request.latest_payment.admin_notes }}
        </p>

        <div class="neo-dash-inline-actions">
          <router-link class="neo-dash-inline-link" to="/ot-payments">Gestionar pago</router-link>
          <a
            v-if="request.latest_payment?.proof_path"
            class="neo-dash-inline-link"
            :href="toApiPath(request.latest_payment.proof_path)"
            target="_blank"
            rel="noopener noreferrer"
          >
            Ver comprobante
          </a>
        </div>
      </article>
    </div>

    <div v-else class="neo-dash-empty">
      <p class="neo-dash-empty-copy">No hay solicitudes de pago para este filtro.</p>
      <router-link class="neo-dash-link-btn neo-dash-link-btn--secondary" to="/ot-payments">
        Ir a pagos y solicitudes
      </router-link>
    </div>
  </NeoDashActiveSection>
</template>

<script setup>
import { computed } from 'vue'
import NeoDashActiveSection from './NeoDashActiveSection.vue'

const props = defineProps({
  requests: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
  activeFilter: { type: String, default: 'pending' },
  formatCurrency: { type: Function, required: true },
  formatDate: { type: Function, required: true },
  toApiPath: { type: Function, required: true },
  normalizeStatus: { type: Function, required: true },
})

defineEmits(['update:active-filter'])

const filters = [
  { key: 'pending', label: 'Pendientes' },
  { key: 'all', label: 'Todas' },
  { key: 'history', label: 'Historial' },
]

const paymentSummary = computed(() => {
  const rows = Array.isArray(props.requests) ? props.requests : []
  return rows.reduce((acc, request) => {
    const status = props.normalizeStatus(request?.status)
    const amount = Number(request?.requested_amount || request?.total_items_amount || 0)
    acc.visibleAmount += Number.isFinite(amount) ? amount : 0
    if (['requested', 'pending_payment'].includes(status)) acc.pending += 1
    if (status === 'proof_submitted') acc.proofs += 1
    if (['paid', 'completed', 'approved'].includes(status)) acc.paid += 1
    return acc
  }, {
    pending: 0,
    proofs: 0,
    paid: 0,
    visibleAmount: 0,
  })
})
</script>

<style src="./neoDashboardShared.css"></style>
