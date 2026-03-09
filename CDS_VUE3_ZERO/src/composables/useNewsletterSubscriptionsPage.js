import { computed, onMounted, ref } from 'vue'
import api, { extractErrorMessage } from '@/services/api'

function normalizeSubscription(entry) {
  return {
    id: entry?.id,
    email: String(entry?.email || ''),
    is_active: Boolean(entry?.is_active),
    source_url: String(entry?.source_url || ''),
    created_at: entry?.created_at || null,
    updated_at: entry?.updated_at || null
  }
}

export function useNewsletterSubscriptionsPage() {
  const subscriptions = ref([])
  const isLoading = ref(false)
  const error = ref('')
  const search = ref('')

  const filteredSubscriptions = computed(() => {
    const query = String(search.value || '').trim().toLowerCase()
    if (!query) return subscriptions.value

    return subscriptions.value.filter((item) => {
      return item.email.toLowerCase().includes(query) ||
        item.source_url.toLowerCase().includes(query)
    })
  })

  function formatDate(value) {
    if (!value) return '—'
    const date = new Date(value)
    if (Number.isNaN(date.getTime())) return '—'
    return new Intl.DateTimeFormat('es-CL', { dateStyle: 'medium', timeStyle: 'short' }).format(date)
  }

  async function loadSubscriptions() {
    isLoading.value = true
    error.value = ''

    try {
      const response = await api.get('/newsletter/subscriptions')
      const payload = Array.isArray(response?.data) ? response.data : []
      subscriptions.value = payload.map(normalizeSubscription)
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
      subscriptions.value = []
    } finally {
      isLoading.value = false
    }
  }

  onMounted(loadSubscriptions)

  return {
    isLoading,
    error,
    search,
    filteredSubscriptions,
    formatDate,
    loadSubscriptions
  }
}
