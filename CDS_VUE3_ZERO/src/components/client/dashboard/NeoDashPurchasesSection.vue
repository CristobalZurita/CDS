<template>
  <NeoDashActiveSection
    eyebrow="Store"
    title="Compras y carrito"
    description="Puente entre carrito actual, tienda y solicitudes reales asociadas al cliente."
  >
    <template #actions>
      <router-link class="neo-dash-inline-link" to="/tienda">Ir a tienda</router-link>
      <router-link class="neo-dash-inline-link" to="/ot-payments">Ver solicitudes</router-link>
    </template>

    <div class="neo-dash-mini-grid">
      <article class="neo-dash-mini-card">
        <span class="neo-dash-stat-label">Items activos</span>
        <strong class="neo-dash-stat-value">{{ cartItems.length }}</strong>
      </article>
      <article class="neo-dash-mini-card">
        <span class="neo-dash-stat-label">Solicitudes</span>
        <strong class="neo-dash-stat-value">{{ storeRequests.length }}</strong>
      </article>
      <article class="neo-dash-mini-card">
        <span class="neo-dash-stat-label">Pendientes</span>
        <strong class="neo-dash-stat-value">{{ pendingRequests }}</strong>
      </article>
      <article class="neo-dash-mini-card">
        <span class="neo-dash-stat-label">Total carrito</span>
        <strong class="neo-dash-stat-value">{{ formatCurrency(totals.grandTotal) }}</strong>
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

    <div v-if="activeFilter === 'cart'" class="neo-dash-purchase-layout">
      <article class="neo-dash-card neo-dash-card--collection">
        <div class="neo-dash-item-head">
          <div>
            <h3 class="neo-dash-card-title">Carrito actual</h3>
            <p class="neo-dash-card-copy">Estado local del carrito que ya vive en Pinia.</p>
          </div>
          <span class="neo-dash-status">{{ cartItems.length }}</span>
        </div>

        <div v-if="cartItems.length > 0" class="neo-dash-list">
          <article v-for="item in cartItems.slice(0, 4)" :key="item.id" class="neo-dash-item neo-dash-item--row">
            <div class="neo-dash-item-head neo-dash-item-head--stack">
              <div>
                <h4 class="neo-dash-item-title">{{ item.name }}</h4>
                <p class="neo-dash-item-meta">{{ item.sku || 'SIN_SKU' }} · {{ item.family || item.category || 'Tienda' }}</p>
              </div>
            </div>
            <div class="neo-dash-item-aside">
              <span class="neo-dash-status">{{ item.qty }}x</span>
              <strong class="neo-dash-item-total">{{ formatCurrency(Number(item.price || 0) * Number(item.qty || 0)) }}</strong>
              <p class="neo-dash-item-meta">{{ formatCurrency(Number(item.price || 0)) }} c/u</p>
            </div>
          </article>
        </div>
        <div v-else class="neo-dash-empty">
          <p class="neo-dash-empty-copy">Tu carrito está vacío.</p>
          <router-link class="neo-dash-link-btn neo-dash-link-btn--primary" to="/tienda">
            Explorar tienda
          </router-link>
        </div>
      </article>

      <aside class="neo-dash-side-stack">
      <article class="neo-dash-callout neo-dash-callout--summary">
        <h3 class="neo-dash-callout-title">Resumen de compra</h3>
        <div class="neo-dash-summary-list">
          <div class="neo-dash-summary-row">
            <span>Items</span>
            <strong>{{ totals.itemsCount }}</strong>
          </div>
          <div class="neo-dash-summary-row">
            <span>Subtotal</span>
            <strong>{{ formatCurrency(totals.productsSubtotal) }}</strong>
          </div>
          <div class="neo-dash-summary-row">
            <span>Despacho</span>
            <strong>{{ currentShipping?.name || '—' }}</strong>
          </div>
          <div class="neo-dash-summary-row neo-dash-summary-row--total">
            <span>Total</span>
            <strong>{{ formatCurrency(totals.grandTotal) }}</strong>
          </div>
        </div>
      </article>
      <article class="neo-dash-card neo-dash-card--actions">
        <h3 class="neo-dash-card-title">Siguiente paso</h3>
        <p class="neo-dash-card-copy">Continúa la compra o revisa las solicitudes ya emitidas desde el mismo flujo.</p>
        <div class="neo-dash-inline-actions">
          <router-link class="neo-dash-link-btn neo-dash-link-btn--primary" to="/tienda">
            Volver a tienda
          </router-link>
          <router-link class="neo-dash-link-btn neo-dash-link-btn--secondary" to="/ot-payments">
            Ver solicitudes
          </router-link>
        </div>
      </article>
      </aside>
    </div>

    <div v-else-if="storeRequests.length > 0" class="neo-dash-list">
      <article v-for="request in storeRequests" :key="request.id" class="neo-dash-item">
        <div class="neo-dash-item-head">
          <div>
            <h3 class="neo-dash-item-title">Solicitud tienda #{{ request.id }}</h3>
            <p class="neo-dash-item-meta">{{ request.items_count || 0 }} item(s) · {{ formatDate(request.created_at || request.payment_due_date) }}</p>
          </div>
          <span class="neo-dash-status" :class="normalizeStatus(request.status)">{{ request.status }}</span>
        </div>
        <p class="neo-dash-item-copy">
          Monto estimado: {{ formatCurrency(request.requested_amount || request.total_items_amount || 0) }}
        </p>
      </article>
    </div>

    <div v-else class="neo-dash-empty">
      <p class="neo-dash-empty-copy">No hay solicitudes de tienda registradas todavía.</p>
      <router-link class="neo-dash-link-btn neo-dash-link-btn--secondary" to="/tienda">
        Ir a tienda
      </router-link>
    </div>
  </NeoDashActiveSection>
</template>

<script setup>
import { computed } from 'vue'
import NeoDashActiveSection from './NeoDashActiveSection.vue'

const props = defineProps({
  activeFilter: { type: String, default: 'cart' },
  cartItems: { type: Array, default: () => [] },
  totals: {
    type: Object,
    default: () => ({ itemsCount: 0, productsSubtotal: 0, grandTotal: 0 }),
  },
  currentShipping: {
    type: Object,
    default: () => null,
  },
  storeRequests: { type: Array, default: () => [] },
  formatCurrency: { type: Function, required: true },
  formatDate: { type: Function, required: true },
  normalizeStatus: { type: Function, required: true },
})

defineEmits(['update:active-filter'])

const filters = [
  { key: 'cart', label: 'Carrito' },
  { key: 'requests', label: 'Solicitudes' },
]

const pendingRequests = computed(() => {
  const rows = Array.isArray(props.storeRequests) ? props.storeRequests : []
  return rows.filter((request) => ['requested', 'pending_payment', 'proof_submitted'].includes(props.normalizeStatus(request?.status))).length
})
</script>

<style src="./neoDashboardShared.css"></style>
