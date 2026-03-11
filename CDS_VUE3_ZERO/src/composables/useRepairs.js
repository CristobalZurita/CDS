/**
 * useRepairs - Composable para gestión de reparaciones (modo admin)
 * Extraído de LEGACY para uso en RepairsList
 */

import { ref } from 'vue'
import api from '@/services/api'

const repairs = ref([])
const isLoading = ref(false)
const error = ref(null)

export function useRepairs() {
  async function fetchRepairs() {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.get('/repairs')
      repairs.value = response.data || response || []
      return repairs.value
    } catch (e) {
      error.value = e.message || 'Error cargando reparaciones'
      console.error('Error fetching repairs:', e)
      return []
    } finally {
      isLoading.value = false
    }
  }

  async function deleteRepair(id) {
    if (!window.confirm('¿Eliminar esta reparación?')) return false
    try {
      await api.delete(`/repairs/${id}`)
      repairs.value = repairs.value.filter(r => r.id !== id)
      return true
    } catch (e) {
      console.error('Error deleting repair:', e)
      alert('Error eliminando reparación')
      return false
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
