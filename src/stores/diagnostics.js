import { defineStore } from 'pinia'
import { useApi } from '@/composables/useApi'

export const useDiagnosticsStore = defineStore('diagnostics', {
  state: () => ({
    diagnostics: [],
    loading: false,
    error: null
  }),
  getters: {
    isLoading: (state) => state.loading
  },
  actions: {
    async fetchDiagnostics() {
      this.error = null
      this.loading = true
      try {
        this.diagnostics = await useApi().get('/diagnostic')
      } catch (e) {
        this.error = e
        this.diagnostics = []
      } finally {
        this.loading = false
      }
    },
    async createDiagnostic(data) {
      return await useApi().post('/diagnostic/calculate', data)
    },
    async updateDiagnostic(id, data) {
      return await useApi().put(`/diagnostic/${id}`, data)
    },
    async deleteDiagnostic(id) {
      return await useApi().delete(`/diagnostic/${id}`)
    },
    setError(message) {
      this.error = message
    }
  }
})
