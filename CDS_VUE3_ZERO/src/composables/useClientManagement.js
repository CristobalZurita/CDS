import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import api, { extractErrorMessage } from '@/services/api'

function normalizeClient(entry) {
  return {
    id: Number(entry?.id || 0),
    client_code: String(entry?.client_code || ''),
    name: String(entry?.name || ''),
    email: String(entry?.email || ''),
    phone: String(entry?.phone || ''),
    phone_alt: String(entry?.phone_alt || ''),
    address: String(entry?.address || ''),
    city: String(entry?.city || ''),
    region: String(entry?.region || ''),
    country: String(entry?.country || ''),
    notes: String(entry?.notes || ''),
    internal_notes: String(entry?.internal_notes || ''),
    total_repairs: Number(entry?.total_repairs || 0),
    total_spent: Number(entry?.total_spent || 0)
  }
}

function baseClientForm() {
  return {
    name: '',
    email: '',
    phone: '',
    phone_alt: '',
    address: '',
    city: '',
    region: '',
    country: 'Chile',
    notes: '',
    internal_notes: ''
  }
}

export function useClientManagement({ selectedClientId, loading, error, onClientDeleted }) {
  const route = useRoute()

  const clients = ref([])
  const searchQuery = ref('')
  const showCreateForm = ref(false)
  const showEditForm = ref(false)
  const createForm = ref(baseClientForm())
  const editForm = ref(baseClientForm())

  const selectedClient = computed(() =>
    clients.value.find(client => client.id === selectedClientId.value) || null
  )

  const filteredClients = computed(() => {
    const query = String(searchQuery.value || '').trim().toLowerCase()
    if (!query) return clients.value
    return clients.value.filter(client => {
      const text = [client.client_code, client.name, client.email, client.phone, client.address]
        .filter(Boolean).join(' ').toLowerCase()
      return text.includes(query)
    })
  })

  function hasValidSelectedClient() {
    return Number(selectedClientId.value) > 0
  }

  function resetCreateForm() {
    createForm.value = baseClientForm()
  }

  function resetEditForm() {
    if (!selectedClient.value) {
      editForm.value = baseClientForm()
      return
    }
    editForm.value = {
      name: String(selectedClient.value.name || ''),
      email: String(selectedClient.value.email || ''),
      phone: String(selectedClient.value.phone || ''),
      phone_alt: String(selectedClient.value.phone_alt || ''),
      address: String(selectedClient.value.address || ''),
      city: String(selectedClient.value.city || ''),
      region: String(selectedClient.value.region || ''),
      country: String(selectedClient.value.country || 'Chile'),
      notes: String(selectedClient.value.notes || ''),
      internal_notes: String(selectedClient.value.internal_notes || '')
    }
  }

  function toggleCreateForm() {
    showCreateForm.value = !showCreateForm.value
    if (showCreateForm.value) {
      showEditForm.value = false
      resetCreateForm()
    }
  }

  function toggleEditForm() {
    showEditForm.value = !showEditForm.value
    if (showEditForm.value) {
      showCreateForm.value = false
      resetEditForm()
    }
  }

  async function loadClients() {
    loading.value = true
    error.value = ''
    try {
      const response = await api.get('/clients/')
      const payload = Array.isArray(response?.data) ? response.data : []
      clients.value = payload.map(normalizeClient)
      const routeClientId = Number(route.query?.client_id || 0)
      const hasRouteClient = routeClientId > 0 && clients.value.some(c => c.id === routeClientId)
      if (hasRouteClient) {
        selectedClientId.value = routeClientId
      } else if (!clients.value.some(c => c.id === selectedClientId.value)) {
        selectedClientId.value = clients.value[0]?.id || 0
      }
    } catch (requestError) {
      clients.value = []
      selectedClientId.value = 0
      error.value = extractErrorMessage(requestError)
    } finally {
      loading.value = false
    }
  }

  async function selectClient(client) {
    const id = Number(client?.id || 0)
    if (!id) return
    selectedClientId.value = id
  }

  async function createClient() {
    error.value = ''
    const payload = {
      name: String(createForm.value.name || '').trim(),
      email: String(createForm.value.email || '').trim() || null,
      phone: String(createForm.value.phone || '').trim() || null,
      phone_alt: String(createForm.value.phone_alt || '').trim() || null,
      address: String(createForm.value.address || '').trim() || null,
      city: String(createForm.value.city || '').trim() || null,
      region: String(createForm.value.region || '').trim() || null,
      country: String(createForm.value.country || 'Chile').trim() || 'Chile',
      notes: String(createForm.value.notes || '').trim() || null,
      internal_notes: String(createForm.value.internal_notes || '').trim() || null
    }
    if (!payload.name) {
      error.value = 'El nombre del cliente es obligatorio.'
      return
    }
    loading.value = true
    try {
      const response = await api.post('/clients/', payload)
      const createdId = Number(response?.data?.id || 0)
      showCreateForm.value = false
      resetCreateForm()
      await loadClients()
      if (createdId > 0) selectedClientId.value = createdId
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      loading.value = false
    }
  }

  async function updateSelectedClient() {
    if (!hasValidSelectedClient()) return
    error.value = ''
    loading.value = true
    try {
      const payload = {
        name: String(editForm.value.name || '').trim(),
        email: String(editForm.value.email || '').trim() || null,
        phone: String(editForm.value.phone || '').trim() || null,
        phone_alt: String(editForm.value.phone_alt || '').trim() || null,
        address: String(editForm.value.address || '').trim() || null,
        city: String(editForm.value.city || '').trim() || null,
        region: String(editForm.value.region || '').trim() || null,
        country: String(editForm.value.country || 'Chile').trim() || 'Chile',
        notes: String(editForm.value.notes || '').trim() || null,
        internal_notes: String(editForm.value.internal_notes || '').trim() || null
      }
      if (!payload.name) throw new Error('El nombre del cliente es obligatorio.')
      await api.put(`/clients/${selectedClientId.value}`, payload)
      showEditForm.value = false
      await loadClients()
    } catch (requestError) {
      error.value = requestError?.message || extractErrorMessage(requestError)
    } finally {
      loading.value = false
    }
  }

  async function deleteSelectedClient() {
    if (!hasValidSelectedClient()) return
    loading.value = true
    error.value = ''
    try {
      await api.delete(`/clients/${selectedClientId.value}`)
      showEditForm.value = false
      if (onClientDeleted) await onClientDeleted()
      await loadClients()
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      loading.value = false
    }
  }

  return {
    clients,
    searchQuery,
    selectedClient,
    filteredClients,
    createForm,
    editForm,
    showCreateForm,
    showEditForm,
    hasValidSelectedClient,
    loadClients,
    selectClient,
    toggleCreateForm,
    toggleEditForm,
    resetCreateForm,
    resetEditForm,
    createClient,
    updateSelectedClient,
    deleteSelectedClient,
  }
}
