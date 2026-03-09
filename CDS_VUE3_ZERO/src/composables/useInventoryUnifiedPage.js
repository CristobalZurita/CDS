import { computed, onMounted, ref } from 'vue'
import api, { extractErrorMessage } from '@/services/api'

export function useInventoryUnifiedPage() {
  const loading = ref(false)
  const error = ref('')
  const alerts = ref({
    critical_5: [],
    high_20: [],
    medium_50: [],
    low_min: [],
    counts: {}
  })
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

      alerts.value = alertsRes?.data || {
        critical_5: [],
        high_20: [],
        medium_50: [],
        low_min: [],
        counts: {}
      }

      inventory.value = Array.isArray(inventoryRes?.data) ? inventoryRes.data : []
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
      alerts.value = { critical_5: [], high_20: [], medium_50: [], low_min: [], counts: {} }
      inventory.value = []
    } finally {
      loading.value = false
    }
  }

  onMounted(loadUnifiedInventory)

  return {
    loading,
    error,
    counts,
    topCritical,
    topHigh,
    familyBreakdown,
    loadUnifiedInventory
  }
}
