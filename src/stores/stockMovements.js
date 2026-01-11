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
        this.movements = await useApi().get('/api/stock-movements')
      } catch (e) {
        this.error = e
      } finally {
        this.loading = false
      }
    },
    async createMovement(data) {
      return await useApi().post('/api/stock-movements', data)
    }
  }
})
