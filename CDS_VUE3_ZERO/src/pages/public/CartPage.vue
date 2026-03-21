<template>
  <main class="cart-page">
    <div class="container cart-page-inner">

      <header class="cart-page-header">
        <h1 class="cart-page-title">Tu carrito</h1>
        <router-link to="/tienda" class="cart-back-link">
          <i class="fas fa-arrow-left"></i> Seguir comprando
        </router-link>
      </header>

      <div v-if="items.length === 0" class="cart-page-empty">
        <i class="fas fa-shopping-basket cart-empty-icon"></i>
        <p>Tu carrito está vacío.</p>
        <router-link to="/tienda" class="btn-to-store">
          <i class="fas fa-store"></i> Ver tienda
        </router-link>
      </div>

      <div v-else class="cart-page-layout">

        <section class="cart-page-items">
          <article v-for="item in items" :key="item.id" class="cart-page-item">
            <div class="cart-item-img-wrap">
              <img
                v-if="item.image_url"
                :src="item.image_url"
                :alt="item.name"
                class="cart-item-img"
                loading="lazy"
              />
              <div v-else class="cart-item-img-placeholder">
                <i class="fas fa-microchip"></i>
              </div>
            </div>

            <div class="cart-item-info">
              <strong class="cart-item-name">{{ item.name }}</strong>
              <span class="cart-item-sku">{{ item.sku }}</span>
              <span class="cart-item-unit-price">{{ formatLinePrice(item.price) }} c/u</span>
            </div>

            <div class="cart-item-controls">
              <button
                class="qty-btn"
                :disabled="submitting"
                @click="shopCart.changeQty(item.id, -1)"
              >−</button>
              <span class="qty-value">{{ item.qty }}</span>
              <button
                class="qty-btn"
                :disabled="submitting || !shopCart.canAddProduct(item)"
                @click="shopCart.changeQty(item.id, 1)"
              >+</button>
            </div>

            <div class="cart-item-line-total">
              {{ formatLinePrice(item.price * item.qty) }}
            </div>

            <button
              class="cart-item-remove"
              :disabled="submitting"
              aria-label="Eliminar producto"
              @click="shopCart.removeItem(item.id)"
            >
              <i class="fas fa-trash"></i>
            </button>
          </article>
        </section>

        <aside class="cart-page-summary">
          <div class="cart-summary-card">
            <h2 class="cart-summary-title">Resumen del pedido</h2>

            <div class="summary-rows">
              <div class="summary-row">
                <span>Productos</span>
                <strong>{{ totals.itemsCount }}</strong>
              </div>
              <div class="summary-row">
                <span>Subtotal</span>
                <strong>{{ formatSummary(totals.productsSubtotal) }}</strong>
              </div>
              <div class="summary-row">
                <span>Despacho</span>
                <strong>{{ currentShipping.name }}</strong>
              </div>
              <div class="summary-row summary-row--total">
                <span>Total</span>
                <strong>{{ formatSummary(totals.grandTotal) }}</strong>
              </div>
            </div>

            <p v-if="feedbackError" class="cart-feedback cart-feedback--error">{{ feedbackError }}</p>
            <p v-if="feedbackSuccess" class="cart-feedback cart-feedback--success">{{ feedbackSuccess }}</p>

            <button
              class="btn-checkout"
              :disabled="submitting || items.length === 0"
              @click="handleCheckout"
            >
              <i class="fas fa-paper-plane"></i>
              {{ submitting ? 'Enviando...' : 'Enviar solicitud' }}
            </button>

            <button
              class="btn-clear-cart"
              :disabled="submitting"
              @click="shopCart.clear()"
            >
              <i class="fas fa-trash"></i> Vaciar carrito
            </button>
          </div>
        </aside>

      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useShopCartStore } from '@/stores/shopCart'
import { formatStoreLinePrice, formatStoreSummaryAmount } from '@/services/storeCatalogService'

const shopCart = useShopCartStore()

const feedbackError = ref('')
const feedbackSuccess = ref('')

const items = computed(() => shopCart.items)
const totals = computed(() => shopCart.totals)
const currentShipping = computed(() => shopCart.currentShipping)
const submitting = computed(() => shopCart.submitting)

function formatLinePrice(value) {
  return formatStoreLinePrice(value)
}

function formatSummary(value) {
  return formatStoreSummaryAmount(value, totals.value)
}

async function handleCheckout() {
  feedbackError.value = ''
  feedbackSuccess.value = ''
  try {
    await shopCart.submitRequest()
    feedbackSuccess.value = 'Solicitud enviada. El taller se pondrá en contacto contigo.'
  } catch (err) {
    feedbackError.value = err?.response?.data?.detail || err?.message || 'Error al enviar la solicitud.'
  }
}

onMounted(() => {
  shopCart.hydrate()
})
</script>

<style scoped>
.cart-page {
  min-height: 100vh;
  background: var(--cds-background-color);
  padding-block: var(--cds-space-2xl);
}

.cart-page-inner {
  display: grid;
  gap: var(--cds-space-xl);
}

/* ── Header ──────────────────────────────────────────────── */
.cart-page-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: var(--cds-space-md);
  flex-wrap: wrap;
}

.cart-page-title {
  margin: 0;
  font-size: clamp(1.6rem, 1.4rem + 1vw, 2.2rem);
  color: var(--cds-dark);
  line-height: 1.1;
  letter-spacing: -0.03em;
}

.cart-back-link {
  display: inline-flex;
  align-items: center;
  gap: var(--cds-space-xs);
  font-size: var(--cds-text-sm, 0.9rem);
  color: var(--cds-text-muted);
  text-decoration: none;
  transition: color 0.15s;
}

.cart-back-link:hover {
  color: var(--cds-primary);
}

/* ── Estado vacío ────────────────────────────────────────── */
.cart-page-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--cds-space-md);
  padding: var(--cds-space-2xl) 0;
  color: var(--cds-text-muted);
  text-align: center;
}

.cart-empty-icon {
  font-size: 3rem;
  opacity: 0.4;
}

.cart-page-empty p {
  margin: 0;
  font-size: var(--cds-text-lg, 1.1rem);
}

.btn-to-store {
  display: inline-flex;
  align-items: center;
  gap: var(--cds-space-xs);
  min-height: 44px;
  padding: var(--cds-space-sm) var(--cds-space-lg);
  border-radius: var(--cds-radius-pill);
  background: var(--cds-primary);
  color: var(--cds-white);
  font-weight: var(--cds-font-semibold);
  text-decoration: none;
  transition: background 0.15s;
}

.btn-to-store:hover {
  background: var(--cds-primary-hover);
}

/* ── Layout principal ────────────────────────────────────── */
.cart-page-layout {
  display: grid;
  gap: var(--cds-space-xl);
  align-items: start;
}

@media (min-width: 900px) {
  .cart-page-layout {
    grid-template-columns: 1fr minmax(280px, 340px);
  }
}

/* ── Items ───────────────────────────────────────────────── */
.cart-page-items {
  display: grid;
  gap: var(--cds-space-sm);
}

.cart-page-item {
  display: grid;
  grid-template-columns: 88px 1fr auto auto auto;
  align-items: center;
  gap: var(--cds-space-md);
  padding: var(--cds-space-md);
  background: var(--cds-surface-1);
  border: 1px solid var(--cds-border-card);
  border-radius: var(--cds-radius-lg);
  box-shadow: var(--cds-shadow-sm);
}

@media (max-width: 640px) {
  .cart-page-item {
    grid-template-columns: 72px 1fr;
    grid-template-rows: auto auto;
  }

  .cart-item-controls,
  .cart-item-line-total,
  .cart-item-remove {
    grid-column: 2;
  }
}

/* Imagen */
.cart-item-img-wrap {
  width: 88px;
  height: 88px;
  flex-shrink: 0;
  border-radius: var(--cds-radius-md);
  overflow: hidden;
  background: var(--cds-white);
  border: 1px solid var(--cds-border-card);
  display: flex;
  align-items: center;
  justify-content: center;
}

.cart-item-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.cart-item-img-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: var(--cds-border-card);
}

/* Info */
.cart-item-info {
  display: flex;
  flex-direction: column;
  gap: var(--cds-space-2xs);
  min-width: 0;
}

.cart-item-name {
  font-size: clamp(0.95rem, 0.9rem + 0.22vw, 1.06rem);
  color: var(--cds-dark);
  line-height: 1.2;
  letter-spacing: -0.01em;
}

.cart-item-sku,
.cart-item-unit-price {
  font-size: 0.82rem;
  color: var(--cds-text-muted);
  line-height: 1.4;
}

/* Controles qty */
.cart-item-controls {
  display: flex;
  align-items: center;
  gap: var(--cds-space-xs);
}

.qty-btn {
  width: 34px;
  height: 34px;
  border: 1px solid var(--cds-border-input);
  border-radius: var(--cds-radius-sm);
  background: var(--cds-surface-1);
  color: var(--cds-dark);
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s;
}

.qty-btn:hover:not(:disabled) {
  background: var(--cds-surface-2);
}

.qty-btn:disabled {
  opacity: 0.45;
  cursor: default;
}

.qty-value {
  min-width: 28px;
  text-align: center;
  font-weight: 700;
  font-size: 1rem;
  color: var(--cds-dark);
}

/* Total línea */
.cart-item-line-total {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--cds-dark);
  white-space: nowrap;
}

/* Eliminar */
.cart-item-remove {
  width: 34px;
  height: 34px;
  border: 1px solid var(--cds-invalid-border);
  border-radius: var(--cds-radius-sm);
  background: transparent;
  color: var(--cds-invalid-text);
  font-size: 0.85rem;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s, color 0.15s;
}

.cart-item-remove:hover:not(:disabled) {
  background: var(--cds-invalid-border);
  color: var(--cds-white);
}

.cart-item-remove:disabled {
  opacity: 0.45;
  cursor: default;
}

/* ── Summary card ────────────────────────────────────────── */
.cart-page-summary {
  position: sticky;
  top: calc(var(--cds-navbar-height, 71px) + var(--cds-space-md));
}

.cart-summary-card {
  display: flex;
  flex-direction: column;
  gap: var(--cds-space-md);
  padding: var(--cds-space-xl) var(--cds-space-lg);
  background: var(--cds-surface-1);
  border: 1px solid var(--cds-border-card);
  border-radius: var(--cds-radius-lg);
  box-shadow: var(--cds-shadow-md);
}

.cart-summary-title {
  margin: 0;
  font-size: clamp(1.05rem, 1rem + 0.3vw, 1.22rem);
  color: var(--cds-dark);
  letter-spacing: -0.01em;
  line-height: 1.1;
}

.summary-rows {
  display: flex;
  flex-direction: column;
  gap: var(--cds-space-xs);
}

.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: var(--cds-space-md);
  font-size: 0.92rem;
  color: var(--cds-dark);
  line-height: 1.5;
}

.summary-row--total {
  padding-top: var(--cds-space-xs);
  border-top: 1px solid var(--cds-border-card);
  font-size: 1rem;
  font-weight: 700;
}

/* Feedback */
.cart-feedback {
  margin: 0;
  padding: var(--cds-space-sm) var(--cds-space-md);
  border-radius: var(--cds-radius-sm);
  font-size: 0.88rem;
  line-height: 1.5;
}

.cart-feedback--error {
  background: var(--cds-invalid-bg);
  color: var(--cds-invalid-text);
  border: 1px solid var(--cds-invalid-border);
}

.cart-feedback--success {
  background: var(--cds-valid-bg);
  color: var(--cds-valid-text);
  border: 1px solid var(--cds-valid-border);
}

/* Botones */
.btn-checkout {
  width: 100%;
  min-height: 44px;
  padding: var(--cds-space-sm) var(--cds-space-md);
  border: none;
  border-radius: var(--cds-radius-sm);
  background: var(--cds-primary);
  color: var(--cds-white);
  font-size: 0.95rem;
  font-weight: 700;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--cds-space-xs);
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
  min-height: 38px;
  padding: var(--cds-space-xs) var(--cds-space-md);
  border: 1px solid var(--cds-invalid-border);
  border-radius: var(--cds-radius-sm);
  background: transparent;
  color: var(--cds-invalid-text);
  font-size: 0.85rem;
  font-weight: var(--cds-font-semibold);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--cds-space-xs);
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
</style>
