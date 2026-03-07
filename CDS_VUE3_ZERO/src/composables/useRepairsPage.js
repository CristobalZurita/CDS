import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api, { extractErrorMessage } from '@new/services/api'
import {
  getRepairProgressByStatus,
  getRepairStatusBucket,
  getRepairStatusLabel,
  isActiveRepairStatus,
  normalizeRepairStatus
} from '@new/utils/repairStatus'

export function useRepairsPage() {
  const router = useRouter()

  const repairs = ref([])
  const isLoading = ref(false)
  const loadingError = ref('')
  const selectedStatus = ref('')

  const decoratedRepairs = computed(() => {
    return repairs.value.map((repair) => {
      const normalizedStatus = normalizeRepairStatus(repair?.status_normalized || repair?.status)
      const rawProgress = Number(repair?.progress)
      const progress = Number.isFinite(rawProgress) ? rawProgress : getRepairProgressByStatus(normalizedStatus)

      return {
        ...repair,
        status_normalized: normalizedStatus,
        status_bucket: getRepairStatusBucket(normalizedStatus),
        progress: Math.max(0, Math.min(100, Math.round(progress)))
      }
    })
  })

  const filteredRepairs = computed(() => {
    if (!selectedStatus.value) return decoratedRepairs.value
    return decoratedRepairs.value.filter((repair) => repair.status_bucket === selectedStatus.value)
  })

  function getStatusLabel(status) {
    return getRepairStatusLabel(status)
  }

  function formatDate(value) {
    if (!value) return '—'
    const date = new Date(value)
    if (Number.isNaN(date.getTime())) return '—'
    return new Intl.DateTimeFormat('es-CL', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    }).format(date)
  }

  function formatPrice(value) {
    const amount = Number(value)
    if (!Number.isFinite(amount)) return '—'
    return new Intl.NumberFormat('es-CL', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount)
  }

  function shouldShowProgress(repair) {
    return isActiveRepairStatus(repair?.status_normalized || repair?.status)
  }

  function viewRepair(repair) {
    if (!repair?.id) return
    router.push({ name: 'repair-detail', params: { id: String(repair.id) } })
  }

  async function loadRepairs() {
    isLoading.value = true
    loadingError.value = ''

    try {
      const response = await api.get('/client/repairs')
      repairs.value = Array.isArray(response?.data) ? response.data : []
    } catch (error) {
      loadingError.value = extractErrorMessage(error)
      repairs.value = []
    } finally {
      isLoading.value = false
    }
  }

  onMounted(loadRepairs)

  return {
    selectedStatus,
    filteredRepairs,
    isLoading,
    loadingError,
    getStatusLabel,
    formatDate,
    formatPrice,
    shouldShowProgress,
    viewRepair,
    loadRepairs
  }
}
