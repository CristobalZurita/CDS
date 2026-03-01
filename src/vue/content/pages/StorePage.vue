<template>
  <div class="store-page">
    <div class="store-shell">
      <header class="store-header">
        <div>
          <p class="eyebrow">Catalogo publico</p>
          <h1>Tienda tecnica de repuestos</h1>
          <p class="subtitle">
            Catalogo real basado en <code>products</code>. La logica de lista tecnica ya vive en el
            front actual. El pedido backend y el pago real siguen pendientes.
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

                <span v-if="Number(product.available_stock || 0) <= 0" class="stock-badge stock-badge--warning">
                  Sin stock local
                </span>
                <span v-else-if="product.is_low_stock" class="stock-badge stock-badge--warning">
                  Stock bajo
                </span>
                <span v-else class="stock-badge">
                  {{ product.available_stock }} {{ product.stock_unit || 'u' }}
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
                  :disabled="item.qty >= Number(item.available_stock || 0)"
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
            :disabled="cartItems.length === 0"
            @click="showCheckoutPending"
          >
            Solicitud backend pendiente
          </button>

          <p class="cart-note">
            Este primer slice ya usa catalogo real y lista tecnica real del front.
            La siguiente capa es solicitud backend y luego pago real.
          </p>
        </aside>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { api } from '@/services/api'
import { showInfo, showSuccess, showWarning } from '@/services/toastService'

const CART_STORAGE_KEY = 'cirujano-shop-cart-v1'
const SHIPPING_STORAGE_KEY = 'cirujano-shop-shipping-v1'
const MAX_QTY_PER_PRODUCT = 20

const shippingOptions = [
  { key: 'pickup', name: 'Retiro en taller', price: 0 },
  { key: 'manual', name: 'Despacho coordinado manualmente', price: 0 },
]

const catalog = ref([])
const loading = ref(false)
const error = ref('')
const searchTerm = ref('')
const selectedCategory = ref('')
const selectedShippingKey = ref(shippingOptions[0].key)
const cart = ref({})

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

const cartItems = computed(() => {
  return Object.entries(cart.value)
    .map(([id, qty]) => {
      const product = catalogById.value.get(String(id))
      if (!product) return null
      return {
        ...product,
        qty: normalizeQty(qty),
      }
    })
    .filter(Boolean)
})

const currentShipping = computed(() => {
  return shippingOptions.find((option) => option.key === selectedShippingKey.value) || shippingOptions[0]
})

const totals = computed(() => {
  const productsSubtotal = cartItems.value.reduce((sum, item) => sum + (Number(item.price || 0) * item.qty), 0)
  const itemsCount = cartItems.value.reduce((sum, item) => sum + item.qty, 0)
  const shippingPrice = Number(currentShipping.value.price || 0)
  const hasQuotedAmount = cartItems.value.some((item) => Number(item.price || 0) > 0)

  return {
    itemsCount,
    productsSubtotal,
    shippingPrice,
    grandTotal: productsSubtotal + shippingPrice,
    hasQuotedAmount,
  }
})

function normalizeQty(value) {
  const qty = Number(value)
  if (!Number.isFinite(qty)) return 0
  return Math.min(MAX_QTY_PER_PRODUCT, Math.max(0, Math.floor(qty)))
}

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
  const currentQty = normalizeQty(cart.value[String(product.id)] || 0)
  return currentQty < MAX_QTY_PER_PRODUCT
}

function addButtonLabel(product) {
  if (!canAddProduct(product)) {
    return 'No disponible'
  }
  if (Number(product.available_stock || 0) > 0 && Number(product.price || 0) > 0) {
    return 'Agregar'
  }
  return 'Agregar a lista'
}

function addToCart(product) {
  if (!product || !canAddProduct(product)) {
    showWarning('Este item todavia no se puede agregar desde el catalogo actual.')
    return
  }

  const id = String(product.id)
  const nextQty = normalizeQty((cart.value[id] || 0) + 1)
  cart.value = {
    ...cart.value,
    [id]: nextQty,
  }
  showSuccess(`${product.name} agregado al carrito.`)
}

function removeFromCart(productId) {
  const id = String(productId)
  if (!(id in cart.value)) return

  const next = { ...cart.value }
  delete next[id]
  cart.value = next
}

function changeQty(productId, delta) {
  const id = String(productId)
  const currentQty = normalizeQty(cart.value[id] || 0)
  const nextQty = Math.min(MAX_QTY_PER_PRODUCT, normalizeQty(currentQty + delta))

  if (nextQty <= 0) {
    removeFromCart(productId)
    return
  }

  cart.value = {
    ...cart.value,
    [id]: nextQty,
  }
}

function hydrateCart() {
  try {
    const raw = window.localStorage.getItem(CART_STORAGE_KEY)
    if (!raw) return
    const parsed = JSON.parse(raw)
    if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) return

    const next = {}
    for (const [id, qty] of Object.entries(parsed)) {
      const normalized = normalizeQty(qty)
      if (normalized > 0) {
        next[String(id)] = normalized
      }
    }
    cart.value = next
  } catch {
    cart.value = {}
  }
}

function hydrateShipping() {
  try {
    const raw = window.localStorage.getItem(SHIPPING_STORAGE_KEY)
    if (!raw) return
    const value = String(JSON.parse(raw) || '')
    if (shippingOptions.some((option) => option.key === value)) {
      selectedShippingKey.value = value
    }
  } catch {
    selectedShippingKey.value = shippingOptions[0].key
  }
}

function persistCart() {
  try {
    window.localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(cart.value))
  } catch {
    // noop
  }
}

function persistShipping() {
  try {
    window.localStorage.setItem(SHIPPING_STORAGE_KEY, JSON.stringify(selectedShippingKey.value))
  } catch {
    // noop
  }
}

function cleanupCartAgainstCatalog() {
  const validIds = new Set(catalog.value.map((product) => String(product.id)))
  const next = {}
  for (const [id, qty] of Object.entries(cart.value)) {
    if (validIds.has(String(id)) && normalizeQty(qty) > 0) {
      next[String(id)] = normalizeQty(qty)
    }
  }
  cart.value = next
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
    cleanupCartAgainstCatalog()
  } catch (err) {
    error.value = err?.response?.data?.detail || 'No se pudo cargar el catalogo publico.'
    catalog.value = []
  } finally {
    loading.value = false
  }
}

function showCheckoutPending() {
  showInfo('La solicitud backend y el pago real todavia no estan conectados. Este slice deja catalogo y lista tecnica listos sobre datos reales.')
}

watch(cart, persistCart, { deep: true })
watch(selectedShippingKey, persistShipping)

onMounted(async () => {
  hydrateCart()
  hydrateShipping()
  await loadCatalog()
})
</script>

<style lang="scss" scoped>
@use "@/scss/_core.scss" as *;

.store-page {
  min-height: 100vh;
  background:
    radial-gradient(circle at top left, rgba($primary, 0.12), transparent 30%),
    radial-gradient(circle at top right, rgba($success, 0.10), transparent 25%),
    linear-gradient(180deg, $light-1 0%, $light-2 100%);
  padding: $spacer-xl $spacer-md;
}

.store-shell {
  max-width: 1440px;
  margin: 0 auto;
}

.store-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: $spacer-lg;
  padding: $spacer-xl;
  margin-bottom: $spacer-lg;
  border-radius: $border-radius-lg;
  background: rgba($color-white, 0.88);
  box-shadow: $shadow-md;
  backdrop-filter: blur(10px);
}

.eyebrow {
  margin: 0 0 $spacer-xs;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-weight: $fw-bold;
  color: $primary;
}

.store-header h1 {
  margin: 0 0 $spacer-sm;
  color: $color-dark;
}

.subtitle {
  margin: 0;
  max-width: 62ch;
  color: $light-6;
}

.header-actions {
  display: flex;
  gap: $spacer-sm;
  flex-wrap: wrap;
}

.store-toolbar {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: $spacer-md;
  padding: $spacer-lg;
  margin-bottom: $spacer-lg;
  border-radius: $border-radius-lg;
  background: rgba($color-white, 0.92);
  box-shadow: $shadow-sm;
}

.toolbar-field {
  display: flex;
  flex-direction: column;
  gap: $spacer-xs;
}

.toolbar-field label {
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-weight: $fw-bold;
  color: $light-7;
}

.store-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.75fr) minmax(320px, 420px);
  gap: $spacer-lg;
  align-items: start;
}

.catalog-panel,
.cart-panel {
  padding: $spacer-lg;
  border-radius: $border-radius-lg;
  background: rgba($color-white, 0.92);
  box-shadow: $shadow-md;
}

.catalog-state,
.cart-empty {
  padding: $spacer-xl;
  border-radius: $border-radius-md;
  background: rgba($light-3, 0.4);
  color: $light-7;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: $spacer-md;
}

.product-card {
  display: flex;
  flex-direction: column;
  border: 1px solid rgba($color-black, 0.08);
  border-radius: $border-radius-lg;
  overflow: hidden;
  background: linear-gradient(180deg, rgba($color-white, 0.98), rgba($light-2, 0.9));
}

.product-visual {
  position: relative;
  min-height: 180px;
  display: flex;
  align-items: center;
  justify-content: center;
  background:
    linear-gradient(135deg, rgba($primary, 0.1), rgba($success, 0.08)),
    $light-2;
  border-bottom: 1px solid rgba($color-black, 0.06);
}

.product-image {
  max-width: 100%;
  max-height: 180px;
  object-fit: contain;
}

.product-placeholder {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 84px;
  height: 84px;
  border-radius: 50%;
  background: rgba($primary, 0.12);
  color: $primary;
  font-weight: $fw-extrabold;
  letter-spacing: 0.08em;
}

.stock-badge {
  position: absolute;
  top: $spacer-sm;
  right: $spacer-sm;
  padding: 0.3rem 0.6rem;
  border-radius: 999px;
  background: rgba($success, 0.12);
  color: darken($success, 15%);
  font-size: 0.8rem;
  font-weight: $fw-bold;
}

.stock-badge--warning {
  background: rgba($primary, 0.14);
  color: darken($primary, 18%);
}

.product-body {
  display: flex;
  flex-direction: column;
  gap: $spacer-sm;
  padding: $spacer-lg;
  flex: 1;
}

.product-family,
.product-sku {
  margin: 0;
  font-size: 0.88rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: $light-7;
}

.product-body h2 {
  margin: 0;
  font-size: 1.15rem;
  line-height: 1.3;
  color: $color-dark;
}

.product-description {
  margin: 0;
  color: $light-7;
  font-size: 0.95rem;
}

.product-footer {
  margin-top: auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: $spacer-sm;
}

.price-block {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}

.price-block strong {
  color: $color-dark;
}

.price-block small {
  color: $light-7;
}

.cart-panel {
  position: sticky;
  top: calc(var(--navbar-height, 120px) + 1rem);
}

.cart-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: $spacer-sm;
  padding-bottom: $spacer-md;
  border-bottom: 1px solid rgba($color-black, 0.08);
}

.cart-header h2 {
  margin: 0;
}

.cart-count {
  color: $light-7;
  font-weight: $fw-bold;
}

.cart-list {
  display: flex;
  flex-direction: column;
  gap: $spacer-sm;
  margin: $spacer-lg 0;
}

.cart-item {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: $spacer-sm;
  padding: $spacer-md;
  border-radius: $border-radius-md;
  background: rgba($light-2, 0.75);
}

.cart-item-copy {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.cart-item-copy span,
.cart-item-copy small {
  color: $light-7;
}

.cart-item-actions {
  display: flex;
  align-items: center;
  gap: 0.35rem;
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

.cart-summary {
  display: flex;
  flex-direction: column;
  gap: $spacer-sm;
  margin: $spacer-lg 0;
  padding: $spacer-md 0;
  border-top: 1px solid rgba($color-black, 0.08);
  border-bottom: 1px solid rgba($color-black, 0.08);
}

.summary-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: $spacer-sm;
}

.summary-row--total {
  padding-top: $spacer-xs;
  font-size: 1.05rem;
}

.cart-note {
  margin: $spacer-sm 0 0;
  color: $light-7;
  font-size: 0.92rem;
}

@media (max-width: 1080px) {
  .store-layout {
    grid-template-columns: 1fr;
  }

  .cart-panel {
    position: static;
  }
}

@media (max-width: 768px) {
  .store-page {
    padding: $spacer-lg $spacer-sm;
  }

  .store-header,
  .store-toolbar {
    grid-template-columns: 1fr;
    display: grid;
  }

  .store-header {
    padding: $spacer-lg;
  }

  .header-actions {
    justify-content: flex-start;
  }

  .cart-item {
    grid-template-columns: 1fr;
  }

  .cart-item-actions {
    justify-content: flex-start;
    flex-wrap: wrap;
  }
}
</style>
