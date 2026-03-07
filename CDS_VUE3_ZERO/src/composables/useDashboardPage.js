import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api, { extractErrorMessage } from '@new/services/api'
import { useAuthStore } from '@new/stores/auth'
import {
  getRepairProgressByStatus,
  getRepairStatusLabel,
  normalizeRepairStatus
} from '@new/utils/repairStatus'

function normalizeDashboardResponse(payload) {
  if (!payload || typeof payload !== 'object') {
    return {
      user: null,
      stats: {},
      active_repairs: [],
      notifications: []
    }
  }

  return {
    user: payload.user || null,
    stats: payload.stats || {},
    active_repairs: Array.isArray(payload.active_repairs) ? payload.active_repairs : [],
    notifications: Array.isArray(payload.notifications) ? payload.notifications : []
  }
}

export function useDashboardPage() {
  const router = useRouter()
  const authStore = useAuthStore()

  const activeRepairsList = ref([])
  const notifications = ref([])
  const stats = ref({
    pending_repairs: 0,
    active_repairs: 0,
    completed_repairs: 0,
    total_spent: 0,
    pending_ot_payments: 0
  })

  const isLoading = ref(false)
  const loadingError = ref('')

  const userFirstName = computed(() => {
    const fullName = authStore.user?.full_name || ''
    const trimmed = String(fullName).trim()
    if (!trimmed) return 'cliente'
    return trimmed.split(/\s+/)[0] || 'cliente'
  })

  const pendingRepairs = computed(() => Number(stats.value.pending_repairs || 0))
  const activeRepairs = computed(() => Number(stats.value.active_repairs || 0))
  const completedRepairs = computed(() => Number(stats.value.completed_repairs || 0))
  const pendingOtPayments = computed(() => Number(stats.value.pending_ot_payments || 0))

  const totalSpent = computed(() => {
    const amount = Number(stats.value.total_spent || 0)
    return new Intl.NumberFormat('es-CL', {
      style: 'currency',
      currency: 'CLP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount)
  })

  function normalizeRepair(rawRepair) {
    const status = normalizeRepairStatus(rawRepair?.status_normalized || rawRepair?.status)
    const progress = Number.isFinite(Number(rawRepair?.progress))
      ? Number(rawRepair.progress)
      : getRepairProgressByStatus(status)

    return {
      ...rawRepair,
      status_normalized: status,
      progress: Math.max(0, Math.min(100, Math.round(progress)))
    }
  }

  function normalizeNotification(rawNotification) {
    return {
      id: rawNotification?.id || `notif-${Date.now()}`,
      type: String(rawNotification?.type || 'info').toLowerCase(),
      message: String(rawNotification?.message || ''),
      date: rawNotification?.date || null
    }
  }

  function getStatusLabel(status) {
    return getRepairStatusLabel(status)
  }

  function getStatusClass(status) {
    return normalizeRepairStatus(status)
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

  function formatTime(value) {
    if (!value) return 'Ahora'
    const date = new Date(value)
    if (Number.isNaN(date.getTime())) return 'Ahora'

    const now = new Date()
    const diff = now.getTime() - date.getTime()

    if (diff < 60 * 1000) return 'Hace unos segundos'
    if (diff < 60 * 60 * 1000) return `Hace ${Math.floor(diff / (60 * 1000))} minutos`
    if (diff < 24 * 60 * 60 * 1000) return `Hace ${Math.floor(diff / (60 * 60 * 1000))} horas`

    return formatDate(date)
  }

  function getNotificationIcon(type) {
    const map = {
      update: 'Actualizacion',
      info: 'Info',
      warning: 'Alerta',
      error: 'Error',
      success: 'OK'
    }
    return map[type] || 'Info'
  }

  function dismissNotification(notificationId) {
    notifications.value = notifications.value.filter((entry) => entry.id !== notificationId)
  }

  function viewRepair(repair) {
    if (!repair?.id) return
    router.push({ name: 'repair-detail', params: { id: String(repair.id) } })
  }

  async function handleLogout() {
    await authStore.logout()
    router.push({ name: 'login' })
  }

  async function loadDashboard() {
    isLoading.value = true
    loadingError.value = ''

    try {
      const response = await api.get('/client/dashboard')
      const normalized = normalizeDashboardResponse(response?.data)

      if (normalized.user && typeof normalized.user === 'object') {
        authStore.user = {
          ...authStore.user,
          ...normalized.user
        }
      }

      stats.value = {
        pending_repairs: Number(normalized.stats.pending_repairs || 0),
        active_repairs: Number(normalized.stats.active_repairs || 0),
        completed_repairs: Number(normalized.stats.completed_repairs || 0),
        total_spent: Number(normalized.stats.total_spent || 0),
        pending_ot_payments: Number(normalized.stats.pending_ot_payments || 0)
      }

      activeRepairsList.value = normalized.active_repairs.map(normalizeRepair)
      notifications.value = normalized.notifications.map(normalizeNotification)
    } catch (error) {
      loadingError.value = extractErrorMessage(error)
      activeRepairsList.value = []
      notifications.value = []
    } finally {
      isLoading.value = false
    }
  }

  onMounted(loadDashboard)

  return {
    isLoading,
    loadingError,
    userFirstName,
    pendingRepairs,
    activeRepairs,
    completedRepairs,
    totalSpent,
    pendingOtPayments,
    activeRepairsList,
    notifications,
    getStatusLabel,
    getStatusClass,
    formatDate,
    formatTime,
    getNotificationIcon,
    dismissNotification,
    viewRepair,
    handleLogout,
    loadDashboard
  }
}
