import { defineStore } from 'pinia'
import { useApi } from '@/composables/useApi'
import { useInstrumentsCatalog } from '@/composables/useInstrumentsCatalog'

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
        const { api } = useApi()
        this.instruments = await api.get('/api/instruments')
      } catch (e) {
        // Fallback: use catalog data
        const catalog = useInstrumentsCatalog()
        this.instruments = catalog.getAllInstruments()
        this.error = 'Using local data: API unavailable'
      } finally {
        this.loading = false
      }
    },
    async createInstrument(data) {
      try {
        const { api } = useApi()
        return await api.post('/api/instruments', data)
      } catch (e) {
        this.error = e.message
        throw e
      }
    },
    async updateInstrument(id, data) {
      try {
        const { api } = useApi()
        return await api.put(`/api/instruments/${id}`, data)
      } catch (e) {
        this.error = e.message
        throw e
      }
    },
    async deleteInstrument(id) {
      try {
        const { api } = useApi()
        return await api.delete(`/api/instruments/${id}`)
      } catch (e) {
        this.error = e.message
        throw e
      }
    }
  }
})
