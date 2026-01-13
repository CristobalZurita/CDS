import { defineStore } from 'pinia'
import { useApi } from '@/composables/useApi'

export const useRepairsStore = defineStore('repairs', {
  state: () => ({
    repairs: [],
    loading: false,
    error: null
  }),
  actions: {
    async fetchRepairs() {
      this.loading = true
      try {
        const { api } = useApi()
        this.repairs = await api.get('/api/v1/repairs')
      } catch (e) {
        this.error = e.message || String(e)
        this.repairs = []
      } finally {
        this.loading = false
      }
    },
    async createRepair(data) {
      try {
        const { api } = useApi()
        return await api.post('/api/v1/repairs', data)
      } catch (e) {
        this.error = e.message || String(e)
        throw e
      }
    },
    async updateRepair(id, data) {
      try {
        const { api } = useApi()
        return await api.put(`/api/v1/repairs/${id}`, data)
      } catch (e) {
        this.error = e.message || String(e)
        throw e
      }
    },
    async deleteRepair(id) {
      try {
        const { api } = useApi()
        return await api.delete(`/api/v1/repairs/${id}`)
      } catch (e) {
        this.error = e.message || String(e)
        throw e
      }
    }
  }
})
