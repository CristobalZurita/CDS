import { defineStore } from 'pinia'
import { useApi } from '@/composables/useApi'

export const useUsersStore = defineStore('users', {
  state: () => ({
    users: [],
    loading: false,
    error: null
  }),
  getters: {
    isLoading: (state) => state.loading
  },
  actions: {
    async fetchUsers() {
      this.error = null
      this.loading = true
      try {
        this.users = await useApi().get('/users')
      } catch (e) {
        this.error = e
        this.users = []
      } finally {
        this.loading = false
      }
    },
    async createUser(data) {
      const created = await useApi().post('/users/', data)
      this.users.push(created)
      return created
    },
    async updateUser(id, data) {
      const updated = await useApi().put(`/users/${id}`, data)
      this.users = this.users.map((user) =>
        String(user.id) === String(id) ? updated : user
      )
      return updated
    },
    async deleteUser(id) {
      const result = await useApi().delete(`/users/${id}`)
      this.users = this.users.filter((user) => String(user.id) !== String(id))
      return result
    },
    setError(message) {
      this.error = message
    }
  }
})
