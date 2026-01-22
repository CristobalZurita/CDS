import { defineStore } from 'pinia'
import { api } from '@/services/api'

export const useInventoryStore = defineStore('inventory', {
  state: () => ({
    items: [],
    loading: false,
    page: 1,
    limit: 20
  }),
  actions: {
    async fetchItems(page = 1, limit = 20, search = null, categoryId = null) {
      this.loading = true
      this.page = page
      this.limit = limit
      const q = new URLSearchParams({ limit: String(limit), page: String(page) })
      if (search) q.set('search', search)
      if (categoryId) q.set('category_id', String(categoryId))
      try {
        const res = await api.get(`/inventory?${q.toString()}`)
        this.items = res.data || []
      } catch (e) {
        this.items = []
      }
      this.loading = false
    }
      ,
    async deleteItem(itemId) {
      try {
        await api.delete(`/inventory/${itemId}`)
        // refresh list
        await this.fetchItems(this.page, this.limit)
        return true
      } catch (e) {
        console.error('Error deleting item', e)
        return false
      }
    },
    async updateItem(itemId, payload) {
      // Normalize payload: backend expects `stock` (some MODELOS use `quantity`)
      const body = Object.assign({}, payload)
      if (body.quantity !== undefined && body.stock === undefined) body.stock = body.quantity
      delete body.quantity
      const updatedRes = await api.put(`/inventory/${itemId}`, body)
      await this.fetchItems(this.page, this.limit)
      return updatedRes.data
    },
    async createItem(payload) {
      const body = Object.assign({}, payload)
      if (body.quantity !== undefined && body.stock === undefined) body.stock = body.quantity
      delete body.quantity
      const createdRes = await api.post('/inventory', body)
      await this.fetchItems(this.page, this.limit)
      return createdRes.data
    }
  }
})
