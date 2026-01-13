import { defineStore } from 'pinia'
import { useApi } from '@/composables/useApi'

export const useDiagnosticsStore = defineStore('diagnostics', {
  state: () => ({
    diagnostics: [],
    loading: false,
    error: null
  }),
  actions: {
    async fetchDiagnostics() {
      this.loading = true
      try {
        const { api } = useApi()
        this.diagnostics = await api.get('/api/v1/diagnostics')
      } catch (e) {
        this.error = e.message || String(e)
        this.diagnostics = []
      } finally {
        this.loading = false
      }
    },
    async createDiagnostic(data) {
      try {
        const { api } = useApi()
        return await api.post('/api/v1/diagnostics', data)
      } catch (e) {
        this.error = e.message || String(e)
        throw e
      }
    },
    async updateDiagnostic(id, data) {
      try {
        const { api } = useApi()
        return await api.put(`/api/v1/diagnostics/${id}`, data)
      } catch (e) {
        this.error = e.message || String(e)
        throw e
      }
    },
    async deleteDiagnostic(id) {
      try {
        const { api } = useApi()
        return await api.delete(`/api/v1/diagnostics/${id}`)
      } catch (e) {
        this.error = e.message || String(e)
        throw e
      }
    }
  }
})
