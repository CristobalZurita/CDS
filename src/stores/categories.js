import { defineStore } from 'pinia'
import { useApi } from '@/composables/useApi'

export const useCategoriesStore = defineStore('categories', {
  state: () => ({
    categories: [],
    loading: false,
    error: null
  }),
  getters: {
    isLoading: (state) => state.loading
  },
  actions: {
    async fetchCategories() {
      this.error = null
      this.loading = true
      try {
        this.categories = await useApi().get('/categories')
      } catch (e) {
        this.error = e
        this.categories = []
      } finally {
        this.loading = false
      }
    },
    async createCategory(data) {
      const created = await useApi().post('/categories', data)
      this.categories.push(created)
      return created
    },
    async updateCategory(id, data) {
      const updated = await useApi().put(`/categories/${id}`, data)
      this.categories = this.categories.map((category) =>
        String(category.id) === String(id) ? updated : category
      )
      return updated
    },
    async deleteCategory(id) {
      const result = await useApi().delete(`/categories/${id}`)
      this.categories = this.categories.filter((category) => String(category.id) !== String(id))
      return result
    },
    setError(message) {
      this.error = message
    }
  }
})
