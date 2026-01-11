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
        this.repairs = await useApi().get('/api/repairs')
      } catch (e) {
        this.error = e
      } finally {
        this.loading = false
      }
    },
    async createRepair(data) {
      return await useApi().post('/api/repairs', data)
    },
    async updateRepair(id, data) {
      return await useApi().put(`/api/repairs/${id}`, data)
    },
    async deleteRepair(id) {
      return await useApi().delete(`/api/repairs/${id}`)
    }
  }
})
