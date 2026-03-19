import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { useShopCartStore } from '@/stores/shopCart'
import { formatCurrency } from '@/utils/format'
import {
  clearStoreCatalogCache,
  describeStoreProduct,
  fetchStoreCatalog,
  filterStoreCatalog,
  formatStoreLinePrice,
  formatStoreSummaryAmount,
  listStoreCategories,
  readStoreCatalogCache,
  resolveStoreProductImage,
  writeStoreCatalogCache
} from '@/services/storeCatalogService'

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

  const availableCategories = computed(() => listStoreCategories(catalog.value))

  const filteredProducts = computed(() => filterStoreCatalog(catalog.value, {
    searchTerm: searchTerm.value,
    selectedCategory: selectedCategory.value,
    selectedAvailability: selectedAvailability.value,
  }))

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
    if (!canAddProduct(product)) {
      if (Number(product.available_stock || 0) <= 0) return 'Sin stock'
      return Number(product.sellable_stock || 0) <= 0 ? 'Reservado taller' : 'No disponible'
    }
    if (Number(product.sellable_stock || 0) > 0 && Number(product.price || 0) > 0) return 'Agregar'
    return 'Agregar a lista'
  }

  function clearTransientError(delay = 3000) {
    window.setTimeout(() => {
      error.value = ''
    }, delay)
  }

  function syncCatalog(rows) {
    catalog.value = Array.isArray(rows) ? rows : []
    shopCart.syncCatalog(catalog.value)
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

  async function loadCatalog() {
    loading.value = true
    error.value = ''

    try {
      const rows = await fetchStoreCatalog({ isAuthenticated: isAuthenticated.value })
      if (rows.length > 0) {
        syncCatalog(rows)
        writeStoreCatalogCache(rows)
      } else {
        clearStoreCatalogCache()
        syncCatalog([])
      }
    } catch (err) {
      const cached = readStoreCatalogCache()
      if (cached.length > 0) {
        syncCatalog(cached)
        error.value = 'No se pudo actualizar desde backend. Mostrando la última copia local del catálogo.'
      } else {
        error.value = err?.response?.data?.detail || 'No se pudo cargar el catálogo.'
        syncCatalog([])
      }
    } finally {
      loading.value = false
    }
  }

  async function submitCheckout() {
    if (!cartItems.value.length) {
      error.value = 'El carrito está vacío.'
      clearTransientError()
      return
    }
    if (isAdmin.value) {
      error.value = 'La solicitud de tienda está disponible para cuentas cliente.'
      clearTransientError()
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
      clearTransientError(4000)
    }
  }

  onMounted(async () => {
    shopCart.hydrate()
    const cached = readStoreCatalogCache()
    if (cached.length > 0) {
      syncCatalog(cached)
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
    closeCartDrawer,
    onDrawerChangeQty,
    submitCheckout,
  }
}
