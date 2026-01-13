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
        const { api } = useApi()
        this.users = await api.get('/api/v1/users')
      } catch (e) {
        this.error = e.message || String(e)
        this.users = []
      } finally {
        this.loading = false
      }
    },
    async createUser(data) {
      try {
        const { api } = useApi()
        return await api.post('/api/v1/users', data)
      } catch (e) {
        this.error = e.message || String(e)
        throw e
      }
    },
    async updateUser(id, data) {
      try {
        const { api } = useApi()
        return await api.put(`/api/v1/users/${id}`, data)
      } catch (e) {
        this.error = e.message || String(e)
        throw e
      }
    },
    async deleteUser(id) {
      try {
        const { api } = useApi()
        return await api.delete(`/api/v1/users/${id}`)
      } catch (e) {
        this.error = e.message || String(e)
        throw e
      }
    }
  }
})
