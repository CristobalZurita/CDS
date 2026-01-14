import { defineStore } from 'pinia'
import { useApi } from '@/composables/useApi'

export const useInstrumentsStore = defineStore('instruments', {
  state: () => ({
    instruments: [],
    loading: false,
    error: null
  }),
  actions: {
    async fetchInstruments() {
      this.loading = true
      try {
        this.instruments = await useApi().get('/api/instruments')
      } catch (e) {
        this.error = e
      } finally {
        this.loading = false
      }
    },
    async createInstrument(data) {
      return await useApi().post('/api/instruments', data)
    },
    async updateInstrument(id, data) {
      return await useApi().put(`/api/instruments/${id}`, data)
    },
    async deleteInstrument(id) {
      return await useApi().delete(`/api/instruments/${id}`)
    }
  }
})
