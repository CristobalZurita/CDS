import { computed, onMounted, ref } from 'vue'
import api, { extractErrorMessage } from '@new/services/api'

function normalizeCategory(entry) {
  return {
    id: entry?.id,
    name: String(entry?.name || ''),
    description: String(entry?.description || ''),
    created_at: entry?.created_at || null,
    updated_at: entry?.updated_at || null
  }
}

export function useCategoriesPage() {
  const categories = ref([])
  const loading = ref(false)
  const error = ref('')

  const showForm = ref(false)
  const editingCategoryId = ref(null)
  const form = ref({
    name: '',
    description: ''
  })

  const hasEditingCategory = computed(() => editingCategoryId.value !== null)

  const sortedCategories = computed(() => {
    return [...categories.value].sort((a, b) => a.name.localeCompare(b.name, 'es'))
  })

  function resetForm() {
    form.value = { name: '', description: '' }
    editingCategoryId.value = null
  }

  function formatDate(value) {
    if (!value) return '—'
    const date = new Date(value)
    if (Number.isNaN(date.getTime())) return '—'
    return new Intl.DateTimeFormat('es-CL', { dateStyle: 'medium', timeStyle: 'short' }).format(date)
  }

  async function loadCategories() {
    loading.value = true
    error.value = ''

    try {
      const response = await api.get('/categories/')
      const payload = Array.isArray(response?.data) ? response.data : []
      categories.value = payload.map(normalizeCategory)
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
      categories.value = []
    } finally {
      loading.value = false
    }
  }

  function toggleForm() {
    showForm.value = !showForm.value
    if (!showForm.value) {
      resetForm()
    }
  }

  function startCreate() {
    resetForm()
    showForm.value = true
  }

  function startEdit(category) {
    editingCategoryId.value = Number(category.id)
    form.value = {
      name: String(category.name || ''),
      description: String(category.description || '')
    }
    showForm.value = true
  }

  async function saveCategory() {
    error.value = ''

    const payload = {
      name: String(form.value.name || '').trim(),
      description: String(form.value.description || '').trim() || null
    }

    if (payload.name.length < 2) {
      error.value = 'El nombre de la categoría requiere al menos 2 caracteres.'
      return
    }

    loading.value = true

    try {
      if (hasEditingCategory.value) {
        await api.put(`/categories/${editingCategoryId.value}`, payload)
      } else {
        await api.post('/categories/', payload)
      }

      showForm.value = false
      resetForm()
      await loadCategories()
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      loading.value = false
    }
  }

  async function removeCategory(category) {
    const id = Number(category?.id || 0)
    if (!id) return

    loading.value = true
    error.value = ''

    try {
      await api.delete(`/categories/${id}`)
      await loadCategories()
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      loading.value = false
    }
  }

  onMounted(loadCategories)

  return {
    categories: sortedCategories,
    loading,
    error,
    showForm,
    hasEditingCategory,
    form,
    formatDate,
    loadCategories,
    toggleForm,
    startCreate,
    startEdit,
    saveCategory,
    removeCategory
  }
}
