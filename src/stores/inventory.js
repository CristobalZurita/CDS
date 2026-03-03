import { defineStore } from 'pinia'
import { api } from '@/services/api'

export const useInventoryStore = defineStore('inventory', {
  state: () => ({
    items: [],
    loading: false,
    error: null,
    page: 1,
    limit: 20,
    catalogStatus: null,
    syncingCatalog: false,
    importing: false,
    lastRunId: null,
    runStatus: null,
  }),
  getters: {
    isLoading: (state) => state.loading
  },
  actions: {
    async fetchItems(page = 1, limit = 20, search = null, categoryId = null) {
      this.loading = true
      this.error = null
      this.page = page
      this.limit = limit
      const q = new URLSearchParams({ limit: String(limit), page: String(page) })
      if (search) q.set('search', search)
      if (categoryId) q.set('category_id', String(categoryId))
      try {
        const res = await api.get(`/inventory/?${q.toString()}`)
        this.items = res.data || []
      } catch (e) {
        this.error = e
        this.items = []
      }
      this.loading = false
      return this.items
    }
      ,
    async deleteItem(itemId) {
      this.error = null
      try {
        await api.delete(`/inventory/${itemId}`)
        this.items = this.items.filter((item) => String(item.id) !== String(itemId))
        return true
      } catch (e) {
        this.error = e
        console.error('Error deleting item', e)
        return false
      }
    },
    async updateItem(itemId, payload) {
      this.error = null
      // Normalize payload: backend expects `stock` (some MODELOS use `quantity`)
      const body = Object.assign({}, payload)
      if (body.quantity !== undefined && body.stock === undefined) body.stock = body.quantity
      delete body.quantity
      try {
        const updatedRes = await api.put(`/inventory/${itemId}`, body)
        const updated = updatedRes.data
        this.items = this.items.map((item) =>
          String(item.id) === String(itemId) ? { ...item, ...updated } : item
        )
        return updated
      } catch (e) {
        this.error = e
        throw e
      }
    },
    async createItem(payload) {
      this.error = null
      const body = Object.assign({}, payload)
      if (body.quantity !== undefined && body.stock === undefined) body.stock = body.quantity
      delete body.quantity
      try {
        const createdRes = await api.post('/inventory/', body)
        const created = createdRes.data
        this.items = [created, ...this.items.filter((item) => String(item.id) !== String(created.id))]
        return created
      } catch (e) {
        this.error = e
        throw e
      }
    },
    async fetchCatalogStatus() {
      this.error = null
      try {
        const res = await api.get('/inventory/store-catalog/status')
        this.catalogStatus = res.data || null
        return this.catalogStatus
      } catch (e) {
        this.error = e
        throw e
      }
    },
    async fetchItemById(itemId) {
      this.error = null
      try {
        const res = await api.get(`/inventory/${itemId}`)
        const item = res.data || null
        if (!item) return null
        const index = this.items.findIndex((existing) => String(existing.id) === String(itemId))
        if (index >= 0) {
          this.items.splice(index, 1, { ...this.items[index], ...item })
        } else {
          this.items.unshift(item)
        }
        return item
      } catch (e) {
        this.error = e
        throw e
      }
    },
    async syncCatalog() {
      if (this.syncingCatalog) return null
      this.error = null
      this.syncingCatalog = true
      try {
        const res = await api.post('/inventory/store-catalog/sync')
        const data = res.data || {}
        this.catalogStatus = data.status || null
        await this.fetchItems(this.page, this.limit)
        return data
      } catch (e) {
        this.error = e
        throw e
      } finally {
        this.syncingCatalog = false
      }
    },
    async triggerImport() {
      if (this.importing) {
        return {
          run_id: this.lastRunId,
          status: this.runStatus,
        }
      }
      this.error = null
      this.importing = true
      try {
        const res = await api.post('/imports/run')
        const data = res.data || {}
        this.lastRunId = data.run_id || null
        this.runStatus = data.status || null
        return data
      } catch (e) {
        this.error = e
        throw e
      } finally {
        this.importing = false
      }
    },
    setError(message) {
      this.error = message
    }
  }
})
