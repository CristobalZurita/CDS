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
