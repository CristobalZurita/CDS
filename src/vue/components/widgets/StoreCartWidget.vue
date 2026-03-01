<template>
  <div v-if="shouldRender" class="store-cart-widget">
    <button
      class="cart-trigger"
      type="button"
      data-testid="global-cart-trigger"
      :aria-expanded="String(isOpen)"
      @click="isOpen = !isOpen"
    >
      <span class="cart-trigger__icon">
        <i class="fa-solid fa-cart-shopping"></i>
      </span>
      <span class="cart-trigger__copy">
        <strong>{{ itemCountLabel }}</strong>
        <small>{{ totalLabel }}</small>
      </span>
    </button>

    <aside
      v-if="isOpen"
      class="cart-panel"
      data-testid="global-cart-panel"
    >
      <header class="cart-panel__header">
        <div>
          <p class="eyebrow">Carro global</p>
          <h2>Tu lista técnica</h2>
        </div>
        <button class="panel-close" type="button" aria-label="Cerrar carrito" @click="isOpen = false">
          <i class="fa-solid fa-xmark"></i>
        </button>
      </header>

      <div v-if="cart.items.length === 0" class="cart-empty" data-testid="global-cart-empty">
        <p>No tienes repuestos agregados todavía.</p>
        <router-link class="btn btn-outline-primary btn-sm" to="/tienda" @click="isOpen = false">
          Ir a tienda
        </router-link>
      </div>

      <template v-else>
        <div class="cart-list">
          <article
            v-for="item in cart.items"
            :key="item.id"
            class="cart-item"
            data-testid="global-cart-item"
          >
            <div class="cart-item__copy">
              <strong>{{ item.name }}</strong>
              <span>{{ item.sku }}</span>
              <small>{{ formatLinePrice(item.price) }} c/u</small>
            </div>

            <div class="cart-item__actions">
              <button class="qty-btn" type="button" @click="cart.changeQty(item.id, -1)">-</button>
              <span class="qty-value">{{ item.qty }}</span>
              <button
                class="qty-btn"
                type="button"
                :disabled="!cart.canAddProduct(item)"
                @click="cart.changeQty(item.id, 1)"
              >
                +
              </button>
              <button class="remove-btn" type="button" @click="cart.removeItem(item.id)">Quitar</button>
            </div>
          </article>
        </div>

        <div class="shipping-block">
          <label for="global-cart-shipping">Despacho</label>
          <select
            id="global-cart-shipping"
            class="form-select form-select-sm"
            data-testid="global-cart-shipping-select"
            :value="cart.selectedShippingKey"
            @change="cart.setShippingKey($event.target.value)"
          >
            <option
              v-for="option in cart.shippingOptions"
              :key="option.key"
              :value="option.key"
            >
              {{ option.name }}
            </option>
          </select>
        </div>

        <div class="cart-summary">
          <div class="summary-row">
            <span>Items</span>
            <strong>{{ cart.totals.itemsCount }}</strong>
          </div>
          <div class="summary-row">
            <span>Subtotal</span>
            <strong>{{ formatSummaryAmount(cart.totals.productsSubtotal) }}</strong>
          </div>
          <div class="summary-row">
            <span>Despacho</span>
            <strong>{{ cart.currentShipping.name }}</strong>
          </div>
          <div class="summary-row summary-row--total">
            <span>Total</span>
            <strong>{{ formatSummaryAmount(cart.totals.grandTotal) }}</strong>
          </div>
        </div>

        <div class="cart-actions">
          <router-link class="btn btn-outline-secondary btn-sm" to="/tienda" @click="isOpen = false">
            Ver catálogo
          </router-link>
          <button
            class="btn btn-primary btn-sm"
            data-testid="global-cart-checkout"
            :disabled="cart.submitting"
            @click="submitCart"
          >
            {{ checkoutLabel }}
          </button>
        </div>
      </template>
    </aside>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useShopCartStore } from '@/stores/shopCart'
import { showError, showInfo, showSuccess, showWarning } from '@/services/toastService'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const cart = useShopCartStore()

const isOpen = ref(false)

const shouldRender = computed(() => !route.path.startsWith('/admin'))
const itemCountLabel = computed(() => `${cart.totals.itemsCount} item${cart.totals.itemsCount === 1 ? '' : 's'}`)
const totalLabel = computed(() => formatSummaryAmount(cart.totals.grandTotal))
const checkoutLabel = computed(() => {
  if (authStore.isAdmin) return 'Cuenta admin no compra'
  if (!authStore.isAuthenticated) return 'Inicia sesión para solicitar'
  if (cart.submitting) return 'Enviando...'
  return 'Enviar solicitud'
})

function formatCurrency(value) {
  const amount = Number(value || 0)
  return new Intl.NumberFormat('es-CL', {
    style: 'currency',
    currency: 'CLP',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount)
}

function formatLinePrice(value) {
  const amount = Number(value || 0)
  return amount > 0 ? formatCurrency(amount) : 'Por cotizar'
}

function formatSummaryAmount(value) {
  const amount = Number(value || 0)
  return cart.totals.hasQuotedAmount && amount > 0 ? formatCurrency(amount) : 'Por cotizar'
}

async function ensureAuthState() {
  if (authStore.isAuthenticated) return
  if (typeof window === 'undefined') return
  if (!window.localStorage.getItem('access_token')) return
  try {
    await authStore.checkAuth()
  } catch {
    // noop
  }
}

async function submitCart() {
  if (!cart.items.length) {
    showWarning('El carrito está vacío.')
    return
  }

  if (authStore.isAdmin) {
    showInfo('La solicitud de tienda está disponible para cuentas cliente.')
    return
  }

  if (!authStore.isAuthenticated) {
    showInfo('Inicia sesión para convertir el carrito en una solicitud real.')
    await router.push({ name: 'login', query: { redirect: route.fullPath } })
    return
  }

  try {
    const request = await cart.submitRequest()
    isOpen.value = false
    showSuccess(`Solicitud #${request?.id || ''} enviada correctamente.`)
    await router.push('/ot-payments')
  } catch (error) {
    const message = error?.response?.data?.detail || error?.message || 'No se pudo enviar la solicitud'
    showError(message)
  }
}

watch(() => route.fullPath, () => {
  if (route.path.startsWith('/admin')) {
    isOpen.value = false
  }
})

onMounted(async () => {
  cart.hydrate()
  await ensureAuthState()
})
</script>

<style scoped lang="scss">
@use "@/scss/_core.scss" as *;

.store-cart-widget {
  position: fixed;
  right: 1.5rem;
  bottom: 5.75rem;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: $spacer-sm;
}

.cart-trigger {
  display: inline-flex;
  align-items: center;
  gap: $spacer-sm;
  padding: 0.9rem 1rem;
  border: 0;
  border-radius: 999px;
  background: linear-gradient(135deg, $color-dark, lighten($color-dark, 8%));
  color: $color-white;
  box-shadow: 0 16px 36px rgba($color-black, 0.18);
}

.cart-trigger__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.6rem;
  height: 2.6rem;
  border-radius: 50%;
  background: rgba($primary, 0.22);
  color: lighten($primary, 10%);
}

.cart-trigger__copy {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  line-height: 1.1;
}

.cart-trigger__copy small {
  color: rgba($color-white, 0.74);
}

.cart-panel {
  width: min(420px, calc(100vw - 2rem));
  max-height: min(72vh, 760px);
  overflow: auto;
  padding: $spacer-lg;
  border-radius: $border-radius-lg;
  background: rgba($color-white, 0.98);
  box-shadow: 0 20px 56px rgba($color-black, 0.18);
  backdrop-filter: blur(12px);
}

.cart-panel__header,
.cart-actions,
.summary-row,
.cart-item__actions {
  display: flex;
  align-items: center;
}

.cart-panel__header,
.summary-row {
  justify-content: space-between;
}

.cart-panel__header {
  gap: $spacer-sm;
  margin-bottom: $spacer-md;
}

.eyebrow {
  margin: 0 0 $spacer-xs;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-weight: $fw-bold;
  color: $primary;
}

.cart-panel__header h2 {
  margin: 0;
}

.panel-close {
  border: 0;
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  background: rgba($color-black, 0.05);
  color: $color-dark;
}

.cart-empty {
  display: grid;
  gap: $spacer-sm;
  padding: $spacer-lg;
  border-radius: $border-radius-md;
  background: rgba($light-2, 0.8);
}

.cart-empty p {
  margin: 0;
}

.cart-list {
  display: flex;
  flex-direction: column;
  gap: $spacer-sm;
  margin-bottom: $spacer-md;
}

.cart-item {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: $spacer-sm;
  padding: $spacer-md;
  border-radius: $border-radius-md;
  background: rgba($light-2, 0.72);
}

.cart-item__copy {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.cart-item__copy span,
.cart-item__copy small {
  color: $light-7;
}

.cart-item__actions {
  gap: 0.35rem;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.qty-btn,
.remove-btn {
  border: 0;
  border-radius: $border-radius-sm;
  font-weight: $fw-bold;
}

.qty-btn {
  width: 2rem;
  height: 2rem;
  background: rgba($primary, 0.12);
  color: $primary;
}

.remove-btn {
  padding: 0.45rem 0.65rem;
  background: rgba($primary, 0.12);
  color: darken($primary, 12%);
}

.qty-value {
  min-width: 1.5rem;
  text-align: center;
  font-weight: $fw-bold;
}

.shipping-block {
  display: grid;
  gap: $spacer-xs;
  margin-bottom: $spacer-md;
}

.shipping-block label {
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-weight: $fw-bold;
  color: $light-7;
}

.cart-summary {
  display: flex;
  flex-direction: column;
  gap: $spacer-sm;
  margin-bottom: $spacer-md;
  padding: $spacer-md 0;
  border-top: 1px solid rgba($color-black, 0.08);
  border-bottom: 1px solid rgba($color-black, 0.08);
}

.summary-row--total {
  padding-top: $spacer-xs;
  font-size: 1.05rem;
}

.cart-actions {
  justify-content: space-between;
  gap: $spacer-sm;
  flex-wrap: wrap;
}

@media (max-width: 768px) {
  .store-cart-widget {
    right: 1rem;
    bottom: 4.9rem;
  }

  .cart-trigger {
    padding: 0.8rem 0.9rem;
  }

  .cart-panel {
    width: min(420px, calc(100vw - 1rem));
  }

  .cart-item {
    grid-template-columns: 1fr;
  }

  .cart-item__actions,
  .cart-actions {
    justify-content: flex-start;
  }
}
</style>
