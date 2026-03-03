import { defineStore } from 'pinia'
import { useApi } from '@/composables/useApi'
import { hydrateRepairPhotos, revokeHydratedRepairPhotos } from '@/services/secureMedia'

export const useRepairsStore = defineStore('repairs', {
  state: () => ({
    repairs: [],
    currentRepair: null,
    currentRepairTimeline: [],
    currentRepairPhotos: [],
    currentRepairNotes: [],
    loading: false,
    error: null
  }),
  getters: {
    isLoading: (state) => state.loading
  },
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
    async fetchClientRepairs() {
      this.error = null
      this.loading = true
      try {
        this.repairs = await useApi().get('/client/repairs')
        return this.repairs
      } catch (e) {
        this.error = e
        this.repairs = []
        return []
      } finally {
        this.loading = false
      }
    },
    async fetchClientRepairDetail(id) {
      this.error = null
      this.loading = true
      try {
        const detail = await useApi().get(`/client/repairs/${id}/details`)
        const nextPhotos = await hydrateRepairPhotos(detail?.photos || [])
        revokeHydratedRepairPhotos(this.currentRepairPhotos || [])
        this.currentRepair = detail?.repair || null
        this.currentRepairTimeline = detail?.timeline || []
        this.currentRepairPhotos = nextPhotos
        this.currentRepairNotes = detail?.notes || []
        return detail
      } catch (e) {
        this.error = e
        this.currentRepair = null
        this.currentRepairTimeline = []
        revokeHydratedRepairPhotos(this.currentRepairPhotos || [])
        this.currentRepairPhotos = []
        this.currentRepairNotes = []
        throw e
      } finally {
        this.loading = false
      }
    },
    async downloadClientClosurePdf(id) {
      this.error = null
      try {
        return await useApi().get(`/client/repairs/${id}/closure-pdf`, {
          responseType: 'blob'
        })
      } catch (e) {
        this.error = e
        throw e
      }
    },
    clearCurrentRepairDetail() {
      revokeHydratedRepairPhotos(this.currentRepairPhotos || [])
      this.currentRepair = null
      this.currentRepairTimeline = []
      this.currentRepairPhotos = []
      this.currentRepairNotes = []
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
    },
    setError(message) {
      this.error = message
    }
  }
})
