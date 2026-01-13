import { defineStore } from 'pinia'
import { useApi } from '@/composables/useApi'

export const useDiagnosticsStore = defineStore('diagnostics', {
  state: () => ({
    diagnostics: [],
    currentDiagnostic: null,
    calculationResult: null,
    loading: false,
    calculating: false,
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
    async fetchDiagnostic(id) {
      this.loading = true
      try {
        const { api } = useApi()
        this.currentDiagnostic = await api.get(`/api/v1/diagnostics/${id}`)
        return this.currentDiagnostic
      } catch (e) {
        this.error = e.message || String(e)
        throw e
      } finally {
        this.loading = false
      }
    },
    async fetchDiagnosticsWithQuotes() {
      this.loading = true
      try {
        const { api } = useApi()
        this.diagnostics = await api.get('/api/v1/diagnostics/with-quotes')
      } catch (e) {
        this.error = e.message || String(e)
        this.diagnostics = []
      } finally {
        this.loading = false
      }
    },
    async fetchDiagnosticsByConfidence(minConfidence) {
      this.loading = true
      try {
        const { api } = useApi()
        this.diagnostics = await api.get(`/api/v1/diagnostics/by-confidence/${minConfidence}`)
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
    async addNote(id, note) {
      try {
        const { api } = useApi()
        return await api.post(`/api/v1/diagnostics/${id}/notes`, { note })
      } catch (e) {
        this.error = e.message || String(e)
        throw e
      }
    },
    async calculateQuote(data) {
      this.calculating = true
      this.calculationResult = null
      try {
        const { api } = useApi()
        this.calculationResult = await api.post('/api/v1/diagnostics/calculate', data)
        return this.calculationResult
      } catch (e) {
        this.error = e.message || String(e)
        throw e
      } finally {
        this.calculating = false
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
    },
    clearCalculation() {
      this.calculationResult = null
    }
  }
})
