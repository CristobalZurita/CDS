import { computed, onMounted, ref } from 'vue'
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
  filterStoreCatalog,
  formatStoreLinePrice,
  formatStoreSummaryAmount,
  listStoreCategories,
  loadStoreCatalogSnapshot,
  readStoreCatalogCache,
  resolveStoreProductImage,
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
  const cartOpen = computed(() => shopCart.cartOpen)
  const cartSubmitting = computed(() => shopCart.submitting)
  const cartItems = computed(() => shopCart.items)
  const currentShipping = computed(() => shopCart.currentShipping)
  const totals = computed(() => shopCart.totals)

  const checkoutLabel = computed(() => {
    return resolveStoreCheckoutLabel({
      isAdmin: isAdmin.value,
      isAuthenticated: isAuthenticated.value,
      submitting: shopCart.submitting
    })
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
    return resolveStoreAddButtonLabel(product, canAddProduct(product))
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
      const snapshot = await loadStoreCatalogSnapshot({
        isAuthenticated: isAuthenticated.value
      })

      syncCatalog(snapshot.rows)
      error.value = snapshot.error
    } finally {
      loading.value = false
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
    cartOpen,
    cartSubmitting,
    availableCategories,
    filteredProducts,
    cartItems,
    currentShipping,
    totals,
    checkoutLabel,
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
