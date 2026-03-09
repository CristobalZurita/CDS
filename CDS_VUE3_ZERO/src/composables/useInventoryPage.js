import { computed, onMounted, ref } from 'vue'
import api, { extractErrorMessage } from '@/services/api'

function normalizeItem(entry) {
  return {
    id: entry?.id,
    sku: String(entry?.sku || ''),
    name: String(entry?.name || ''),
    category_id: entry?.category_id || null,
    category: String(entry?.category || ''),
    family: String(entry?.family || ''),
    origin_status: String(entry?.origin_status || ''),
    price: Number(entry?.price || 0),
    stock: Number(entry?.stock || 0),
    available_stock: Number(entry?.available_stock || 0),
    sellable_stock: Number(entry?.sellable_stock || 0),
    min_stock: Number(entry?.min_stock || 0),
    enabled: entry?.enabled !== false,
    store_visible: Boolean(entry?.store_visible),
    is_low_stock: Boolean(entry?.is_low_stock)
  }
}

export function useInventoryPage() {
  const items = ref([])
  const categories = ref([])
  const loading = ref(false)
  const error = ref('')

  const filters = ref({
    search: '',
    category_id: '',
    low_stock_only: false
  })

  const showForm = ref(false)
  const editingId = ref(null)
  const form = ref({
    name: '',
    sku: '',
    category_id: '',
    price: 0,
    stock: 0,
    min_quantity: 5,
    family: 'REPUESTO',
    origin_status: 'USADO',
    store_visible: false,
    enabled: true
  })

  const hasEditing = computed(() => editingId.value !== null)

  const sortedItems = computed(() => {
    return [...items.value].sort((a, b) => a.name.localeCompare(b.name, 'es'))
  })

  const totalStock = computed(() => sortedItems.value.reduce((sum, item) => sum + Number(item.stock || 0), 0))
  const lowStockCount = computed(() => sortedItems.value.filter((item) => item.is_low_stock).length)

  function resetForm() {
    form.value = {
      name: '',
      sku: '',
      category_id: '',
      price: 0,
      stock: 0,
      min_quantity: 5,
      family: 'REPUESTO',
      origin_status: 'USADO',
      store_visible: false,
      enabled: true
    }
    editingId.value = null
  }

  function startCreate() {
    resetForm()
    showForm.value = true
  }

  function startEdit(item) {
    editingId.value = Number(item.id)
    form.value = {
      name: String(item.name || ''),
      sku: String(item.sku || ''),
      category_id: item.category_id || '',
      price: Number(item.price || 0),
      stock: Number(item.stock || 0),
      min_quantity: Number(item.min_stock || 5),
      family: String(item.family || 'REPUESTO'),
      origin_status: String(item.origin_status || 'USADO'),
      store_visible: Boolean(item.store_visible),
      enabled: item.enabled !== false
    }
    showForm.value = true
  }

  function toggleForm() {
    showForm.value = !showForm.value
    if (!showForm.value) resetForm()
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

  async function loadCategories() {
    try {
      const response = await api.get('/categories/')
      const payload = Array.isArray(response?.data) ? response.data : []
      categories.value = payload.map((entry) => ({
        id: entry?.id,
        name: String(entry?.name || '')
      }))
    } catch {
      categories.value = []
    }
  }

  async function loadInventory() {
    loading.value = true
    error.value = ''

    try {
      const params = {
        search: String(filters.value.search || '').trim() || undefined,
        category_id: filters.value.category_id ? Number(filters.value.category_id) : undefined,
        low_stock_only: filters.value.low_stock_only || undefined
      }
      const response = await api.get('/inventory/', { params })
      const payload = Array.isArray(response?.data) ? response.data : []
      items.value = payload.map(normalizeItem)
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
      items.value = []
    } finally {
      loading.value = false
    }
  }

  async function saveItem() {
    loading.value = true
    error.value = ''

    try {
      const payload = {
        name: String(form.value.name || '').trim(),
        sku: String(form.value.sku || '').trim(),
        category_id: Number(form.value.category_id || 0),
        price: Number(form.value.price || 0),
        stock: Number(form.value.stock || 0),
        min_quantity: Number(form.value.min_quantity || 0),
        family: String(form.value.family || 'REPUESTO').toUpperCase(),
        origin_status: String(form.value.origin_status || 'USADO').toUpperCase(),
        store_visible: Boolean(form.value.store_visible),
        enabled: Boolean(form.value.enabled)
      }

      if (!payload.name || !payload.sku || !payload.category_id) {
        throw new Error('Completa nombre, SKU y categoría.')
      }

      if (hasEditing.value) {
        await api.put(`/inventory/${editingId.value}`, payload)
      } else {
        await api.post('/inventory/', payload)
      }

      showForm.value = false
      resetForm()
      await loadInventory()
    } catch (requestError) {
      error.value = requestError?.message || extractErrorMessage(requestError)
    } finally {
      loading.value = false
    }
  }

  async function removeItem(item) {
    loading.value = true
    error.value = ''

    try {
      await api.delete(`/inventory/${item.id}`)
      await loadInventory()
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      loading.value = false
    }
  }

  onMounted(async () => {
    await loadCategories()
    await loadInventory()
  })

  return {
    items: sortedItems,
    categories,
    loading,
    error,
    filters,
    showForm,
    hasEditing,
    form,
    totalStock,
    lowStockCount,
    formatCurrency,
    loadInventory,
    toggleForm,
    startCreate,
    startEdit,
    saveItem,
    removeItem
  }
}
