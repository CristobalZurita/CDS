import { defineStore } from 'pinia'
import { useApi } from '@/composables/useApi'

export const useUsersStore = defineStore('users', {
  state: () => ({
    users: [],
    loading: false,
    error: null
  }),
  actions: {
    async fetchUsers() {
      this.loading = true
      try {
        this.users = await useApi().get('/api/users')
      } catch (e) {
        this.error = e
      } finally {
        this.loading = false
      }
    },
    async createUser(data) {
      return await useApi().post('/api/users', data)
    },
    async updateUser(id, data) {
      return await useApi().put(`/api/users/${id}`, data)
    },
    async deleteUser(id) {
      return await useApi().delete(`/api/users/${id}`)
    }
  }
})
