import { computed, onMounted, onBeforeUnmount, ref } from 'vue'
import { useRoute } from 'vue-router'
import api, { extractErrorMessage } from '@/services/api'

function toApiPath(path) {
  const value = String(path || '')
  if (!value) return ''
  if (value.startsWith('http://') || value.startsWith('https://')) return value
  if (value.startsWith('/api/')) return value

  const base = String(import.meta.env.VITE_API_URL || '/api/v1')
  const host = base.includes('/api/') ? base.split('/api/')[0] : ''
  if (!host) return value
  return `${host}${value.startsWith('/') ? '' : '/'}${value}`
}

function sanitizeFilePart(value) {
  const text = String(value || '').trim()
  if (!text) return 'OT'
  return text.replace(/[^a-zA-Z0-9._-]+/g, '_')
}

export function useRepairDetailPage() {
  const route = useRoute()

  const repair = ref(null)
  const timeline = ref([])
  const photos = ref([])
  const notes = ref([])

  const isLoading = ref(false)
  const loadingError = ref('')
  const downloadingPdf = ref(false)

  const repairId = computed(() => String(route.params.id || '').trim())

  const detail = computed(() => ({
    repair: repair.value,
    timeline: timeline.value,
    photos: photos.value,
    notes: notes.value
  }))

  function formatDate(value) {
    if (!value) return '—'
    const date = new Date(value)
    if (Number.isNaN(date.getTime())) return '—'
    return new Intl.DateTimeFormat('es-CL', { dateStyle: 'medium' }).format(date)
  }

  function formatPrice(value) {
    const amount = Number(value)
    if (!Number.isFinite(amount)) return '—'
    return new Intl.NumberFormat('es-CL', {
      style: 'currency',
      currency: 'CLP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount)
  }

  function resolvePhotoUrl(photo) {
    if (!photo || typeof photo !== 'object') return ''
    if (photo.photo_download_url) return String(photo.photo_download_url)
    if (photo.photo_url) return toApiPath(photo.photo_url)
    return ''
  }

  function clearDetail() {
    repair.value = null
    timeline.value = []
    photos.value = []
    notes.value = []
  }

  async function loadDetail() {
    if (!repairId.value) return

    isLoading.value = true
    loadingError.value = ''

    try {
      const response = await api.get(`/client/repairs/${repairId.value}/details`)
      const payload = response?.data || {}

      repair.value = payload.repair || null
      timeline.value = Array.isArray(payload.timeline) ? payload.timeline : []
      photos.value = Array.isArray(payload.photos)
        ? payload.photos.map((photo) => ({
          ...photo,
          resolved_photo_url: resolvePhotoUrl(photo)
        }))
        : []
      notes.value = Array.isArray(payload.notes) ? payload.notes : []
    } catch (error) {
      loadingError.value = extractErrorMessage(error)
      clearDetail()
    } finally {
      isLoading.value = false
    }
  }

  async function downloadClosurePdf() {
    if (!repairId.value) return

    downloadingPdf.value = true

    try {
      const response = await api.get(`/client/repairs/${repairId.value}/closure-pdf`, {
        responseType: 'blob'
      })

      const blob = new Blob([response.data], { type: 'application/pdf' })
      const blobUrl = window.URL.createObjectURL(blob)
      const preferredCode = detail.value?.repair?.repair_code || detail.value?.repair?.repair_number || detail.value?.repair?.id || `OT_${repairId.value}`

      const link = document.createElement('a')
      link.href = blobUrl
      link.download = `CIERRE_CLIENTE_${sanitizeFilePart(preferredCode)}.pdf`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(blobUrl)
    } catch (error) {
      loadingError.value = extractErrorMessage(error)
    } finally {
      downloadingPdf.value = false
    }
  }

  onMounted(loadDetail)
  onBeforeUnmount(clearDetail)

  return {
    detail,
    isLoading,
    loadingError,
    downloadingPdf,
    formatDate,
    formatPrice,
    loadDetail,
    downloadClosurePdf
  }
}
