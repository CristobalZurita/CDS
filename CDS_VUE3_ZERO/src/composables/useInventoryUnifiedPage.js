import { computed, onMounted, ref } from 'vue'
import api, { extractErrorMessage } from '@/services/api'

const EMPTY_ALERTS = Object.freeze({
  critical_5: [],
  high_20: [],
  medium_50: [],
  low_min: [],
  counts: {}
})

function emptyAlerts() {
  return {
    critical_5: [],
    high_20: [],
    medium_50: [],
    low_min: [],
    counts: {}
  }
}

function toInventoryList(payload) {
  return Array.isArray(payload?.data) ? payload.data : []
}

function normalizeAlerts(payload) {
  const source = payload?.data && typeof payload.data === 'object' ? payload.data : EMPTY_ALERTS
  return {
    critical_5: Array.isArray(source.critical_5) ? source.critical_5 : [],
    high_20: Array.isArray(source.high_20) ? source.high_20 : [],
    medium_50: Array.isArray(source.medium_50) ? source.medium_50 : [],
    low_min: Array.isArray(source.low_min) ? source.low_min : [],
    counts: source.counts && typeof source.counts === 'object' ? source.counts : {}
  }
}

export function useInventoryUnifiedPage() {
  const loading = ref(false)
  const error = ref('')
  const alerts = ref(emptyAlerts())
  const inventory = ref([])

  const counts = computed(() => alerts.value?.counts || {})

  const topCritical = computed(() => {
    return Array.isArray(alerts.value.critical_5) ? alerts.value.critical_5.slice(0, 10) : []
  })

  const topHigh = computed(() => {
    return Array.isArray(alerts.value.high_20) ? alerts.value.high_20.slice(0, 10) : []
  })

  const familyBreakdown = computed(() => {
    const map = new Map()
    for (const item of inventory.value) {
      const key = String(item?.family || 'SIN_FAMILIA')
      map.set(key, (map.get(key) || 0) + 1)
    }
    return Array.from(map.entries())
      .map(([family, total]) => ({ family, total }))
      .sort((a, b) => b.total - a.total)
  })

  async function loadUnifiedInventory() {
    loading.value = true
    error.value = ''

    try {
      const [alertsRes, inventoryRes] = await Promise.all([
        api.get('/inventory/alerts/summary'),
        api.get('/inventory/')
      ])

      alerts.value = normalizeAlerts(alertsRes)
      inventory.value = toInventoryList(inventoryRes)
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
      alerts.value = emptyAlerts()
      inventory.value = []
    } finally {
      loading.value = false
    }
  }

  onMounted(loadUnifiedInventory)

  return {
    loading,
    error,
    inventory,
    counts,
    topCritical,
    topHigh,
    familyBreakdown,
    loadUnifiedInventory
  }
}
