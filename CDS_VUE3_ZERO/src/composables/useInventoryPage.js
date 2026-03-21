import { computed, onMounted, ref } from 'vue'
import api, { extractErrorMessage } from '@/services/api'
import { formatCurrency, formatDate } from '@/utils/format'

function normalizeItem(entry) {
  return {
    id: entry?.id,
    stock_id: entry?.stock_id || null,
    sku: String(entry?.sku || ''),
    name: String(entry?.name || ''),
    description: String(entry?.description || ''),
    category_id: entry?.category_id || null,
    category: String(entry?.category || ''),
    family: String(entry?.family || ''),
    origin_status: String(entry?.origin_status || ''),
    price: Number(entry?.price || 0),
    stock: Number(entry?.stock || 0),
    available_stock: Number(entry?.available_stock || 0),
    sellable_stock: Number(entry?.sellable_stock || 0),
    min_stock: Number(entry?.min_stock || 0),
    quantity_reserved: Number(entry?.quantity_reserved || 0),
    quantity_in_transit: Number(entry?.quantity_in_transit || 0),
    quantity_damaged: Number(entry?.quantity_damaged || 0),
    quantity_in_work: Number(entry?.quantity_in_work || 0),
    quantity_under_review: Number(entry?.quantity_under_review || 0),
    quantity_internal_use: Number(entry?.quantity_internal_use || 0),
    location: String(entry?.location || ''),
    supplier: String(entry?.supplier || ''),
    unit_cost: Number(entry?.unit_cost || 0),
    enabled: entry?.enabled !== false,
    store_visible: Boolean(entry?.store_visible),
    is_low_stock: Boolean(entry?.is_low_stock)
  }
}

function normalizeMovement(entry) {
  return {
    id: Number(entry?.id || 0),
    stock_id: Number(entry?.stock_id || 0),
    movement_type: String(entry?.movement_type || ''),
    quantity: Number(entry?.quantity || 0),
    repair_id: Number(entry?.repair_id || 0),
    notes: String(entry?.notes || ''),
    performed_by: entry?.performed_by || null,
    created_at: entry?.created_at || null
  }
}

export function useInventoryPage() {
  const items = ref([])
  const categories = ref([])
  const loading = ref(false)
  const error = ref('')
  const detailLoading = ref(false)
  const detailError = ref('')
  const selectedItem = ref(null)
  const stockMovements = ref([])

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

  async function startEdit(item) {
    if (selectedItem.value?.id !== Number(item?.id || 0)) {
      await openItemDetail(item)
    }

    const current = selectedItem.value?.id === Number(item?.id || 0)
      ? selectedItem.value
      : normalizeItem(item)

    editingId.value = Number(current.id)
    form.value = {
      name: String(current.name || ''),
      sku: String(current.sku || ''),
      category_id: current.category_id || '',
      price: Number(current.price || 0),
      stock: Number(current.stock || 0),
      min_quantity: Number(current.min_stock || 5),
      family: String(current.family || 'REPUESTO'),
      origin_status: String(current.origin_status || 'USADO'),
      store_visible: Boolean(current.store_visible),
      enabled: current.enabled !== false
    }
    showForm.value = true
  }

  function toggleForm() {
    showForm.value = !showForm.value
    if (!showForm.value) resetForm()
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

  async function loadItemDetail(productId) {
    const response = await api.get(`/inventory/${productId}`)
    return normalizeItem(response?.data)
  }

  async function loadStockMovements(productId) {
    const response = await api.get('/stock-movements/', {
      params: {
        product_id: Number(productId || 0),
        limit: 50
      }
    })
    const payload = Array.isArray(response?.data) ? response.data : []
    return payload.map(normalizeMovement)
  }

  async function openItemDetail(item) {
    const productId = Number(item?.id || 0)
    if (!productId) return

    detailLoading.value = true
    detailError.value = ''

    try {
      const [detail, movements] = await Promise.all([
        loadItemDetail(productId),
        loadStockMovements(productId)
      ])
      selectedItem.value = detail
      stockMovements.value = movements
    } catch (requestError) {
      detailError.value = extractErrorMessage(requestError)
      selectedItem.value = null
      stockMovements.value = []
    } finally {
      detailLoading.value = false
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
      if (selectedItem.value?.id) {
        await openItemDetail({ id: selectedItem.value.id })
      }
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
      if (selectedItem.value?.id === Number(item.id)) {
        selectedItem.value = null
        stockMovements.value = []
      }
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
    detailLoading,
    detailError,
    selectedItem,
    stockMovements,
    filters,
    showForm,
    hasEditing,
    form,
    totalStock,
    lowStockCount,
    formatDate,
    formatCurrency,
    loadInventory,
    openItemDetail,
    toggleForm,
    startCreate,
    startEdit,
    saveItem,
    removeItem
  }
}
