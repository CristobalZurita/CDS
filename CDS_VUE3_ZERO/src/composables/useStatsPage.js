import { computed, onMounted, ref } from 'vue'
import { extractErrorMessage, } from '@/services/api'
import {
  buildStatsCards,
  buildStatsChartPanels,
  buildStatsSummaryPanels,
  createEmptyStatsBundle,
  fetchStatsPageBundle
} from '@/services/statsPageService'

export function useStatsPage() {
  const isLoading = ref(false)
  const error = ref('')
  const bundle = ref(createEmptyStatsBundle())

  const cards = computed(() => buildStatsCards(bundle.value.stats))
  const summaryPanels = computed(() => buildStatsSummaryPanels(bundle.value))
  const chartPanels = computed(() => buildStatsChartPanels(bundle.value))

  const stats = computed(() => bundle.value.stats)
  const kpiSummary = computed(() => bundle.value.kpiSummary)
  const kpiDashboard = computed(() => bundle.value.kpiDashboard)
  const kpiRevenue = computed(() => bundle.value.kpiRevenue)
  const kpiInventory = computed(() => bundle.value.kpiInventory)
  const kpiClients = computed(() => bundle.value.kpiClients)
  const kpiWarranty = computed(() => bundle.value.kpiWarranty)
  const repairsTimeline = computed(() => bundle.value.repairsTimeline)
  const revenueTimeline = computed(() => bundle.value.revenueTimeline)
  const kpiTurnaround = computed(() => bundle.value.kpiTurnaround)
  const kpiOverdue = computed(() => bundle.value.kpiOverdue)
  const kpiLeadConversion = computed(() => bundle.value.kpiLeadConversion)
  const kpiTopModels = computed(() => bundle.value.kpiTopModels)
  const kpiClientReturn = computed(() => bundle.value.kpiClientReturn)

  async function load() {
    isLoading.value = true
    error.value = ''

    try {
      bundle.value = await fetchStatsPageBundle()
    } catch (loadError) {
      error.value = extractErrorMessage(loadError)
    } finally {
      isLoading.value = false
    }
  }

  onMounted(load)

  return {
    isLoading,
    error,
    cards,
    summaryPanels,
    chartPanels,
    stats,
    kpiSummary,
    kpiDashboard,
    kpiRevenue,
    kpiInventory,
    kpiClients,
    kpiWarranty,
    repairsTimeline,
    revenueTimeline,
    kpiTurnaround,
    kpiOverdue,
    kpiLeadConversion,
    kpiTopModels,
    kpiClientReturn,
    load
  }
}
