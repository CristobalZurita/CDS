import { defineStore } from 'pinia'
import { useApi } from '@/composables/useApi'

export const useStockMovementsStore = defineStore('stockMovements', {
  state: () => ({
    movements: [],
    loading: false,
    error: null
  }),
  getters: {
    isLoading: (state) => state.loading
  },
  actions: {
    async fetchMovements() {
      this.error = null
      this.loading = true
      try {
        this.movements = await useApi().get('/stock-movements')
      } catch (e) {
        this.error = e
        this.movements = []
      } finally {
        this.loading = false
      }
    },
    async createMovement(data) {
      return await useApi().post('/stock-movements', data)
    },
    setError(message) {
      this.error = message
    }
  }
})
