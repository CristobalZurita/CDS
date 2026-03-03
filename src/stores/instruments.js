import { defineStore } from 'pinia'
import { useApi } from '@/composables/useApi'

export const useInstrumentsStore = defineStore('instruments', {
  state: () => ({
    instruments: [],
    loading: false,
    error: null
  }),
  getters: {
    isLoading: (state) => state.loading
  },
  actions: {
    async fetchInstruments() {
      this.error = null
      this.loading = true
      try {
        this.instruments = await useApi().get('/instruments')
      } catch (e) {
        this.error = e
        this.instruments = []
      } finally {
        this.loading = false
      }
    },
    async createInstrument(data) {
      return await useApi().post('/instruments', data)
    },
    async updateInstrument(id, data) {
      return await useApi().put(`/instruments/${id}`, data)
    },
    async deleteInstrument(id) {
      return await useApi().delete(`/instruments/${id}`)
    },
    setError(message) {
      this.error = message
    }
  }
})
