import { defineStore } from 'pinia'
import { useApi } from '@/composables/useApi'

export const useRepairsStore = defineStore('repairs', {
  state: () => ({
    repairs: [],
    loading: false,
    error: null
  }),
  actions: {
    async fetchRepairs() {
      this.error = null
      this.loading = true
      try {
        this.repairs = await useApi().get('/repairs/')
        return this.repairs
      } catch (e) {
        this.error = e
        this.repairs = []
        return []
      } finally {
        this.loading = false
      }
    },
    async createRepair(data) {
      const created = await useApi().post('/repairs/', data)
      this.repairs.unshift(created)
      return created
    },
    async updateRepair(id, data) {
      const updated = await useApi().put(`/repairs/${id}`, data)
      this.repairs = this.repairs.map((repair) =>
        String(repair.id) === String(id) ? updated : repair
      )
      return updated
    },
    async deleteRepair(id) {
      const result = await useApi().delete(`/repairs/${id}`)
      this.repairs = this.repairs.filter((repair) => String(repair.id) !== String(id))
      return result
    }
  }
})
