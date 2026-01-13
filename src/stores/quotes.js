import { defineStore } from 'pinia'
import { useApi } from '@/composables/useApi'

export const useQuotesStore = defineStore('quotes', {
  state: () => ({
    quotes: [],
    currentQuote: null,
    estimateResult: null,
    stats: null,
    loading: false,
    estimating: false,
    error: null
  }),
  actions: {
    async fetchQuotes() {
      this.loading = true
      try {
        const { api } = useApi()
        this.quotes = await api.get('/api/v1/quotes')
      } catch (e) {
        this.error = e.message || String(e)
        this.quotes = []
      } finally {
        this.loading = false
      }
    },
    async fetchQuote(id) {
      this.loading = true
      try {
        const { api } = useApi()
        this.currentQuote = await api.get(`/api/v1/quotes/${id}`)
        return this.currentQuote
      } catch (e) {
        this.error = e.message || String(e)
        throw e
      } finally {
        this.loading = false
      }
    },
    async fetchPendingQuotes() {
      this.loading = true
      try {
        const { api } = useApi()
        this.quotes = await api.get('/api/v1/quotes/pending')
      } catch (e) {
        this.error = e.message || String(e)
        this.quotes = []
      } finally {
        this.loading = false
      }
    },
    async fetchAcceptedQuotes() {
      this.loading = true
      try {
        const { api } = useApi()
        this.quotes = await api.get('/api/v1/quotes/accepted')
      } catch (e) {
        this.error = e.message || String(e)
        this.quotes = []
      } finally {
        this.loading = false
      }
    },
    async fetchExpiredQuotes() {
      this.loading = true
      try {
        const { api } = useApi()
        this.quotes = await api.get('/api/v1/quotes/expired')
      } catch (e) {
        this.error = e.message || String(e)
        this.quotes = []
      } finally {
        this.loading = false
      }
    },
    async fetchQuotesByStatus(status) {
      this.loading = true
      try {
        const { api } = useApi()
        this.quotes = await api.get(`/api/v1/quotes/by-status/${status}`)
      } catch (e) {
        this.error = e.message || String(e)
        this.quotes = []
      } finally {
        this.loading = false
      }
    },
    async fetchQuotesByDiagnostic(diagnosticId) {
      this.loading = true
      try {
        const { api } = useApi()
        this.quotes = await api.get(`/api/v1/quotes/by-diagnostic/${diagnosticId}`)
      } catch (e) {
        this.error = e.message || String(e)
        this.quotes = []
      } finally {
        this.loading = false
      }
    },
    async fetchQuotesByRepair(repairId) {
      this.loading = true
      try {
        const { api } = useApi()
        this.quotes = await api.get(`/api/v1/quotes/by-repair/${repairId}`)
      } catch (e) {
        this.error = e.message || String(e)
        this.quotes = []
      } finally {
        this.loading = false
      }
    },
    async fetchStats() {
      try {
        const { api } = useApi()
        this.stats = await api.get('/api/v1/quotes/stats')
        return this.stats
      } catch (e) {
        this.error = e.message || String(e)
        throw e
      }
    },
    async createQuote(data) {
      try {
        const { api } = useApi()
        return await api.post('/api/v1/quotes', data)
      } catch (e) {
        this.error = e.message || String(e)
        throw e
      }
    },
    async updateQuote(id, data) {
      try {
        const { api } = useApi()
        return await api.put(`/api/v1/quotes/${id}`, data)
      } catch (e) {
        this.error = e.message || String(e)
        throw e
      }
    },
    async updateQuoteStatus(id, status, notes = null) {
      try {
        const { api } = useApi()
        const payload = { status }
        if (notes) payload.notes = notes
        return await api.patch(`/api/v1/quotes/${id}/status`, payload)
      } catch (e) {
        this.error = e.message || String(e)
        throw e
      }
    },
    async estimateQuote(data) {
      this.estimating = true
      this.estimateResult = null
      try {
        const { api } = useApi()
        this.estimateResult = await api.post('/api/v1/quotes/estimate', data)
        return this.estimateResult
      } catch (e) {
        this.error = e.message || String(e)
        throw e
      } finally {
        this.estimating = false
      }
    },
    async deleteQuote(id) {
      try {
        const { api } = useApi()
        return await api.delete(`/api/v1/quotes/${id}`)
      } catch (e) {
        this.error = e.message || String(e)
        throw e
      }
    },
    clearEstimate() {
      this.estimateResult = null
    }
  }
})
