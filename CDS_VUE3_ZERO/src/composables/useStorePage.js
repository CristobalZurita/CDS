import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import {
  resolveStoreAddButtonLabel,
  resolveStoreCheckoutGuard,
  resolveStoreCheckoutLabel
} from '@/composables/storePageState'
import { useShopCartStore } from '@/stores/shopCart'
import { formatCurrency } from '@/utils/format'
import {
  describeStoreProduct,
  fetchStoreCatalog,
  filterStoreCatalog,
  formatStoreLinePrice,
  formatStoreSummaryAmount,
  listStoreCategories,
  loadStoreCatalogSnapshot,
  loadStoreFeaturedSnapshot,
  readStoreCatalogCache,
  resolveStoreProductImage,
  searchStoreCatalog,
  sortStoreCatalog,
} from '@/services/storeCatalogService'

export function useStorePage() {
  const { isAuthenticated, isAdmin } = useAuth()
  const router = useRouter()
  const shopCart = useShopCartStore()

  const catalog = ref([])
  const catalogIndex = ref([]) // lista completa SKU+nombre para el datalist de búsqueda
  const loading = ref(false)
  const error = ref('')
  const searchTerm = ref('')
  const selectedCategory = ref('')
  const selectedAvailability = ref('all')
  const selectedSort = ref('featured')
  const catalogMode = ref('featured') // 'featured' | 'search' | 'full'
  const isFullCatalogLoaded = ref(false)
  const featuredRows = ref([])
  let searchDebounceTimer = null

  const selectedShippingKey = computed({
    get: () => shopCart.selectedShippingKey,
    set: (value) => shopCart.setShippingKey(value),
  })

  const shippingOptions = shopCart.shippingOptions
  const cartOpen = computed(() => shopCart.cartOpen)
  const cartSubmitting = computed(() => shopCart.submitting)
  const cartItems = computed(() => shopCart.items)
  const cartItemsCount = computed(() => shopCart.itemsCount)
  const currentShipping = computed(() => shopCart.currentShipping)
  const totals = computed(() => shopCart.totals)

  const checkoutLabel = computed(() => {
    return resolveStoreCheckoutLabel({
      isAdmin: isAdmin.value,
      isAuthenticated: isAuthenticated.value,
      submitting: shopCart.submitting
    })
  })

  // Usa el índice completo si ya está disponible; si no, lo que hay en catalog.
  // Así las categorías aparecen aunque el modo featured tenga 0 resultados.
  const availableCategories = computed(() =>
    listStoreCategories(catalogIndex.value.length > 0 ? catalogIndex.value : catalog.value)
  )

  const activeSortKey = computed(() => {
    if (selectedSort.value !== 'featured') return selectedSort.value
    return catalogMode.value === 'featured' ? 'featured' : 'name'
  })

  const filteredProducts = computed(() => {
    const filtered = filterStoreCatalog(catalog.value, {
      searchTerm: searchTerm.value,
      selectedCategory: selectedCategory.value,
      selectedAvailability: selectedAvailability.value,
    })
    return sortStoreCatalog(filtered, { sortKey: activeSortKey.value })
  })

  function productImageSrc(product) {
    return resolveStoreProductImage(product)
  }

  function describeProduct(product) {
    return describeStoreProduct(product)
  }

  function formatLinePrice(value) {
    return formatStoreLinePrice(value)
  }

  function formatSummaryAmount(value) {
    return formatStoreSummaryAmount(value, totals.value)
  }

  function canAddProduct(product) {
    return shopCart.canAddProduct(product)
  }

  function addButtonLabel(product) {
    return resolveStoreAddButtonLabel(product, canAddProduct(product))
  }

  function clearCart() {
    if (!shopCart.items.length) return
    if (!window.confirm('¿Vaciar el carrito? Se eliminarán todos los productos.')) return
    shopCart.clear()
  }

  function openCartDrawer() {
    shopCart.openCart()
  }

  function productQtyInCart(productId) {
    const match = shopCart.items.find((item) => String(item.id) === String(productId))
    return Number(match?.qty || 0)
  }

  function clearTransientError(delay = 3000) {
    window.setTimeout(() => {
      error.value = ''
    }, delay)
  }

  // syncCart=true solo cuando se carga el catálogo completo (evita BUG-003: cart limpiado por catálogo parcial)
  function syncCatalog(rows, syncCart = true) {
    catalog.value = Array.isArray(rows) ? rows : []
    if (syncCart && catalog.value.length > 0) {
      shopCart.syncCatalog(catalog.value)
    }
  }

  function addToCart(product) {
    if (!product || !shopCart.addProduct(product)) {
      error.value = `${product?.name || 'Producto'} no se puede agregar desde el catálogo actual.`
      clearTransientError()
    }
  }

  function removeFromCart(productId) {
    shopCart.removeItem(productId)
  }

  function changeQty(productId, delta) {
    shopCart.changeQty(productId, delta)
  }

  function closeCartDrawer() {
    shopCart.closeCart()
  }

  function onDrawerChangeQty({ id, delta }) {
    changeQty(id, delta)
  }

  async function loadFeatured() {
    loading.value = true
    error.value = ''
    try {
      const snapshot = await loadStoreFeaturedSnapshot({ isAuthenticated: isAuthenticated.value })
      featuredRows.value = snapshot.rows
      syncCatalog(snapshot.rows, false)
      catalogMode.value = 'featured'
      error.value = snapshot.error || ''
    } finally {
      loading.value = false
    }
  }

  async function loadFullCatalog() {
    loading.value = true
    error.value = ''
    try {
      const snapshot = await loadStoreCatalogSnapshot({ isAuthenticated: isAuthenticated.value })
      syncCatalog(snapshot.rows, true)
      error.value = snapshot.error || ''
      if (snapshot.rows.length > 0) {
        isFullCatalogLoaded.value = true
        catalogMode.value = 'full'
      }
    } finally {
      loading.value = false
    }
  }

  // Respeta el modo actual: en full recarga todo, en featured/search recarga featured
  async function loadCatalog() {
    if (catalogMode.value === 'full') {
      await loadFullCatalog()
    } else {
      await loadFeatured()
    }
  }

  async function submitCheckout() {
    const checkoutGuard = resolveStoreCheckoutGuard({
      cartItemsCount: cartItems.value.length,
      isAdmin: isAdmin.value,
      isAuthenticated: isAuthenticated.value
    })

    if (checkoutGuard.kind === 'error') {
      error.value = checkoutGuard.message
      clearTransientError()
      return
    }

    if (checkoutGuard.kind === 'login') {
      await router.push({ name: 'login', query: { redirect: '/tienda' } })
      return
    }
    try {
      const request = await shopCart.submitRequest()
      await router.push('/ot-payments')
      return request
    } catch (err) {
      error.value = err?.response?.data?.detail || err?.message || 'No se pudo enviar la solicitud.'
      clearTransientError(4000)
    }
  }

  watch(searchTerm, (val) => {
    clearTimeout(searchDebounceTimer)
    // En modo full el filtrado local es suficiente — no necesita llamar al API
    if (catalogMode.value === 'full') return

    if (!val || val.length < 2) {
      if (catalogMode.value === 'search' && featuredRows.value.length > 0) {
        catalogMode.value = 'featured'
        syncCatalog(featuredRows.value, false)
      }
      return
    }

    searchDebounceTimer = setTimeout(async () => {
      catalogMode.value = 'search'
      loading.value = true
      error.value = ''
      try {
        const rows = await searchStoreCatalog(val, {
          isAuthenticated: isAuthenticated.value,
          categoryId: selectedCategory.value || null
        })
        syncCatalog(rows, false)
      } catch (err) {
        error.value = err?.response?.data?.detail || err?.message || 'Error en la búsqueda.'
      } finally {
        loading.value = false
      }
    }, 400)
  })

  watch(selectedCategory, async (value) => {
    if (!value || isFullCatalogLoaded.value || loading.value) return
    await loadFullCatalog()
  })

  async function loadCatalogIndex() {
    // Carga en background — solo para el datalist de autocompletado, no afecta la vista
    try {
      const rows = await fetchStoreCatalog({ isAuthenticated: isAuthenticated.value })
      catalogIndex.value = rows
    } catch {
      // silencio — el datalist es mejora progresiva, no crítica
    }
  }

  onMounted(async () => {
    shopCart.hydrate()
    const cached = readStoreCatalogCache()
    if (cached.length > 0) {
      // Usar cache solo para validar el carrito — no mostrar todo en pantalla
      shopCart.syncCatalog(cached)
      catalogIndex.value = cached // precarga el datalist desde cache mientras llega el fetch
    }
    // Siempre arrancar en modo featured (rápido)
    await loadFeatured()
    // Catálogo completo en background para autocompletado del buscador
    loadCatalogIndex()
  })

  return {
    isAuthenticated,
    catalog,
    catalogIndex,
    loading,
    error,
    searchTerm,
    selectedCategory,
    selectedAvailability,
    selectedSort,
    selectedShippingKey,
    shippingOptions,
    cartOpen,
    cartSubmitting,
    availableCategories,
    filteredProducts,
    cartItems,
    cartItemsCount,
    currentShipping,
    totals,
    checkoutLabel,
    catalogMode,
    isFullCatalogLoaded,
    loadCatalog,
    loadFullCatalog,
    formatCurrency,
    formatLinePrice,
    formatSummaryAmount,
    productImageSrc,
    describeProduct,
    canAddProduct,
    addButtonLabel,
    addToCart,
    openCartDrawer,
    productQtyInCart,
    removeFromCart,
    changeQty,
    clearCart,
    closeCartDrawer,
    onDrawerChangeQty,
    submitCheckout,
  }
}
