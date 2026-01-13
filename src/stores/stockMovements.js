import { defineStore } from 'pinia'
import { useApi } from '@/composables/useApi'

export const useStockMovementsStore = defineStore('stockMovements', {
  state: () => ({
    movements: [],
    loading: false,
    error: null
  }),
  actions: {
    async fetchMovements() {
      this.loading = true
      try {
        const { api } = useApi()
        this.movements = await api.get('/api/v1/stock-movements')
      } catch (e) {
        this.error = e.message || String(e)
        this.movements = []
      } finally {
        this.loading = false
      }
    },
    async createMovement(data) {
      try {
        const { api } = useApi()
        return await api.post('/api/v1/stock-movements', data)
      } catch (e) {
        this.error = e.message || String(e)
        throw e
      }
    },
    async updateMovement(id, data) {
      try {
        const { api } = useApi()
        return await api.put(`/api/v1/stock-movements/${id}`, data)
      } catch (e) {
        this.error = e.message || String(e)
        throw e
      }
    },
    async deleteMovement(id) {
      try {
        const { api } = useApi()
        return await api.delete(`/api/v1/stock-movements/${id}`)
      } catch (e) {
        this.error = e.message || String(e)
        throw e
      }
    }
  }
})
