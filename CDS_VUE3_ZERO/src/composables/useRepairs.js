/**
 * useRepairs - Composable para gestión de reparaciones (modo admin)
 * Extraído de LEGACY para uso en RepairsList
 */

import { ref } from 'vue'
import api, { extractErrorMessage } from '@/services/api'

function toRepairList(payload) {
  return Array.isArray(payload?.data) ? payload.data : []
}

export function useRepairs() {
  const repairs = ref([])
  const isLoading = ref(false)
  const error = ref('')

  async function fetchRepairs() {
    isLoading.value = true
    error.value = ''
    try {
      const response = await api.get('/repairs/')
      repairs.value = toRepairList(response)
      return repairs.value
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
      repairs.value = []
      return []
    } finally {
      isLoading.value = false
    }
  }

  async function deleteRepair(id) {
    error.value = ''
    try {
      await api.delete(`/repairs/${id}`)
      repairs.value = repairs.value.filter(r => r.id !== id)
      return true
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
      throw requestError
    }
  }

  return {
    repairs,
    isLoading,
    error,
    fetchRepairs,
    deleteRepair
  }
}
