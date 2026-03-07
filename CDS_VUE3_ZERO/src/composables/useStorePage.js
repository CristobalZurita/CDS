import { computed, onMounted, ref } from 'vue'
import api, { extractErrorMessage } from '@new/services/api'
import { useAuth } from '@new/composables/useAuth'

function normalizeSearchText(value) {
  return String(value || '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[_-]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
}

export function useStorePage() {
  const { isAuthenticated } = useAuth()

  const catalog = ref([])
  const loading = ref(false)
  const error = ref('')
  const searchTerm = ref('')
  const selectedCategory = ref('')

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

    return catalog.value.filter((product) => {
      if (selectedCategory.value && String(product.category || '') !== selectedCategory.value) {
        return false
      }

      if (!normalizedSearch) return true

      const index = normalizeSearchText([
        product.name,
        product.sku,
        product.category,
        product.family,
        product.description
      ].filter(Boolean).join(' '))

      return index.includes(normalizedSearch)
    })
  })

  function normalizeCatalogPayload(payload) {
    if (Array.isArray(payload)) return payload
    if (Array.isArray(payload?.data)) return payload.data
    if (Array.isArray(payload?.items)) return payload.items
    return []
  }

  async function loadCatalog() {
    loading.value = true
    error.value = ''

    try {
      const response = await api.get('/inventory/public/')
      catalog.value = normalizeCatalogPayload(response.data)
    } catch (err) {
      catalog.value = []
      error.value = extractErrorMessage(err)
    } finally {
      loading.value = false
    }
  }

  function formatCurrency(value) {
    const amount = Number(value || 0)
    return new Intl.NumberFormat('es-CL', {
      style: 'currency',
      currency: 'CLP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount)
  }

  function productImageSrc(product) {
    const value = String(product?.image_url || '').trim()
    if (!value) return ''
    return value
  }

  function describeProduct(product) {
    if (String(product?.description || '').trim()) return String(product.description).trim()
    const parts = [product?.family, product?.category].filter(Boolean)
    return parts.join(' · ') || 'Repuesto disponible'
  }

  onMounted(loadCatalog)

  return {
    isAuthenticated,
    catalog,
    loading,
    error,
    searchTerm,
    selectedCategory,
    availableCategories,
    filteredProducts,
    loadCatalog,
    formatCurrency,
    productImageSrc,
    describeProduct
  }
}
