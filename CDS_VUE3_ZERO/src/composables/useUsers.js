/**
 * useUsers - Composable para gestión de usuarios
 * Extraído de LEGACY para uso en UserList
 */

import { ref } from 'vue'
import api, { extractErrorMessage } from '@/services/api'

function toUserList(payload) {
  return Array.isArray(payload?.data) ? payload.data : []
}

function toUserEntity(payload) {
  return payload?.data && typeof payload.data === 'object' ? payload.data : null
}

export function useUsers() {
  const users = ref([])
  const isLoading = ref(false)
  const error = ref('')

  async function fetchUsers() {
    isLoading.value = true
    error.value = ''
    try {
      const response = await api.get('/users/')
      users.value = toUserList(response)
      return users.value
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
      users.value = []
      return []
    } finally {
      isLoading.value = false
    }
  }

  async function createUser(data) {
    error.value = ''
    try {
      const response = await api.post('/users/', data)
      const createdUser = toUserEntity(response)
      if (createdUser) {
        users.value.push(createdUser)
      }
      return createdUser
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
      throw requestError
    }
  }

  async function updateUser(id, data) {
    error.value = ''
    try {
      const response = await api.put(`/users/${id}`, data)
      const updatedUser = toUserEntity(response)
      const index = users.value.findIndex(u => u.id === id)
      if (index !== -1 && updatedUser) {
        users.value[index] = { ...users.value[index], ...updatedUser }
      }
      return updatedUser
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
      throw requestError
    }
  }

  async function deleteUser(id) {
    error.value = ''
    try {
      await api.delete(`/users/${id}`)
      users.value = users.value.filter(u => u.id !== id)
      return true
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
      throw requestError
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
