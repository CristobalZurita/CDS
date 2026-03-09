import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@new/services/api'
import { useAuth } from '@new/composables/useAuth'
import { useShopCartStore } from '@new/stores/shopCart'
import { inventoryImagePaths, instrumentImagePaths } from '@new/utils/publicImageCatalog'

const STORE_CATALOG_CACHE_KEY = 'cds_store_catalog_cache_v1'

function normalizeSearchText(value) {
  return String(value || '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[_-]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
}

function normalizeImageToken(value) {
  return normalizeSearchText(value)
    .replace(/[^a-z0-9 ]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
}

function imageStemFromPath(path) {
  const filename = String(path || '').split('/').pop() || ''
  return filename.replace(/\.[^.]+$/, '')
}

function buildImageEntries(paths) {
  return paths.map((path) => ({
    path,
    token: normalizeImageToken(imageStemFromPath(path))
  }))
}

function buildExactMap(entries) {
  return new Map(entries.map((entry) => [entry.token, entry.path]))
}

function findExactMatch(tokens, map) {
  for (const token of tokens) {
    const match = map.get(token)
    if (match) return match
  }
  return ''
}

function findLooseMatch(tokens, entries) {
  for (const token of tokens) {
    if (token.length < 3) continue
    const match = entries.find((entry) => entry.token.includes(token) || token.includes(entry.token))
    if (match) return match.path
  }
  return ''
}

const inventoryImageEntries = buildImageEntries(inventoryImagePaths)
const instrumentImageEntries = buildImageEntries(instrumentImagePaths)
const inventoryImageMap = buildExactMap(inventoryImageEntries)
const instrumentImageMap = buildExactMap(instrumentImageEntries)

function catalogImageFallback(product) {
  const tokenCandidates = Array.from(new Set(
    [product?.sku, product?.name, product?.family, product?.category]
      .map((value) => normalizeImageToken(value))
      .filter(Boolean)
  ))
  if (!tokenCandidates.length) return ''
  const inventoryExact = findExactMatch(tokenCandidates, inventoryImageMap)
  if (inventoryExact) return inventoryExact
  const instrumentExact = findExactMatch(tokenCandidates, instrumentImageMap)
  if (instrumentExact) return instrumentExact
  const inventoryLoose = findLooseMatch(tokenCandidates, inventoryImageEntries)
  if (inventoryLoose) return inventoryLoose
  return findLooseMatch(tokenCandidates, instrumentImageEntries)
}

function readCatalogCache() {
  try {
    const raw = localStorage.getItem(STORE_CATALOG_CACHE_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

function writeCatalogCache(rows) {
  try {
    localStorage.setItem(STORE_CATALOG_CACHE_KEY, JSON.stringify(Array.isArray(rows) ? rows : []))
  } catch {
    // noop
  }
}

export function useStorePage() {
  const { isAuthenticated, isAdmin } = useAuth()
  const router = useRouter()
  const shopCart = useShopCartStore()

  const catalog = ref([])
  const loading = ref(false)
  const error = ref('')
  const searchTerm = ref('')
  const selectedCategory = ref('')
  const selectedAvailability = ref('all')

  // Shipping synced to Pinia store
  const selectedShippingKey = computed({
    get: () => shopCart.selectedShippingKey,
    set: (value) => shopCart.setShippingKey(value),
  })

  const shippingOptions = shopCart.shippingOptions
  const cartItems = computed(() => shopCart.items)
  const currentShipping = computed(() => shopCart.currentShipping)
  const totals = computed(() => shopCart.totals)

  const checkoutLabel = computed(() => {
    if (isAdmin.value) return 'Cuenta admin no compra'
    if (!isAuthenticated.value) return 'Inicia sesión para solicitar'
    if (shopCart.submitting) return 'Enviando solicitud...'
    return 'Enviar solicitud'
  })

  const availableCategories = computed(() => {
    const values = new Set(
      catalog.value
        .map((product) => String(product.category || '').trim())
        .filter(Boolean)
    )
    return Array.from(values).sort((a, b) => a.localeCompare(b, 'es'))
  })

  const indexedCatalog = computed(() =>
    catalog.value.map((product) => ({
      ...product,
      _searchIndex: normalizeSearchText(
        [product.name, product.sku, product.family, product.category, describeProduct(product)]
          .filter(Boolean)
          .join(' ')
      ),
    }))
  )

  const filteredProducts = computed(() => {
    const normalizedSearch = normalizeSearchText(searchTerm.value)
    return indexedCatalog.value
      .filter((product) => {
        if (selectedCategory.value && product.category !== selectedCategory.value) return false
        if (selectedAvailability.value === 'sellable' && Number(product.sellable_stock || 0) <= 0) return false
        if (
          selectedAvailability.value === 'reserved' &&
          !(Number(product.available_stock || 0) > 0 && Number(product.sellable_stock || 0) <= 0)
        ) return false
        if (selectedAvailability.value === 'out' && Number(product.available_stock || 0) > 0) return false
        if (!normalizedSearch) return true
        return product._searchIndex.includes(normalizedSearch)
      })
      .sort((a, b) =>
        String(a.name || '').localeCompare(String(b.name || ''), 'es', { sensitivity: 'base' })
      )
  })

  function parseDescriptionMeta(rawDescription) {
    const text = String(rawDescription || '').trim()
    if (!text.startsWith('{')) return { text }
    try {
      const payload = JSON.parse(text)
      return typeof payload === 'object' && payload ? payload : {}
    } catch {
      return { text }
    }
  }

  function describeProduct(product) {
    const meta = parseDescriptionMeta(product?.description)
    if (meta.text && meta.text !== 'Importado desde Excel (N°)') return meta.text
    const parts = [meta.family || product?.family, meta.source, meta.origin_status || product?.origin_status]
      .map((part) => String(part || '').replaceAll('_', ' ').trim())
      .filter(Boolean)
    return parts.join(' · ') || 'Repuesto disponible'
  }

  function productImageSrc(product) {
    const value = String(product?.image_url || '').trim()
    if (value) {
      if (/^https?:\/\//i.test(value) || value.startsWith('/')) return value
      return `/${value.replace(/^\/+/, '')}`
    }
    return catalogImageFallback(product)
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

  function canAddProduct(product) {
    return shopCart.canAddProduct(product)
  }

  function addButtonLabel(product) {
    if (!canAddProduct(product)) {
      if (Number(product.available_stock || 0) <= 0) return 'Sin stock'
      return Number(product.sellable_stock || 0) <= 0 ? 'Reservado taller' : 'No disponible'
    }
    if (Number(product.sellable_stock || 0) > 0 && Number(product.price || 0) > 0) return 'Agregar'
    return 'Agregar a lista'
  }

  function addToCart(product) {
    if (!product || !shopCart.addProduct(product)) {
      error.value = `${product?.name || 'Producto'} no se puede agregar desde el catálogo actual.`
      setTimeout(() => { error.value = '' }, 3000)
      return
    }
    // feedback visual via cart badge update
  }

  function removeFromCart(productId) {
    shopCart.removeItem(productId)
  }

  function changeQty(productId, delta) {
    shopCart.changeQty(productId, delta)
  }

  function normalizeCatalogPayload(payload) {
    if (Array.isArray(payload)) return payload
    if (Array.isArray(payload?.data)) return payload.data
    if (Array.isArray(payload?.items)) return payload.items
    if (Array.isArray(payload?.results)) return payload.results
    return []
  }

  async function loadCatalog() {
    loading.value = true
    error.value = ''
    try {
      const res = await api.get('/inventory/', {
        params: { limit: 5000 },
      })
      const rows = normalizeCatalogPayload(res?.data)
      if (rows.length > 0) {
        catalog.value = rows
        writeCatalogCache(rows)
      } else {
        const cached = readCatalogCache()
        catalog.value = cached
      }
      shopCart.syncCatalog(catalog.value)
    } catch (err) {
      const cached = readCatalogCache()
      if (cached.length > 0) {
        catalog.value = cached
        shopCart.syncCatalog(catalog.value)
        error.value = 'No se pudo actualizar desde backend. Mostrando la última copia local del catálogo.'
      } else {
        error.value = err?.response?.data?.detail || 'No se pudo cargar el catálogo público.'
        catalog.value = []
      }
    } finally {
      loading.value = false
    }
  }

  async function submitCheckout() {
    if (!cartItems.value.length) {
      error.value = 'El carrito está vacío.'
      setTimeout(() => { error.value = '' }, 3000)
      return
    }
    if (isAdmin.value) {
      error.value = 'La solicitud de tienda está disponible para cuentas cliente.'
      setTimeout(() => { error.value = '' }, 3000)
      return
    }
    if (!isAuthenticated.value) {
      await router.push({ name: 'login', query: { redirect: '/tienda' } })
      return
    }
    try {
      const request = await shopCart.submitRequest()
      await router.push('/ot-payments')
      return request
    } catch (err) {
      error.value = err?.response?.data?.detail || err?.message || 'No se pudo enviar la solicitud.'
      setTimeout(() => { error.value = '' }, 4000)
    }
  }

  onMounted(async () => {
    shopCart.hydrate()
    const cached = readCatalogCache()
    if (cached.length > 0) {
      catalog.value = cached
      shopCart.syncCatalog(catalog.value)
    }
    await loadCatalog()
  })

  return {
    isAuthenticated,
    catalog,
    loading,
    error,
    searchTerm,
    selectedCategory,
    selectedAvailability,
    selectedShippingKey,
    shippingOptions,
    availableCategories,
    filteredProducts,
    cartItems,
    currentShipping,
    totals,
    checkoutLabel,
    shopCart,
    loadCatalog,
    formatCurrency,
    formatLinePrice,
    formatSummaryAmount,
    productImageSrc,
    describeProduct,
    canAddProduct,
    addButtonLabel,
    addToCart,
    removeFromCart,
    changeQty,
    submitCheckout,
  }
}
