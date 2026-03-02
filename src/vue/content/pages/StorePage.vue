<template>
  <div class="store-page">
    <div class="store-shell">
      <header class="store-header">
        <div>
          <p class="eyebrow">Catalogo publico</p>
          <h1>Tienda tecnica de repuestos</h1>
          <p class="subtitle">
            Catálogo real basado en <code>products</code>, con stock vendible protegido para taller
            y solicitud real al backend usando el mismo flujo de compras del sistema.
          </p>
        </div>
        <div class="header-actions">
          <button
            class="btn btn-outline-primary btn-sm"
            data-testid="store-refresh"
            :disabled="loading"
            @click="loadCatalog"
          >
            {{ loading ? 'Actualizando...' : 'Actualizar catalogo' }}
          </button>
          <router-link to="/" class="btn btn-outline-secondary btn-sm">
            Volver al inicio
          </router-link>
        </div>
      </header>

      <section class="store-toolbar">
        <div class="toolbar-field">
          <label for="store-search">Buscar</label>
          <input
            id="store-search"
            v-model.trim="searchTerm"
            class="form-control"
            data-testid="store-search-input"
            placeholder="SKU, nombre o familia"
            type="text"
          />
        </div>

        <div class="toolbar-field">
          <label for="store-category">Categoria</label>
          <select
            id="store-category"
            v-model="selectedCategory"
            class="form-select"
            data-testid="store-category-filter"
          >
            <option value="">Todas</option>
            <option
              v-for="category in availableCategories"
              :key="category"
              :value="category"
            >
              {{ category }}
            </option>
          </select>
        </div>

        <div class="toolbar-field">
          <label for="store-shipping">Despacho</label>
          <select
            id="store-shipping"
            v-model="selectedShippingKey"
            class="form-select"
            data-testid="store-shipping-select"
          >
            <option
              v-for="option in shippingOptions"
              :key="option.key"
              :value="option.key"
            >
              {{ option.name }}
            </option>
          </select>
        </div>
      </section>

      <div v-if="error" class="alert alert-warning" data-testid="store-error">
        {{ error }}
      </div>

      <div class="store-layout">
        <section class="catalog-panel">
          <div v-if="loading" class="catalog-state" data-testid="store-loading">
            Cargando catalogo...
          </div>

          <div v-else-if="filteredProducts.length === 0" class="catalog-state" data-testid="store-empty">
            No hay productos publicables que coincidan con el filtro actual.
          </div>

          <div v-else class="products-grid">
            <article
              v-for="product in filteredProducts"
              :key="product.id"
              class="product-card"
              data-testid="store-product-card"
            >
              <div class="product-visual">
                <img
                  v-if="product.image_url"
                  :src="toApiPath(product.image_url)"
                  :alt="product.name"
                  class="product-image"
                  loading="lazy"
                />
                <div v-else class="product-placeholder" aria-hidden="true">
                  {{ placeholderLabel(product) }}
                </div>

                <span v-if="Number(product.sellable_stock || 0) <= 0" class="stock-badge stock-badge--warning">
                  Reservado para taller
                </span>
                <span v-else-if="product.is_low_stock" class="stock-badge stock-badge--warning">
                  Stock bajo
                </span>
                <span v-else class="stock-badge">
                  {{ product.sellable_stock }} {{ product.stock_unit || 'u' }}
                </span>
              </div>

              <div class="product-body">
                <p class="product-family">{{ product.family || product.category || 'repuesto' }}</p>
                <h2>{{ product.name }}</h2>
                <p class="product-sku">{{ product.sku }}</p>
                <p class="product-description">{{ describeProduct(product) }}</p>

                <div class="product-footer">
                  <div class="price-block">
                    <strong>{{ formatCurrency(product.price) }}</strong>
                    <small>{{ product.category || 'Sin categoria' }}</small>
                  </div>

                  <button
                    class="btn btn-primary btn-sm"
                    data-testid="store-add-to-cart"
                    :disabled="!canAddProduct(product)"
                    @click="addToCart(product)"
                  >
                    {{ addButtonLabel(product) }}
                  </button>
                </div>
              </div>
            </article>
          </div>
        </section>

        <aside class="cart-panel" data-testid="store-cart">
          <header class="cart-header">
            <div>
              <p class="eyebrow">Lista tecnica</p>
              <h2>Resumen actual</h2>
            </div>
            <span class="cart-count">{{ totals.itemsCount }} items</span>
          </header>

          <div v-if="cartItems.length === 0" class="cart-empty" data-testid="store-cart-empty">
            La lista esta vacia. Puedes ir agregando repuestos del catalogo publico.
          </div>

          <div v-else class="cart-list">
            <article
              v-for="item in cartItems"
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
                <button class="qty-btn" @click="changeQty(item.id, -1)">-</button>
                <span class="qty-value">{{ item.qty }}</span>
                <button
                  class="qty-btn"
                  :disabled="!canAddProduct(item)"
                  @click="changeQty(item.id, 1)"
                >
                  +
                </button>
                <button class="remove-btn" @click="removeFromCart(item.id)">Quitar</button>
              </div>
            </article>
          </div>

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
            class="btn btn-primary w-100"
            data-testid="store-checkout"
            :disabled="cartItems.length === 0 || shopCart.submitting"
            @click="submitCheckout"
          >
            {{ checkoutLabel }}
          </button>

          <p class="cart-note">
            El carro global queda disponible al navegar por todo el sitio. Si inicias sesión como cliente,
            esta lista se convierte en una solicitud real dentro del módulo de compras.
          </p>
        </aside>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useShopCartStore } from '@/stores/shopCart'
import { api } from '@/services/api'
import { showError, showInfo, showSuccess, showWarning } from '@/services/toastService'

const catalog = ref([])
const loading = ref(false)
const error = ref('')
const searchTerm = ref('')
const selectedCategory = ref('')
const router = useRouter()
const authStore = useAuthStore()
const shopCart = useShopCartStore()
const shippingOptions = shopCart.shippingOptions

const selectedShippingKey = computed({
  get: () => shopCart.selectedShippingKey,
  set: (value) => shopCart.setShippingKey(value),
})

const availableCategories = computed(() => {
  const values = new Set(
    catalog.value
      .map((product) => String(product.category || '').trim())
      .filter(Boolean)
  )
  return Array.from(values).sort((a, b) => a.localeCompare(b, 'es'))
})

const filteredProducts = computed(() => {
  const normalizedSearch = String(searchTerm.value || '').trim().toLowerCase()

  return catalog.value.filter((product) => {
    if (selectedCategory.value && product.category !== selectedCategory.value) {
      return false
    }

    if (!normalizedSearch) {
      return true
    }

    const haystack = [
      product.name,
      product.sku,
      product.family,
      product.category,
      describeProduct(product),
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()

    return haystack.includes(normalizedSearch)
  })
})

const catalogById = computed(() => {
  const map = new Map()
  for (const product of catalog.value) {
    map.set(String(product.id), product)
  }
  return map
})

const cartItems = computed(() => shopCart.items)
const currentShipping = computed(() => shopCart.currentShipping)
const totals = computed(() => shopCart.totals)
const checkoutLabel = computed(() => {
  if (authStore.isAdmin) return 'Cuenta admin no compra'
  if (!authStore.isAuthenticated) return 'Inicia sesión para solicitar'
  if (shopCart.submitting) return 'Enviando solicitud...'
  return 'Enviar solicitud real'
})

function parseDescriptionMeta(rawDescription) {
  const text = String(rawDescription || '').trim()
  if (!text.startsWith('{')) {
    return { text }
  }

  try {
    const payload = JSON.parse(text)
    return typeof payload === 'object' && payload ? payload : {}
  } catch {
    return { text }
  }
}

function describeProduct(product) {
  const meta = parseDescriptionMeta(product.description)
  if (meta.text && meta.text !== 'Importado desde Excel (N°)') {
    return meta.text
  }

  const parts = [
    meta.family || product.family,
    meta.source,
    meta.origin_status || product.origin_status,
  ]
    .map((part) => String(part || '').replaceAll('_', ' ').trim())
    .filter(Boolean)

  return parts.join(' · ') || 'Repuesto disponible en catalogo real'
}

function placeholderLabel(product) {
  const source = String(product.family || product.category || product.sku || 'RP')
  return source.slice(0, 3).toUpperCase()
}

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
  return totals.value.hasQuotedAmount && amount > 0 ? formatCurrency(amount) : 'Por cotizar'
}

function toApiPath(path) {
  const value = String(path || '').trim()
  if (!value) return ''
  if (value.startsWith('http')) return value
  const base = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'
  const host = base.includes('/api/') ? base.split('/api/')[0] : base
  return `${host}${value.startsWith('/') ? '' : '/'}${value}`
}

function canAddProduct(product) {
  return shopCart.canAddProduct(product)
}

function addButtonLabel(product) {
  if (!canAddProduct(product)) {
    return Number(product.sellable_stock || 0) <= 0 ? 'Reservado taller' : 'No disponible'
  }
  if (Number(product.sellable_stock || 0) > 0 && Number(product.price || 0) > 0) {
    return 'Agregar'
  }
  return 'Agregar a lista'
}

function addToCart(product) {
  if (!product || !shopCart.addProduct(product)) {
    showWarning('Este item todavia no se puede agregar desde el catalogo actual.')
    return
  }
  showSuccess(`${product.name} agregado al carrito.`)
}

function removeFromCart(productId) {
  shopCart.removeItem(productId)
}

function changeQty(productId, delta) {
  shopCart.changeQty(productId, delta)
}

async function loadCatalog() {
  loading.value = true
  error.value = ''
  try {
    const res = await api.get('/inventory/public/', {
      params: {
        limit: 500,
        enabled_only: true,
        in_stock_only: false,
      },
    })
    catalog.value = Array.isArray(res?.data) ? res.data : []
    shopCart.syncCatalog(catalog.value)
  } catch (err) {
    error.value = err?.response?.data?.detail || 'No se pudo cargar el catalogo publico.'
    catalog.value = []
  } finally {
    loading.value = false
  }
}

async function submitCheckout() {
  if (!cartItems.value.length) {
    showWarning('El carrito está vacío.')
    return
  }

  if (authStore.isAdmin) {
    showInfo('La solicitud de tienda está disponible para cuentas cliente.')
    return
  }

  if (!authStore.isAuthenticated) {
    showInfo('Inicia sesión para convertir esta lista en una solicitud real.')
    await router.push({ name: 'login', query: { redirect: '/tienda' } })
    return
  }

  try {
    const request = await shopCart.submitRequest()
    showSuccess(`Solicitud #${request?.id || ''} enviada correctamente.`)
    await router.push('/ot-payments')
  } catch (err) {
    const message = err?.response?.data?.detail || err?.message || 'No se pudo enviar la solicitud'
    showError(message)
  }
}

onMounted(async () => {
  shopCart.hydrate()
  await loadCatalog()
})
</script>
