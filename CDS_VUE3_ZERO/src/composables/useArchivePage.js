import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api, { extractErrorMessage } from '@new/services/api'

function normalizeArchiveEntry(entry) {
  return {
    id: Number(entry?.id || 0),
    repair_code: String(entry?.repair_code || entry?.repair_number || ''),
    repair_number: String(entry?.repair_number || ''),
    client_name: String(entry?.client_name || ''),
    device_model: String(entry?.device_model || ''),
    status: String(entry?.status || ''),
    archived_at: entry?.archived_at || null
  }
}

export function useArchivePage() {
  const router = useRouter()

  const items = ref([])
  const loading = ref(false)
  const error = ref('')
  const busyId = ref(0)
  const searchQuery = ref('')

  const filteredItems = computed(() => {
    const query = String(searchQuery.value || '').trim().toLowerCase()
    if (!query) return items.value

    return items.value.filter((item) => {
      const text = [
        item.repair_code,
        item.repair_number,
        item.client_name,
        item.device_model,
        item.status
      ]
        .filter(Boolean)
        .join(' ')
        .toLowerCase()

      return text.includes(query)
    })
  })

  function formatDate(value) {
    if (!value) return '—'
    const date = new Date(value)
    if (Number.isNaN(date.getTime())) return '—'
    return new Intl.DateTimeFormat('es-CL', { dateStyle: 'medium', timeStyle: 'short' }).format(date)
  }

  async function loadArchive() {
    loading.value = true
    error.value = ''

    try {
      const response = await api.get('/repairs/archived')
      const payload = Array.isArray(response?.data) ? response.data : []
      items.value = payload.map(normalizeArchiveEntry)
    } catch (requestError) {
      items.value = []
      error.value = extractErrorMessage(requestError)
    } finally {
      loading.value = false
    }
  }

  function goToRepair(item) {
    const id = Number(item?.id || 0)
    if (!id) return
    router.push({ name: 'admin-repair-detail', params: { id } })
  }

  async function reactivate(item) {
    const id = Number(item?.id || 0)
    if (!id) return

    busyId.value = id
    error.value = ''

    try {
      await api.post(`/repairs/${id}/reactivate`)
      await loadArchive()
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      busyId.value = 0
    }
  }

  onMounted(loadArchive)

  return {
    items: filteredItems,
    loading,
    error,
    busyId,
    searchQuery,
    formatDate,
    loadArchive,
    goToRepair,
    reactivate
  }
}
