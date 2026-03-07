import { computed, onMounted, ref } from 'vue'
import api, { extractErrorMessage } from '@new/services/api'

function normalizeTicket(entry) {
  return {
    id: Number(entry?.id || 0),
    client_id: entry?.client_id || null,
    repair_id: entry?.repair_id || null,
    subject: String(entry?.subject || ''),
    status: String(entry?.status || 'open'),
    priority: String(entry?.priority || 'normal'),
    messages: Array.isArray(entry?.messages) ? entry.messages : [],
    created_at: entry?.created_at || null,
    updated_at: entry?.updated_at || null
  }
}

function normalizeClient(entry) {
  return {
    id: Number(entry?.id || 0),
    name: String(entry?.name || ''),
    client_code: String(entry?.client_code || '')
  }
}

function normalizeRepair(entry) {
  return {
    id: Number(entry?.id || 0),
    repair_code: String(entry?.repair_code || entry?.repair_number || ''),
    client_name: String(entry?.client_name || ''),
    problem_reported: String(entry?.problem_reported || '')
  }
}

function baseForm() {
  return {
    client_id: '',
    repair_id: '',
    subject: '',
    message: '',
    priority: 'normal'
  }
}

export function useTicketsPage() {
  const tickets = ref([])
  const clients = ref([])
  const repairs = ref([])

  const loading = ref(false)
  const error = ref('')

  const showForm = ref(false)
  const form = ref(baseForm())
  const searchQuery = ref('')

  const statusOptions = [
    { value: 'open', label: 'open' },
    { value: 'in_progress', label: 'in_progress' },
    { value: 'closed', label: 'closed' }
  ]

  const priorityOptions = [
    { value: 'low', label: 'Baja' },
    { value: 'normal', label: 'Normal' },
    { value: 'high', label: 'Alta' },
    { value: 'urgent', label: 'Urgente' }
  ]

  const filteredTickets = computed(() => {
    const query = String(searchQuery.value || '').trim().toLowerCase()
    if (!query) return tickets.value

    return tickets.value.filter((ticket) => {
      const text = [
        ticket.id,
        ticket.subject,
        ticket.status,
        ticket.priority,
        ticket.client_id,
        ticket.repair_id
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

  function toggleForm() {
    showForm.value = !showForm.value
    if (!showForm.value) resetForm()
  }

  function formatDate(value) {
    if (!value) return '—'
    const date = new Date(value)
    if (Number.isNaN(date.getTime())) return '—'
    return new Intl.DateTimeFormat('es-CL', { dateStyle: 'medium', timeStyle: 'short' }).format(date)
  }

  async function loadSupportData() {
    try {
      const [clientsResponse, repairsResponse] = await Promise.all([
        api.get('/clients/').catch(() => ({ data: [] })),
        api.get('/repairs/').catch(() => ({ data: [] }))
      ])

      const clientsPayload = Array.isArray(clientsResponse?.data) ? clientsResponse.data : []
      const repairsPayload = Array.isArray(repairsResponse?.data) ? repairsResponse.data : []

      clients.value = clientsPayload.map(normalizeClient)
      repairs.value = repairsPayload.map(normalizeRepair)
    } catch {
      clients.value = []
      repairs.value = []
    }
  }

  async function loadTickets() {
    loading.value = true
    error.value = ''

    try {
      const response = await api.get('/tickets/')
      const payload = Array.isArray(response?.data) ? response.data : []
      tickets.value = payload.map(normalizeTicket)
    } catch (requestError) {
      tickets.value = []
      error.value = extractErrorMessage(requestError)
    } finally {
      loading.value = false
    }
  }

  async function createTicket() {
    error.value = ''

    const payload = {
      client_id: form.value.client_id ? Number(form.value.client_id) : null,
      repair_id: form.value.repair_id ? Number(form.value.repair_id) : null,
      subject: String(form.value.subject || '').trim(),
      message: String(form.value.message || '').trim(),
      priority: String(form.value.priority || 'normal')
    }

    if (payload.subject.length < 3 || !payload.message) {
      error.value = 'Completa asunto (min 3) y mensaje.'
      return
    }

    loading.value = true

    try {
      await api.post('/tickets/', payload)
      showForm.value = false
      resetForm()
      await loadTickets()
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      loading.value = false
    }
  }

  async function updateTicketStatus(ticket, status) {
    const id = Number(ticket?.id || 0)
    if (!id) return

    loading.value = true
    error.value = ''

    try {
      await api.patch(`/tickets/${id}`, null, {
        params: { status }
      })
      await loadTickets()
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      loading.value = false
    }
  }

  async function deleteTicket(ticket) {
    const id = Number(ticket?.id || 0)
    if (!id) return

    loading.value = true
    error.value = ''

    try {
      await api.delete(`/tickets/${id}`)
      await loadTickets()
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      loading.value = false
    }
  }

  async function addMessage(ticket, messageText) {
    const id = Number(ticket?.id || 0)
    const message = String(messageText || '').trim()
    if (!id || !message) return

    loading.value = true
    error.value = ''

    try {
      await api.post(`/tickets/${id}/messages`, {
        message
      })
      await loadTickets()
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      loading.value = false
    }
  }

  onMounted(async () => {
    await Promise.all([loadSupportData(), loadTickets()])
  })

  return {
    tickets: filteredTickets,
    clients,
    repairs,
    loading,
    error,
    showForm,
    form,
    searchQuery,
    statusOptions,
    priorityOptions,
    formatDate,
    toggleForm,
    loadTickets,
    createTicket,
    updateTicketStatus,
    deleteTicket,
    addMessage
  }
}
