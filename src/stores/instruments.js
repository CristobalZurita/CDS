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
        this.instruments = await useApi().get('/instruments')
      } catch (e) {
        this.error = e
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
    }
  }
})
