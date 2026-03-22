<template>
  <div
    class="cart-overlay"
    :class="{ 'cart-overlay--open': open }"
    @click="$emit('close')"
  ></div>

  <aside class="cart-drawer" :class="{ 'cart-drawer--open': open }" data-testid="store-cart">
    <header class="cart-drawer-header">
      <div class="cart-drawer-title">
        <i class="fas fa-shopping-cart"></i>
        <span>Carrito</span>
        <span v-if="totals.itemsCount > 0" class="cart-badge-inline">{{ totals.itemsCount }}</span>
      </div>
      <button class="cart-close-btn" @click="$emit('close')" aria-label="Cerrar carrito">
        <i class="fas fa-times"></i>
      </button>
    </header>

    <div class="cart-drawer-body">
      <div v-if="items.length === 0" class="cart-empty" data-testid="store-cart-empty">
        <i class="fas fa-shopping-basket cart-empty-icon"></i>
        <p>La lista está vacía.</p>
        <p>Agrega repuestos del catálogo.</p>
      </div>

      <div v-else class="cart-list">
        <article
          v-for="item in items"
          :key="item.id"
          class="cart-item"
          data-testid="store-cart-item"
        >
          <div class="cart-item-thumb">
            <img v-if="item.image_url" :src="item.image_url" :alt="item.name" loading="lazy" />
            <i v-else class="fas fa-microchip"></i>
          </div>
          <div class="cart-item-info">
            <strong class="cart-item-name">{{ item.name }}</strong>
            <span class="cart-item-qty">× {{ item.qty }}</span>
          </div>
        </article>
      </div>
    </div>

    <footer class="cart-drawer-footer">
      <div class="cart-summary">
        <div class="summary-row">
          <span>Subtotal</span>
          <strong>{{ formatSummaryAmount(totals.productsSubtotal) }}</strong>
        </div>
        <div class="summary-row">
          <span>Despacho</span>
          <strong>{{ currentShipping.name }}</strong>
        </div>
        <div class="summary-row">
          <span>Costo despacho</span>
          <strong>{{ formatCurrency(totals.shippingPrice) }}</strong>
        </div>
        <div class="summary-row summary-row--total">
          <span>Total</span>
          <strong>{{ formatSummaryAmount(totals.grandTotal) }}</strong>
        </div>
      </div>

      <router-link
        to="/carrito"
        class="btn-view-cart"
        @click="$emit('close')"
      >
        <i class="fas fa-basket-shopping"></i> Ver carrito completo
      </router-link>

      <button
        class="btn-checkout"
        data-testid="store-checkout"
        :disabled="items.length === 0 || submitting"
        @click="$emit('checkout')"
      >
        {{ checkoutLabel }}
      </button>

      <button
        v-if="items.length > 0"
        class="btn-clear-cart"
        :disabled="submitting"
        @click="$emit('clear-cart')"
      >
        <i class="fa-solid fa-trash"></i> Vaciar carrito
      </button>

      <p class="cart-note">
        Al confirmar se genera una solicitud real y el taller coordina pago, despacho o retiro.
      </p>
    </footer>
  </aside>
</template>

<script setup>
import { formatStoreLinePrice, formatStoreSummaryAmount } from '@/services/storeCatalogService'
import { formatCurrency } from '@/utils/format'

const props = defineProps({
  open: {
    type: Boolean,
    default: false,
  },
  items: {
    type: Array,
    default: () => [],
  },
  totals: {
    type: Object,
    default: () => ({}),
  },
  currentShipping: {
    type: Object,
    default: () => ({ name: '' }),
  },
  checkoutLabel: {
    type: String,
    default: 'Enviar solicitud',
  },
  submitting: {
    type: Boolean,
    default: false,
  },
  canAddProduct: {
    type: Function,
    required: true,
  },
})

defineEmits(['close', 'change-qty', 'remove', 'checkout', 'clear-cart'])

function formatLinePrice(value) {
  return formatStoreLinePrice(value)
}

function formatSummaryAmount(value) {
  return formatStoreSummaryAmount(value, props.totals)
}
</script>

<style scoped>
.cart-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  z-index: 800;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.28s ease;
}

.cart-overlay--open {
  opacity: 1;
  pointer-events: auto;
}

.cart-drawer {
  --store-cart-drawer-width: var(--layout-store-drawer-width, min(500px, 100vw));
  --store-cart-header-pad-block: calc(1.1rem * var(--cds-type-scale, 1));
  --store-cart-section-pad-block: calc(1rem * var(--cds-type-scale, 1));
  --store-cart-section-pad-inline: calc(1.25rem * var(--cds-type-scale, 1));
  --store-cart-empty-gap: calc(0.5rem * var(--cds-type-scale, 1));
  --store-cart-empty-pad-block: calc(2rem * var(--cds-type-scale, 1));
  --store-cart-item-padding: calc(0.85rem * var(--cds-type-scale, 1));
  --store-cart-summary-gap: calc(0.5rem * var(--cds-type-scale, 1));
  --store-cart-action-gap: calc(0.5rem * var(--cds-type-scale, 1));
  --store-cart-checkout-min-height: calc(44px * var(--cds-type-scale, 1));
  --store-cart-checkout-pad-block: calc(0.7rem * var(--cds-type-scale, 1));
  --store-cart-checkout-pad-inline: calc(1rem * var(--cds-type-scale, 1));
  position: fixed;
  top: 0;
  right: -540px;
  width: var(--store-cart-drawer-width, min(420px, 100vw));
  height: 100dvh;
  z-index: 900;
  display: flex;
  flex-direction: column;
  background: var(--cds-surface-2);
  font-family: var(--layout-public-font-family-base, var(--cds-font-family-base), sans-serif);
  box-shadow: -6px 0 32px rgba(10, 12, 15, 0.28);
  transition: right 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.cart-drawer--open {
  right: 0;
}

.cart-drawer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--store-cart-header-pad-block, 1.1rem) var(--store-cart-section-pad-inline, 1.25rem);
  border-bottom: 1px solid rgba(198, 187, 176, 0.18);
  background: var(--cds-nav-background-color);
  color: var(--cds-white);
  flex-shrink: 0;
}

.cart-drawer-title {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-family: var(--layout-public-font-family-heading, var(--layout-public-font-family-base, var(--cds-font-family-base)));
  font-size: var(--layout-public-text-brand, 1.05rem);
  font-weight: 700;
  letter-spacing: -0.01em;
}

.cart-badge-inline {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: calc(22px * var(--cds-type-scale, 1));
  height: calc(22px * var(--cds-type-scale, 1));
  padding: 0 calc(5px * var(--cds-type-scale, 1));
  border-radius: var(--cds-radius-pill);
  background: var(--cds-primary);
  color: var(--cds-white);
  font-size: var(--layout-public-text-label, 0.75rem);
  font-weight: 800;
}

.cart-close-btn {
  width: calc(36px * var(--cds-type-scale, 1));
  height: calc(36px * var(--cds-type-scale, 1));
  border: 1px solid rgba(198, 187, 176, 0.24);
  border-radius: 50%;
  background: transparent;
  color: var(--cds-white);
  font-size: var(--layout-public-text-meta, 1rem);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s;
}

.cart-close-btn:hover {
  background: #25292e;
}

.cart-drawer-body {
  flex: 1;
  overflow-y: auto;
  padding: var(--store-cart-section-pad-block, 1rem) var(--store-cart-section-pad-inline, 1.25rem);
  display: flex;
  flex-direction: column;
  background: var(--cds-surface-2);
}

.cart-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--store-cart-empty-gap, 0.5rem);
  text-align: center;
  color: var(--cds-dark);
  opacity: 0.65;
  padding: var(--store-cart-empty-pad-block, 2rem) 0;
}

.cart-empty-icon {
  font-size: clamp(calc(2rem * var(--cds-type-scale, 1)), calc((1.6rem + 1vw) * var(--cds-type-scale, 1)), calc(2.5rem * var(--cds-type-scale, 1)));
  opacity: 0.45;
  margin-bottom: 0.5rem;
}

.cart-empty p {
  margin: 0;
  font-size: var(--layout-public-text-body, 0.95rem);
  line-height: 1.62;
}

.cart-list {
  display: grid;
  gap: calc(var(--cds-space-sm) * var(--cds-type-scale, 1));
}

.cart-item {
  display: grid;
  gap: calc(var(--cds-space-xs) * var(--cds-type-scale, 1));
  padding: var(--store-cart-item-padding, 0.75rem);
  border: 1px solid var(--cds-border-card);
  border-radius: var(--cds-radius-md);
  background: var(--cds-surface-1);
  box-shadow: var(--cds-shadow-sm);
}

.cart-item-name {
  flex: 1;
  min-width: 0;
  font-family: var(--layout-public-font-family-heading, var(--layout-public-font-family-base, var(--cds-font-family-base)));
  font-size: var(--layout-public-text-brand, 0.9rem);
  line-height: 1.25;
  letter-spacing: -0.01em;
  color: var(--cds-dark);
}

.cart-item-qty {
  flex-shrink: 0;
  font-size: var(--layout-public-text-meta, 0.82rem);
  color: var(--cds-text-muted);
}

.btn-view-cart {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: calc(0.4rem * var(--cds-type-scale, 1));
  width: 100%;
  min-height: calc(40px * var(--cds-type-scale, 1));
  padding: calc(0.6rem * var(--cds-type-scale, 1)) calc(1rem * var(--cds-type-scale, 1));
  border-radius: var(--cds-radius-sm);
  border: 1px solid var(--cds-border-card);
  background: var(--cds-surface-1);
  color: var(--cds-dark);
  font-size: var(--layout-public-text-body, 0.9rem);
  font-weight: var(--cds-font-semibold);
  text-decoration: none;
  transition: background 0.15s, color 0.15s;
}

.btn-view-cart:hover {
  background: var(--cds-surface-2);
  color: var(--cds-primary);
}

.cart-drawer-footer {
  padding: var(--store-cart-section-pad-block, 1rem) var(--store-cart-section-pad-inline, 1.25rem);
  border-top: 1px solid var(--cds-border-card);
  display: flex;
  flex-direction: column;
  gap: calc(var(--cds-space-sm) * var(--cds-type-scale, 1));
  flex-shrink: 0;
  background: var(--cds-surface-2);
}

.cart-summary {
  display: flex;
  flex-direction: column;
  gap: var(--store-cart-summary-gap, 0.4rem);
}

.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: calc(0.8rem * var(--cds-type-scale, 1));
  font-size: var(--layout-public-text-body, 0.9rem);
  line-height: 1.5;
  color: var(--cds-dark);
}

.summary-row--total {
  padding-top: calc(var(--cds-space-xs) * var(--cds-type-scale, 1));
  border-top: 1px solid var(--cds-border-card);
  font-size: var(--layout-public-text-brand, 1rem);
}

.btn-checkout {
  width: 100%;
  min-height: var(--store-cart-checkout-min-height, 44px);
  padding: var(--store-cart-checkout-pad-block, 0.7rem) var(--store-cart-checkout-pad-inline, 1rem);
  border-radius: var(--cds-radius-sm);
  border: none;
  background: var(--cds-primary);
  color: var(--cds-white);
  font-size: var(--layout-public-text-body, 0.95rem);
  font-weight: 700;
  cursor: pointer;
  transition: background 0.15s;
}

.btn-checkout:hover:not(:disabled) {
  background: var(--cds-primary-hover);
}

.btn-checkout:disabled {
  opacity: 0.55;
  cursor: default;
}

.btn-clear-cart {
  width: 100%;
  min-height: calc(38px * var(--cds-type-scale, 1));
  padding: calc(0.45rem * var(--cds-type-scale, 1)) calc(1rem * var(--cds-type-scale, 1));
  border-radius: var(--cds-radius-sm);
  border: 1px solid var(--cds-invalid-border);
  background: transparent;
  color: var(--cds-invalid-text);
  font-size: var(--layout-public-text-meta, 0.85rem);
  font-weight: var(--cds-font-semibold);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  transition: background 0.15s, color 0.15s;
}

.btn-clear-cart:hover:not(:disabled) {
  background: var(--cds-invalid-border);
  color: var(--cds-white);
}

.btn-clear-cart:disabled {
  opacity: 0.45;
  cursor: default;
}

.cart-note {
  margin: 0;
  font-size: var(--layout-public-text-meta, 0.82rem);
  color: var(--cds-text-muted);
  line-height: 1.62;
}

.cart-item {
  display: flex;
  align-items: center;
  gap: calc(var(--cds-space-sm) * var(--cds-type-scale, 1));
}

.cart-item-thumb {
  flex-shrink: 0;
  width: calc(44px * var(--cds-type-scale, 1));
  height: calc(44px * var(--cds-type-scale, 1));
  border-radius: var(--cds-radius-sm);
  border: 1px solid var(--cds-border-card);
  background: var(--cds-white);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  color: var(--cds-border-card);
  font-size: 1.1rem;
}

.cart-item-thumb img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.cart-item-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}
</style>
