import { defineStore } from 'pinia'

export const useInventoryStore = defineStore('inventory', {
  state: () => ({
    items: [],
    loading: false,
    page: 1,
    limit: 20
  }),
  actions: {
    async fetchItems(page = 1, limit = 20, category = null) {
      this.loading = true
      this.page = page
      this.limit = limit
      const q = new URLSearchParams({ limit: String(limit), page: String(page) })
      if (category) q.set('category', category)
      const res = await fetch(`/api/v1/items?${q.toString()}`)
      if (!res.ok) {
        this.items = []
        this.loading = false
        return
      }
      this.items = await res.json()
      this.loading = false
    }
      ,
    async deleteItem(itemId) {
      const token = localStorage.getItem('access_token')
      const headers = token ? { Authorization: `Bearer ${token}` } : {}
      try {
        const res = await fetch(`/api/v1/items/${itemId}`, { method: 'DELETE', headers })
        if (!res.ok) {
          const text = await res.text()
          console.error('Failed to delete item', res.status, text)
          return false
        }
        // refresh list
        await this.fetchItems(this.page, this.limit)
        return true
      } catch (e) {
        console.error('Error deleting item', e)
        return false
      }
    },
    async updateItem(itemId, payload) {
      const token = localStorage.getItem('access_token')
      const headers = Object.assign({ 'Content-Type': 'application/json' }, token ? { Authorization: `Bearer ${token}` } : {})
      // Normalize payload: backend expects `stock` (some MODELOS use `quantity`)
      const body = Object.assign({}, payload)
      if (body.quantity !== undefined && body.stock === undefined) body.stock = body.quantity
      delete body.quantity
      const res = await fetch(`/api/v1/items/${itemId}`, { method: 'PUT', headers, body: JSON.stringify(body) })
      if (!res.ok) {
        const text = await res.text()
        throw new Error(`Update failed: ${res.status} ${text}`)
      }
      const updated = await res.json()
      await this.fetchItems(this.page, this.limit)
      return updated
    },
    async createItem(payload) {
      const token = localStorage.getItem('access_token')
      const headers = Object.assign({ 'Content-Type': 'application/json' }, token ? { Authorization: `Bearer ${token}` } : {})
      const body = Object.assign({}, payload)
      if (body.quantity !== undefined && body.stock === undefined) body.stock = body.quantity
      delete body.quantity
      const res = await fetch(`/api/v1/items`, { method: 'POST', headers, body: JSON.stringify(body) })
      if (!res.ok) {
        const text = await res.text()
        throw new Error(`Create failed: ${res.status} ${text}`)
      }
      const created = await res.json()
      await this.fetchItems(this.page, this.limit)
      return created
    }
  }
})
