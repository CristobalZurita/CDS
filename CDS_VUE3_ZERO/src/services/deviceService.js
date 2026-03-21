import api from '@/services/api'

export function normalizeDeviceListItem(entry) {
  return {
    id: Number(entry?.id || 0),
    model: String(entry?.model || ''),
    serial_number: String(entry?.serial_number || ''),
    brand_other: String(entry?.brand_other || '')
  }
}

export async function fetchClientDevices(clientId) {
  const response = await api.get(`/clients/${clientId}/devices`)
  const payload = Array.isArray(response?.data) ? response.data : []
  return payload.map(normalizeDeviceListItem)
}
