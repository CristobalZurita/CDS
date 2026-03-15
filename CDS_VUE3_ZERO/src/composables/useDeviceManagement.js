import { ref } from 'vue'
import api, { extractErrorMessage } from '@/services/api'

function normalizeDevice(entry) {
  return {
    id: Number(entry?.id || 0),
    model: String(entry?.model || ''),
    serial_number: String(entry?.serial_number || ''),
    brand_other: String(entry?.brand_other || '')
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

export function useDeviceManagement({ selectedClientId, contextLoading, error, onDeviceCreated }) {
  const devices = ref([])
  const deviceForm = ref(baseDeviceForm())
  const showDeviceForm = ref(false)

  function resetDeviceForm() {
    deviceForm.value = baseDeviceForm()
  }

  function toggleDeviceForm() {
    showDeviceForm.value = !showDeviceForm.value
    if (showDeviceForm.value) resetDeviceForm()
  }

  async function loadDevices(clientId) {
    const response = await api.get(`/clients/${clientId}/devices`).catch(() => ({ data: [] }))
    const payload = Array.isArray(response?.data) ? response.data : []
    devices.value = payload.map(normalizeDevice)
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

  return {
    devices,
    deviceForm,
    showDeviceForm,
    loadDevices,
    resetDeviceForm,
    toggleDeviceForm,
    createDeviceForSelectedClient
  }
}
