/**
 * useUsers - Composable para gestión de usuarios
 * Extraído de LEGACY para uso en UserList
 */

import { ref } from 'vue'
import api from '@/services/api'

const users = ref([])
const isLoading = ref(false)
const error = ref(null)

export function useUsers() {
  async function fetchUsers() {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.get('/users')
      users.value = response.data || response || []
      return users.value
    } catch (e) {
      error.value = e.message || 'Error cargando usuarios'
      console.error('Error fetching users:', e)
      return []
    } finally {
      isLoading.value = false
    }
  }

  async function createUser(data) {
    try {
      const response = await api.post('/users', data)
      users.value.push(response.data || response)
      return response.data || response
    } catch (e) {
      console.error('Error creating user:', e)
      throw e
    }
  }

  async function updateUser(id, data) {
    try {
      const response = await api.put(`/users/${id}`, data)
      const index = users.value.findIndex(u => u.id === id)
      if (index !== -1) {
        users.value[index] = { ...users.value[index], ...(response.data || response) }
      }
      return response.data || response
    } catch (e) {
      console.error('Error updating user:', e)
      throw e
    }
  }

  async function deleteUser(id) {
    if (!window.confirm('¿Eliminar este usuario?')) return false
    try {
      await api.delete(`/users/${id}`)
      users.value = users.value.filter(u => u.id !== id)
      return true
    } catch (e) {
      console.error('Error deleting user:', e)
      alert('Error eliminando usuario')
      return false
    }
  }

  return {
    users,
    isLoading,
    error,
    fetchUsers,
    createUser,
    updateUser,
    deleteUser
  }
}
