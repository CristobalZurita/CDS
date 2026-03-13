import { computed, onMounted, ref } from 'vue'
import api, { extractErrorMessage } from '@/services/api'
import { formatDate } from '@/utils/format'

function normalizeMessage(entry) {
  return {
    id: entry?.id,
    name: String(entry?.name || ''),
    email: String(entry?.email || ''),
    subject: String(entry?.subject || ''),
    message: String(entry?.message || ''),
    status: String(entry?.status || 'new'),
    created_at: entry?.created_at || null
  }
}

export function useContactMessagesPage() {
  const messages = ref([])
  const isLoading = ref(false)
  const error = ref('')
  const search = ref('')

  const filteredMessages = computed(() => {
    const query = String(search.value || '').trim().toLowerCase()
    if (!query) return messages.value

    return messages.value.filter((entry) => {
      return entry.name.toLowerCase().includes(query) ||
        entry.email.toLowerCase().includes(query) ||
        entry.subject.toLowerCase().includes(query) ||
        entry.message.toLowerCase().includes(query)
    })
  })

  async function loadMessages() {
    isLoading.value = true
    error.value = ''

    try {
      const response = await api.get('/contact/messages')
      const payload = Array.isArray(response?.data) ? response.data : []
      messages.value = payload.map(normalizeMessage)
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
      messages.value = []
    } finally {
      isLoading.value = false
    }
  }

  onMounted(loadMessages)

  return {
    isLoading,
    error,
    search,
    filteredMessages,
    formatDate,
    loadMessages
  }
}
