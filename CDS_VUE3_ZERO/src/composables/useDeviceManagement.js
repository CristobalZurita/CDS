import { ref } from 'vue'
import api, { extractErrorMessage } from '@/services/api'
import { fetchClientDevices } from '@/services/deviceService'

function baseDeviceForm() {
  return {
    model: '',
    serial_number: '',
    brand_other: '',
    description: '',
    condition_notes: ''
  }
}

export function useDeviceManagement({ selectedClientId, contextLoading, error, onDeviceCreated }) {
  const devices = ref([])
  const deviceForm = ref(baseDeviceForm())
  const editingDeviceId = ref(0)
  const editingDeviceForm = ref(baseDeviceForm())
  const showDeviceForm = ref(false)

  function resetDeviceForm() {
    deviceForm.value = baseDeviceForm()
  }

  function resetEditingDeviceForm() {
    editingDeviceForm.value = baseDeviceForm()
  }

  function toggleDeviceForm() {
    showDeviceForm.value = !showDeviceForm.value
    if (showDeviceForm.value) {
      resetDeviceForm()
      cancelDeviceEdit()
    }
  }

  async function loadDevices(clientId) {
    try {
      devices.value = await fetchClientDevices(clientId)
    } catch {
      devices.value = []
    }
  }

  async function createDeviceForSelectedClient() {
    const clientId = Number(selectedClientId.value)
    if (!clientId) return

    error.value = ''

    const payload = {
      client_id: clientId,
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
      if (onDeviceCreated) await onDeviceCreated()
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      contextLoading.value = false
    }
  }

  async function startDeviceEdit(device) {
    const deviceId = Number(device?.id || 0)
    if (!deviceId) return

    error.value = ''
    contextLoading.value = true

    try {
      const response = await api.get(`/devices/${deviceId}`)
      const payload = response?.data || {}

      editingDeviceId.value = deviceId
      editingDeviceForm.value = {
        model: String(payload?.model || device?.model || ''),
        serial_number: String(payload?.serial_number || device?.serial_number || ''),
        brand_other: String(payload?.brand_other || device?.brand_other || ''),
        description: String(payload?.description || ''),
        condition_notes: String(payload?.condition_notes || '')
      }
      showDeviceForm.value = false
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      contextLoading.value = false
    }
  }

  function cancelDeviceEdit() {
    editingDeviceId.value = 0
    resetEditingDeviceForm()
  }

  async function saveDeviceForSelectedClient() {
    const deviceId = Number(editingDeviceId.value || 0)
    if (!deviceId) return

    error.value = ''

    const payload = {
      model: String(editingDeviceForm.value.model || '').trim(),
      serial_number: String(editingDeviceForm.value.serial_number || '').trim() || null,
      brand_other: String(editingDeviceForm.value.brand_other || '').trim() || null,
      description: String(editingDeviceForm.value.description || '').trim() || null,
      condition_notes: String(editingDeviceForm.value.condition_notes || '').trim() || null
    }

    if (!payload.model) {
      error.value = 'El modelo del dispositivo es obligatorio.'
      return
    }

    contextLoading.value = true

    try {
      await api.put(`/devices/${deviceId}`, payload)
      cancelDeviceEdit()
      if (onDeviceCreated) await onDeviceCreated()
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      contextLoading.value = false
    }
  }

  async function deleteDeviceForSelectedClient(device) {
    const deviceId = Number(device?.id || 0)
    if (!deviceId) return

    error.value = ''
    contextLoading.value = true

    try {
      await api.delete(`/devices/${deviceId}`)
      if (Number(editingDeviceId.value || 0) === deviceId) {
        cancelDeviceEdit()
      }
      if (onDeviceCreated) await onDeviceCreated()
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      contextLoading.value = false
    }
  }

  return {
    devices,
    deviceForm,
    editingDeviceId,
    editingDeviceForm,
    showDeviceForm,
    loadDevices,
    resetDeviceForm,
    resetEditingDeviceForm,
    toggleDeviceForm,
    createDeviceForSelectedClient,
    startDeviceEdit,
    cancelDeviceEdit,
    saveDeviceForSelectedClient,
    deleteDeviceForSelectedClient
  }
}
