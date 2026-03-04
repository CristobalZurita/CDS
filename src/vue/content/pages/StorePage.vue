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
          <label for="store-availability">Disponibilidad</label>
          <select
            id="store-availability"
            v-model="selectedAvailability"
            class="form-select"
            data-testid="store-availability-filter"
          >
            <option value="all">Todo</option>
            <option value="sellable">Vendibles ahora</option>
            <option value="reserved">Reservados para taller</option>
            <option value="out">Sin stock</option>
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

      <div class="store-summary" data-testid="store-results-count">
        Mostrando {{ filteredProducts.length }} de {{ catalog.length }} productos publicados.
      </div>

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
                  Sin stock
                </span>
                <span v-else-if="Number(product.sellable_stock || 0) <= 0" class="stock-badge stock-badge--warning">
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
const selectedAvailability = ref('all')
const router = useRouter()
const authStore = useAuthStore()
const shopCart = useShopCartStore()
const shippingOptions = shopCart.shippingOptions

const selectedShippingKey = computed({
  get: () => shopCart.selectedShippingKey,
  set: (value) => shopCart.setShippingKey(value),
})

function normalizeSearchText(value) {
  return String(value || '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[_-]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
}

const indexedCatalog = computed(() => {
  return catalog.value.map((product) => ({
    ...product,
    _searchIndex: normalizeSearchText([
      product.name,
      product.sku,
      product.family,
      product.category,
      describeProduct(product),
    ]
      .filter(Boolean)
      .join(' ')),
  }))
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
  const normalizedSearch = normalizeSearchText(searchTerm.value)

  return indexedCatalog.value.filter((product) => {
    if (selectedCategory.value && product.category !== selectedCategory.value) {
      return false
    }

    if (selectedAvailability.value === 'sellable' && Number(product.sellable_stock || 0) <= 0) {
      return false
    }
    if (selectedAvailability.value === 'reserved' && !(Number(product.available_stock || 0) > 0 && Number(product.sellable_stock || 0) <= 0)) {
      return false
    }
    if (selectedAvailability.value === 'out' && Number(product.available_stock || 0) > 0) {
      return false
    }

    if (!normalizedSearch) {
      return true
    }

    return product._searchIndex.includes(normalizedSearch)
  })
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
  if (value.startsWith('/images/')) return value
  const base = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'
  const host = base.includes('/api/') ? base.split('/api/')[0] : base
  return `${host}${value.startsWith('/') ? '' : '/'}${value}`
}

function canAddProduct(product) {
  return shopCart.canAddProduct(product)
}

function addButtonLabel(product) {
  if (!canAddProduct(product)) {
    if (Number(product.available_stock || 0) <= 0) {
      return 'Sin stock'
    }
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
        limit: 5000,
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

<style scoped lang="scss">
@use "@/scss/_core.scss" as *;

.store-page {
  min-height: 100vh;
  padding: clamp(1rem, 3vw, 2rem);
  background:
    radial-gradient(circle at top left, color-mix(in srgb, var(--color-primary) 16%, transparent) 0, transparent 32%),
    linear-gradient(180deg, #f6f2ea 0%, #ede7dc 100%);
}

.store-shell {
  width: min(100%, 1440px);
  margin: 0 auto;
  display: grid;
  gap: var(--spacer-md);
}

.store-header,
.header-actions,
.product-footer,
.cart-header,
.cart-item-actions,
.summary-row {
  display: flex;
  gap: var(--spacer-sm);
  flex-wrap: wrap;
}

.store-header,
.cart-header,
.summary-row {
  align-items: center;
  justify-content: space-between;
}

.store-header,
.store-toolbar,
.catalog-panel,
.cart-panel,
.store-summary,
.alert {
  padding: var(--spacer-md);
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(211, 208, 195, 0.8);
  border-radius: 22px;
  box-shadow: var(--shadow-sm);
}

.store-header h1,
.cart-header h2,
.product-body h2 {
  margin: 0;
  color: var(--color-dark);
  font-weight: 700;
}

.store-header h1 {
  font-size: clamp(2rem, 4vw, 3rem);
}

.subtitle,
.store-summary,
.cart-note {
  margin: 0;
  color: var(--color-dark);
  opacity: 0.78;
  font-size: var(--text-sm);
}

.subtitle {
  margin-top: 0.65rem;
  max-width: 58rem;
  line-height: 1.65;
}

.eyebrow,
.product-family,
.request-subtitle {
  margin: 0 0 0.4rem;
  color: var(--color-primary);
  font-size: var(--text-xs);
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.header-actions {
  align-items: center;
}

.btn,
.qty-btn,
.remove-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 40px;
  padding: 0.65rem 0.95rem;
  border-radius: var(--radius-sm);
  border: 1px solid transparent;
  font-size: var(--text-sm);
  font-weight: 700;
  cursor: pointer;
  transition: var(--transition-base);
  text-decoration: none;
}

.btn:hover:not(:disabled),
.qty-btn:hover:not(:disabled),
.remove-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.btn:disabled,
.qty-btn:disabled,
.remove-btn:disabled {
  opacity: 0.6;
  cursor: wait;
}

.btn-primary {
  background: var(--color-primary);
  color: var(--color-white);
}

.btn-outline-primary {
  border-color: var(--color-primary);
  background: transparent;
  color: var(--color-primary);
}

.btn-outline-secondary {
  border-color: var(--color-dark);
  background: transparent;
  color: var(--color-dark);
}

.store-toolbar {
  display: grid;
  gap: var(--spacer-sm);
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.toolbar-field {
  display: grid;
  gap: 0.35rem;
}

.toolbar-field label {
  color: var(--color-dark);
  font-size: var(--text-sm);
  font-weight: 700;
}

.form-control,
.form-select {
  width: 100%;
  min-height: 44px;
  padding: 0.75rem 0.85rem;
  border: 1px solid var(--color-light);
  border-radius: var(--radius-sm);
  background: var(--color-white);
  color: var(--color-dark);
  font-size: var(--text-sm);
}

.alert {
  color: var(--color-dark);
  background: color-mix(in srgb, var(--color-white) 86%, var(--color-warning) 14%);
}

.store-layout {
  display: grid;
  gap: var(--spacer-md);
  grid-template-columns: minmax(0, 1.7fr) minmax(320px, 0.95fr);
  align-items: start;
}

.catalog-state,
.cart-empty {
  min-height: 220px;
  display: grid;
  place-items: center;
  text-align: center;
  color: var(--color-dark);
  opacity: 0.72;
}

.products-grid {
  display: grid;
  gap: var(--spacer-md);
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
}

.product-card {
  display: grid;
  min-height: 100%;
  overflow: hidden;
  border: 1px solid rgba(211, 208, 195, 0.85);
  border-radius: 18px;
  background: var(--color-white);
  box-shadow: var(--shadow-sm);
}

.product-visual {
  position: relative;
  min-height: 220px;
  background: linear-gradient(180deg, rgba(236, 107, 0, 0.08) 0%, rgba(211, 208, 195, 0.2) 100%);
}

.product-image,
.product-placeholder {
  width: 100%;
  height: 100%;
}

.product-image {
  object-fit: cover;
}

.product-placeholder {
  display: grid;
  place-items: center;
  color: var(--color-dark);
  font-size: clamp(2rem, 5vw, 3rem);
  font-weight: 700;
}

.stock-badge {
  position: absolute;
  top: 0.75rem;
  left: 0.75rem;
  display: inline-flex;
  align-items: center;
  min-height: 30px;
  padding: 0.2rem 0.7rem;
  border-radius: 999px;
  background: var(--color-primary);
  color: var(--color-white);
  font-size: var(--text-xs);
  font-weight: 700;
}

.stock-badge--warning {
  background: var(--color-warning);
  color: var(--color-dark);
}

.product-body {
  display: grid;
  gap: 0.65rem;
  padding: 1rem;
}

.product-sku,
.cart-item-copy span,
.cart-item-copy small {
  color: var(--color-dark);
  opacity: 0.72;
  font-size: var(--text-sm);
}

.product-description {
  margin: 0;
  color: var(--color-dark);
  font-size: var(--text-sm);
  line-height: 1.6;
}

.product-footer {
  align-items: flex-end;
  justify-content: space-between;
  margin-top: auto;
}

.price-block {
  display: grid;
  gap: 0.2rem;
}

.price-block strong,
.qty-value,
.cart-count {
  color: var(--color-dark);
  font-size: var(--text-lg);
  font-weight: 700;
}

.price-block small {
  color: var(--color-dark);
  opacity: 0.7;
}

.cart-panel {
  position: sticky;
  top: 1.25rem;
  display: grid;
  gap: var(--spacer-md);
}

.cart-count {
  display: inline-flex;
  align-items: center;
  min-height: 40px;
  padding: 0.35rem 0.8rem;
  border-radius: 999px;
  background: color-mix(in srgb, var(--color-primary) 16%, var(--color-white) 84%);
}

.cart-list {
  display: grid;
  gap: var(--spacer-sm);
}

.cart-item {
  display: grid;
  gap: var(--spacer-sm);
  padding: 0.9rem;
  border: 1px solid var(--color-light);
  border-radius: var(--radius-sm);
}

.cart-item-copy {
  display: grid;
  gap: 0.2rem;
}

.cart-item-actions {
  align-items: center;
}

.qty-btn {
  min-width: 42px;
  padding-inline: 0;
  border-color: var(--color-light);
  background: var(--color-white);
  color: var(--color-dark);
}

.remove-btn {
  border-color: var(--color-danger);
  background: transparent;
  color: var(--color-danger);
}

.cart-summary {
  display: grid;
  gap: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid var(--color-light);
}

.summary-row {
  color: var(--color-dark);
  font-size: var(--text-sm);
}

.summary-row--total {
  padding-top: 0.5rem;
  border-top: 1px solid var(--color-light);
  font-size: var(--text-base);
}

.w-100 {
  width: 100%;
}

.cart-note code,
.subtitle code {
  padding: 0.15rem 0.35rem;
  border-radius: var(--radius-sm);
  background: color-mix(in srgb, var(--color-white) 70%, var(--color-light) 30%);
}

@include media-breakpoint-down(lg) {
  .store-toolbar,
  .store-layout {
    grid-template-columns: 1fr 1fr;
  }
}

@include media-breakpoint-down(md) {
  .store-header,
  .header-actions,
  .product-footer,
  .cart-header,
  .cart-item-actions,
  .summary-row {
    flex-direction: column;
    align-items: stretch;
  }

  .store-toolbar,
  .store-layout {
    grid-template-columns: 1fr;
  }

  .btn,
  .qty-btn,
  .remove-btn,
  .cart-panel {
    width: 100%;
  }
}
</style>
