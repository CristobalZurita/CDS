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
        this.diagnostics = await useApi().get('/api/diagnostics')
      } catch (e) {
        this.error = e
      } finally {
        this.loading = false
      }
    },
    async createDiagnostic(data) {
      return await useApi().post('/api/diagnostics', data)
    },
    async updateDiagnostic(id, data) {
      return await useApi().put(`/api/diagnostics/${id}`, data)
    },
    async deleteDiagnostic(id) {
      return await useApi().delete(`/api/diagnostics/${id}`)
    }
  }
})
