import { defineStore } from 'pinia'
import { useApi } from '@/composables/useApi'

export const useCategoriesStore = defineStore('categories', {
  state: () => ({
    categories: [],
    loading: false,
    error: null
  }),
  actions: {
    async fetchCategories() {
      this.loading = true
      try {
        const { api } = useApi()
        this.categories = await api.get('/api/v1/categories')
      } catch (e) {
        this.error = e.message || String(e)
        this.categories = []
      } finally {
        this.loading = false
      }
    },
    async createCategory(data) {
      try {
        const { api } = useApi()
        return await api.post('/api/v1/categories', data)
      } catch (e) {
        this.error = e.message || String(e)
        throw e
      }
    },
    async updateCategory(id, data) {
      try {
        const { api } = useApi()
        return await api.put(`/api/v1/categories/${id}`, data)
      } catch (e) {
        this.error = e.message || String(e)
        throw e
      }
    },
    async deleteCategory(id) {
      try {
        const { api } = useApi()
        return await api.delete(`/api/v1/categories/${id}`)
      } catch (e) {
        this.error = e.message || String(e)
        throw e
      }
    }
  }
})
