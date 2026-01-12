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
        this.categories = await useApi().get('/api/categories')
      } catch (e) {
        this.error = e
      } finally {
        this.loading = false
      }
    },
    async createCategory(data) {
      return await useApi().post('/api/categories', data)
    },
    async updateCategory(id, data) {
      return await useApi().put(`/api/categories/${id}`, data)
    },
    async deleteCategory(id) {
      return await useApi().delete(`/api/categories/${id}`)
    }
  }
})
