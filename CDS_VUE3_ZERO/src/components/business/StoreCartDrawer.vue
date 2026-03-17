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
        <span>Mi lista</span>
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
          <div class="cart-item-copy">
            <strong>{{ item.name }}</strong>
            <span>{{ item.sku }}</span>
            <small>{{ formatLinePrice(item.price) }} c/u</small>
          </div>

          <div class="cart-item-actions">
            <button class="qty-btn" @click="$emit('change-qty', { id: item.id, delta: -1 })">−</button>
            <span class="qty-value">{{ item.qty }}</span>
            <button
              class="qty-btn"
              :disabled="!canAddProduct(item)"
              @click="$emit('change-qty', { id: item.id, delta: 1 })"
            >+</button>
            <button class="remove-btn" @click="$emit('remove', item.id)">Quitar</button>
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

      <button
        class="btn-checkout"
        data-testid="store-checkout"
        :disabled="items.length === 0 || submitting"
        @click="$emit('checkout')"
      >
        {{ checkoutLabel }}
      </button>

      <p class="cart-note">
        Al iniciar sesión como cliente esta lista se convierte en una solicitud real.
      </p>
    </footer>
  </aside>
</template>

<script setup>
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

defineEmits(['close', 'change-qty', 'remove', 'checkout'])

function formatLinePrice(value) {
  const amount = Number(value || 0)
  return amount > 0 ? formatCurrency(amount) : 'Por cotizar'
}

function formatSummaryAmount(value) {
  const amount = Number(value || 0)
  return props.totals?.hasQuotedAmount && amount > 0 ? formatCurrency(amount) : 'Por cotizar'
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
  position: fixed;
  top: 0;
  right: -440px;
  width: min(420px, 100vw);
  height: 100dvh;
  z-index: 900;
  display: flex;
  flex-direction: column;
  background: var(--cds-white);
  box-shadow: -6px 0 32px rgba(0, 0, 0, 0.18);
  transition: right 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.cart-drawer--open {
  right: 0;
}

.cart-drawer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.1rem 1.25rem;
  border-bottom: 1px solid color-mix(in srgb, var(--cds-dark) 12%, white);
  background: var(--cds-dark);
  color: var(--cds-white);
  flex-shrink: 0;
}

.cart-drawer-title {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-size: 1.05rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.cart-badge-inline {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 22px;
  height: 22px;
  padding: 0 5px;
  border-radius: var(--cds-radius-pill);
  background: var(--cds-primary);
  color: var(--cds-white);
  font-size: 0.75rem;
  font-weight: 800;
}

.cart-close-btn {
  width: 36px;
  height: 36px;
  border: 1px solid rgba(255, 255, 255, 0.25);
  border-radius: 50%;
  background: transparent;
  color: var(--cds-white);
  font-size: 1rem;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s;
}

.cart-close-btn:hover {
  background: rgba(255, 255, 255, 0.15);
}

.cart-drawer-body {
  flex: 1;
  overflow-y: auto;
  padding: 1rem 1.25rem;
  display: flex;
  flex-direction: column;
}

.cart-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  text-align: center;
  color: var(--cds-dark);
  opacity: 0.65;
  padding: 2rem 0;
}

.cart-empty-icon {
  font-size: 2.5rem;
  opacity: 0.45;
  margin-bottom: 0.5rem;
}

.cart-empty p {
  margin: 0;
  font-size: 0.95rem;
}

.cart-list {
  display: flex;
  flex-direction: column;
  gap: var(--cds-space-sm);
}

.cart-item {
  display: flex;
  flex-direction: column;
  gap: var(--cds-space-xs);
  padding: 0.75rem;
  border: 1px solid var(--cds-border-card);
  border-radius: var(--cds-radius-sm);
}

.cart-item-copy {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.cart-item-copy strong {
  font-size: 0.9rem;
  color: var(--cds-dark);
}

.cart-item-copy span,
.cart-item-copy small {
  font-size: 0.82rem;
  color: var(--cds-text-muted);
}

.cart-item-actions {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.qty-btn {
  width: 34px;
  height: 34px;
  border: 1px solid var(--cds-border-input);
  border-radius: var(--cds-radius-sm);
  background: white;
  color: var(--cds-dark);
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.qty-btn:disabled {
  opacity: 0.5;
}

.qty-value {
  min-width: 28px;
  text-align: center;
  font-weight: 700;
  font-size: 1rem;
  color: var(--cds-dark);
}

.remove-btn {
  margin-left: auto;
  padding: 0.25rem 0.6rem;
  border: 1px solid var(--cds-invalid-border);
  border-radius: var(--cds-radius-sm);
  background: transparent;
  color: var(--cds-invalid-text);
  font-size: 0.8rem;
  cursor: pointer;
}

.cart-drawer-footer {
  padding: 1rem 1.25rem;
  border-top: 1px solid color-mix(in srgb, var(--cds-dark) 12%, white);
  display: flex;
  flex-direction: column;
  gap: var(--cds-space-sm);
  flex-shrink: 0;
  background: color-mix(in srgb, var(--cds-light) 28%, white);
}

.cart-summary {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
  color: var(--cds-dark);
}

.summary-row--total {
  padding-top: var(--cds-space-xs);
  border-top: 1px solid color-mix(in srgb, var(--cds-dark) 12%, white);
  font-size: 1rem;
}

.btn-checkout {
  width: 100%;
  min-height: 44px;
  padding: 0.7rem 1rem;
  border-radius: var(--cds-radius-sm);
  border: none;
  background: var(--cds-primary);
  color: var(--cds-white);
  font-size: 0.95rem;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.15s;
}

.btn-checkout:hover:not(:disabled) {
  background: color-mix(in srgb, var(--cds-primary) 85%, black);
}

.btn-checkout:disabled {
  opacity: 0.55;
  cursor: default;
}

.cart-note {
  margin: 0;
  font-size: 0.82rem;
  color: var(--cds-text-muted);
  line-height: 1.5;
}
</style>
