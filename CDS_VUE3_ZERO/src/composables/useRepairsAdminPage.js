import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api, { extractErrorMessage } from '@/services/api'

function normalizeRepair(entry) {
  return {
    id: Number(entry?.id || 0),
    repair_code: String(entry?.repair_code || entry?.repair_number || ''),
    repair_number: String(entry?.repair_number || ''),
    client_name: String(entry?.client_name || ''),
    client_code: String(entry?.client_code || ''),
    device_model: String(entry?.device_model || ''),
    status: String(entry?.status || ''),
    status_id: Number(entry?.status_id || 0),
    problem_reported: String(entry?.problem_reported || ''),
    created_at: entry?.created_at || null,
    archived_at: entry?.archived_at || null
  }
}

function normalizeClient(entry) {
  return {
    id: Number(entry?.id || 0),
    name: String(entry?.name || ''),
    client_code: String(entry?.client_code || '')
  }
}

function baseForm() {
  return {
    client_id: '',
    model: '',
    problem_reported: '',
    priority: 2,
    paid_amount: 20000,
    payment_method: 'cash'
  }
}

const PAYMENT_METHODS = [
  { value: 'cash', label: 'Efectivo' },
  { value: 'web', label: 'Web' },
  { value: 'transfer', label: 'Transferencia' }
]

export function useRepairsAdminPage() {
  const router = useRouter()

  const repairs = ref([])
  const clients = ref([])
  const loading = ref(false)
  const error = ref('')

  const searchQuery = ref('')
  const statusFilter = ref('')
  const showForm = ref(false)
  const form = ref(baseForm())

  const statusOptions = computed(() => {
    const values = Array.from(new Set(repairs.value.map((repair) => String(repair.status || '').trim()).filter(Boolean)))
    return values.sort((a, b) => a.localeCompare(b, 'es'))
  })

  const filteredRepairs = computed(() => {
    const query = String(searchQuery.value || '').trim().toLowerCase()
    const status = String(statusFilter.value || '').trim().toLowerCase()

    return repairs.value.filter((repair) => {
      if (status && String(repair.status || '').toLowerCase() !== status) {
        return false
      }

      if (!query) return true

      const text = [
        repair.repair_code,
        repair.repair_number,
        repair.client_name,
        repair.client_code,
        repair.device_model,
        repair.problem_reported,
        repair.status
      ]
        .filter(Boolean)
        .join(' ')
        .toLowerCase()

      return text.includes(query)
    })
  })

  function resetForm() {
    form.value = baseForm()
  }

  function formatDate(value) {
    if (!value) return '—'
    const parsed = new Date(value)
    if (Number.isNaN(parsed.getTime())) return '—'
    return new Intl.DateTimeFormat('es-CL', { dateStyle: 'medium', timeStyle: 'short' }).format(parsed)
  }

  async function loadClients() {
    try {
      const response = await api.get('/clients/')
      const payload = Array.isArray(response?.data) ? response.data : []
      clients.value = payload.map(normalizeClient)
    } catch {
      clients.value = []
    }
  }

  async function loadRepairs() {
    loading.value = true
    error.value = ''

    try {
      const response = await api.get('/repairs/')
      const payload = Array.isArray(response?.data) ? response.data : []
      repairs.value = payload.map(normalizeRepair)
    } catch (requestError) {
      repairs.value = []
      error.value = extractErrorMessage(requestError)
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

  function goToRepair(repair) {
    const id = Number(repair?.id || 0)
    if (!id) return
    router.push({ name: 'admin-repair-detail', params: { id } })
  }

  async function createRepair() {
    error.value = ''

    const payload = {
      client_id: Number(form.value.client_id || 0),
      model: String(form.value.model || '').trim(),
      problem_reported: String(form.value.problem_reported || '').trim(),
      priority: Number(form.value.priority || 2),
      paid_amount: Number(form.value.paid_amount || 0),
      payment_method: String(form.value.payment_method || 'cash')
    }

    if (!payload.client_id || !payload.model || !payload.problem_reported) {
      error.value = 'Completa cliente, modelo y problema reportado.'
      return
    }

    loading.value = true

    try {
      const response = await api.post('/repairs/', payload)
      const newId = Number(response?.data?.id || 0)

      showForm.value = false
      resetForm()
      await loadRepairs()

      if (newId > 0) {
        router.push({ name: 'admin-repair-detail', params: { id: newId } })
      }
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      loading.value = false
    }
  }

  async function deleteRepair(repair) {
    const id = Number(repair?.id || 0)
    if (!id) return

    loading.value = true
    error.value = ''

    try {
      await api.delete(`/repairs/${id}`)
      await loadRepairs()
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      loading.value = false
    }
  }

  onMounted(async () => {
    await Promise.all([loadClients(), loadRepairs()])
  })

  return {
    repairs: filteredRepairs,
    clients,
    loading,
    error,
    searchQuery,
    statusFilter,
    statusOptions,
    showForm,
    form,
    paymentMethods: PAYMENT_METHODS,
    formatDate,
    loadRepairs,
    toggleForm,
    goToRepair,
    createRepair,
    deleteRepair
  }
}
