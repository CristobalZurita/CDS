import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import api, { extractErrorMessage } from '@new/services/api'

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

function normalizeDevice(entry) {
  return {
    id: Number(entry?.id || 0),
    model: String(entry?.model || ''),
    serial_number: String(entry?.serial_number || ''),
    brand_other: String(entry?.brand_other || '')
  }
}

function normalizeRepair(entry) {
  return {
    id: Number(entry?.id || 0),
    repair_code: String(entry?.repair_code || entry?.repair_number || ''),
    repair_number: String(entry?.repair_number || ''),
    status_id: Number(entry?.status_id || 0),
    problem_reported: String(entry?.problem_reported || ''),
    created_at: entry?.created_at || null
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

function baseDeviceForm() {
  return {
    model: '',
    serial_number: '',
    brand_other: '',
    description: '',
    condition_notes: ''
  }
}

function baseRepairForm() {
  return {
    device_id: '',
    problem_reported: '',
    priority: 2,
    paid_amount: 20000,
    payment_method: 'cash',
    group_with_ot: false,
    ot_parent_id: ''
  }
}

export function useClientsPage() {
  const route = useRoute()

  const clients = ref([])
  const devices = ref([])
  const repairs = ref([])

  const loading = ref(false)
  const contextLoading = ref(false)
  const error = ref('')

  const searchQuery = ref('')
  const selectedClientId = ref(0)

  const showCreateForm = ref(false)
  const showEditForm = ref(false)
  const showDeviceForm = ref(false)
  const showRepairForm = ref(false)

  const createForm = ref(baseClientForm())
  const editForm = ref(baseClientForm())
  const deviceForm = ref(baseDeviceForm())
  const repairForm = ref(baseRepairForm())

  const selectedClient = computed(() => {
    return clients.value.find((client) => client.id === selectedClientId.value) || null
  })

  const filteredClients = computed(() => {
    const query = String(searchQuery.value || '').trim().toLowerCase()
    if (!query) return clients.value

    return clients.value.filter((client) => {
      const text = [
        client.client_code,
        client.name,
        client.email,
        client.phone,
        client.address
      ]
        .filter(Boolean)
        .join(' ')
        .toLowerCase()

      return text.includes(query)
    })
  })

  const sortedRepairs = computed(() => {
    return [...repairs.value].sort((a, b) => {
      const dateA = new Date(a.created_at || 0).getTime()
      const dateB = new Date(b.created_at || 0).getTime()
      return dateB - dateA
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

  function resetDeviceForm() {
    deviceForm.value = baseDeviceForm()
  }

  function resetRepairForm() {
    repairForm.value = baseRepairForm()
  }

  async function loadClients() {
    loading.value = true
    error.value = ''

    try {
      const response = await api.get('/clients/')
      const payload = Array.isArray(response?.data) ? response.data : []
      clients.value = payload.map(normalizeClient)

      const routeClientId = Number(route.query?.client_id || 0)
      const hasRouteClient = routeClientId > 0 && clients.value.some((client) => client.id === routeClientId)

      if (hasRouteClient) {
        selectedClientId.value = routeClientId
      } else if (!clients.value.some((client) => client.id === selectedClientId.value)) {
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

  async function loadSelectedClientContext() {
    if (!hasValidSelectedClient()) {
      devices.value = []
      repairs.value = []
      return
    }

    contextLoading.value = true

    try {
      const [devicesResponse, repairsResponse] = await Promise.all([
        api.get(`/clients/${selectedClientId.value}/devices`).catch(() => ({ data: [] })),
        api.get(`/clients/${selectedClientId.value}/repairs`).catch(() => ({ data: [] }))
      ])

      const devicesPayload = Array.isArray(devicesResponse?.data) ? devicesResponse.data : []
      const repairsPayload = Array.isArray(repairsResponse?.data) ? repairsResponse.data : []

      devices.value = devicesPayload.map(normalizeDevice)
      repairs.value = repairsPayload.map(normalizeRepair)

      const hasCurrentDevice = devices.value.some((device) => Number(device.id) === Number(repairForm.value.device_id || 0))
      if (!hasCurrentDevice) {
        repairForm.value.device_id = devices.value[0]?.id || ''
      }
    } catch {
      devices.value = []
      repairs.value = []
    } finally {
      contextLoading.value = false
    }
  }

  async function selectClient(client) {
    const id = Number(client?.id || 0)
    if (!id) return
    selectedClientId.value = id
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

  function toggleDeviceForm() {
    showDeviceForm.value = !showDeviceForm.value
    if (showDeviceForm.value) resetDeviceForm()
  }

  function toggleRepairForm() {
    showRepairForm.value = !showRepairForm.value
    if (showRepairForm.value) resetRepairForm()
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
      if (createdId > 0) {
        selectedClientId.value = createdId
      }
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

      if (!payload.name) {
        throw new Error('El nombre del cliente es obligatorio.')
      }

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
      devices.value = []
      repairs.value = []
      await loadClients()
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      loading.value = false
    }
  }

  async function createDeviceForSelectedClient() {
    if (!hasValidSelectedClient()) return

    error.value = ''

    const payload = {
      client_id: selectedClientId.value,
      model: String(deviceForm.value.model || '').trim(),
      serial_number: String(deviceForm.value.serial_number || '').trim() || null,
      brand_other: String(deviceForm.value.brand_other || '').trim() || null,
      description: String(deviceForm.value.description || '').trim() || null,
      condition_notes: String(deviceForm.value.condition_notes || '').trim() || null
    }

    if (!payload.model) {
      error.value = 'El modelo del dispositivo es obligatorio.'
      return
    }

    contextLoading.value = true

    try {
      await api.post('/devices/', payload)
      showDeviceForm.value = false
      resetDeviceForm()
      await loadSelectedClientContext()
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      contextLoading.value = false
    }
  }

  async function createRepairForSelectedClient() {
    if (!hasValidSelectedClient()) return

    error.value = ''

    const problemReported = String(repairForm.value.problem_reported || '').trim()
    if (!problemReported) {
      error.value = 'El problema reportado es obligatorio.'
      return
    }

    const payload = {
      client_id: selectedClientId.value,
      device_id: repairForm.value.device_id ? Number(repairForm.value.device_id) : undefined,
      model: devices.value.find((device) => device.id === Number(repairForm.value.device_id))?.model || 'Equipo',
      problem_reported: problemReported,
      priority: Number(repairForm.value.priority || 2),
      paid_amount: Number(repairForm.value.paid_amount || 0),
      payment_method: String(repairForm.value.payment_method || 'cash')
    }

    if (repairForm.value.group_with_ot && repairForm.value.ot_parent_id) {
      payload.ot_parent_id = Number(repairForm.value.ot_parent_id)
    }

    contextLoading.value = true

    try {
      await api.post('/repairs/', payload)
      showRepairForm.value = false
      resetRepairForm()
      await Promise.all([loadSelectedClientContext(), loadClients()])
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      contextLoading.value = false
    }
  }

  watch(selectedClientId, async () => {
    resetEditForm()
    await loadSelectedClientContext()
  })

  onMounted(async () => {
    await loadClients()
    await loadSelectedClientContext()
  })

  return {
    clients,
    devices,
    repairs: sortedRepairs,
    loading,
    contextLoading,
    error,
    searchQuery,
    selectedClientId,
    selectedClient,
    filteredClients,
    showCreateForm,
    showEditForm,
    showDeviceForm,
    showRepairForm,
    createForm,
    editForm,
    deviceForm,
    repairForm,
    selectClient,
    toggleCreateForm,
    toggleEditForm,
    toggleDeviceForm,
    toggleRepairForm,
    loadClients,
    createClient,
    updateSelectedClient,
    deleteSelectedClient,
    createDeviceForSelectedClient,
    createRepairForSelectedClient
  }
}
