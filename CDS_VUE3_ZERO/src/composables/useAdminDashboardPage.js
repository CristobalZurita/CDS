/**
 * useAdminDashboardPage
 * 
 * Dashboard administrativo completo.
 * Basado en LEGACY - trae StatsCards, KPIs, RepairsList, UserList.
 */

import { ref, onMounted, computed } from 'vue'
import api, { extractErrorMessage } from '@/services/api'

export function useAdminDashboardPage() {
  const isLoading = ref(false)
  const error = ref('')
  
  // Datos de stats (contadores simples)
  const stats = ref({})
  
  // KPIs detallados
  const kpiSummary = ref({})
  const kpiDashboard = ref({})
  const kpiRevenue = ref({})
  const kpiInventory = ref({})
  const kpiClients = ref({})
  const kpiWarranty = ref({})
  
  // Lista de reparaciones recientes
  const recentRepairs = ref([])
  
  // Cards del dashboard
  const cards = computed(() => [
    { id: 'users', label: 'Usuarios', value: stats.value.users || 0 },
    { id: 'clients', label: 'Clientes', value: stats.value.clients || 0 },
    { id: 'repairs', label: 'Reparaciones', value: stats.value.repairs || 0 }
  ])
  
  // Helper para obtener datos seguros
  const safeData = (result, fallback = {}) => {
    if (result.status !== 'fulfilled') return fallback
    return result.value?.data || fallback
  }
  
  async function loadDashboard() {
    isLoading.value = true
    error.value = ''
    
    try {
      // Llamadas paralelas a todos los endpoints de analytics
      const [
        statsRes,
        summaryRes,
        dashboardRes,
        revenueRes,
        inventoryRes,
        clientsRes,
        warrantyRes,
        repairsRes
      ] = await Promise.allSettled([
        api.get('/analytics/dashboard'),
        api.get('/analytics/kpis/summary'),
        api.get('/analytics/dashboard'),
        api.get('/analytics/revenue'),
        api.get('/analytics/inventory'),
        api.get('/analytics/clients'),
        api.get('/analytics/warranties'),
        api.get('/repairs/', { params: { limit: 10, sort: '-created_at' } })
      ])
      
      stats.value = safeData(statsRes, {})
      kpiSummary.value = safeData(summaryRes, {})
      kpiDashboard.value = safeData(dashboardRes, {})
      kpiRevenue.value = safeData(revenueRes, {})
      kpiInventory.value = safeData(inventoryRes, {})
      kpiClients.value = safeData(clientsRes, {})
      kpiWarranty.value = safeData(warrantyRes, {})
      
      // Reparaciones recientes
      const repairsData = safeData(repairsRes, [])
      recentRepairs.value = Array.isArray(repairsData) ? repairsData : (repairsData.data || [])
      
    } catch (err) {
      error.value = extractErrorMessage(err)
    } finally {
      isLoading.value = false
    }
  }
  
  // Formateo de moneda
  function formatCurrency(value) {
    const amount = Number(value || 0)
    return new Intl.NumberFormat('es-CL', {
      style: 'currency',
      currency: 'CLP',
      minimumFractionDigits: 0
    }).format(amount)
  }
  
  // Formateo de fecha
  function formatDate(value) {
    if (!value) return '—'
    const date = new Date(value)
    if (Number.isNaN(date.getTime())) return '—'
    return new Intl.DateTimeFormat('es-CL', { 
      dateStyle: 'medium',
      timeStyle: 'short'
    }).format(date)
  }
  
  onMounted(loadDashboard)
  
  return {
    isLoading,
    error,
    cards,
    stats,
    kpiSummary,
    kpiDashboard,
    kpiRevenue,
    kpiInventory,
    kpiClients,
    kpiWarranty,
    recentRepairs,
    loadDashboard,
    formatCurrency,
    formatDate
  }
}

export default useAdminDashboardPage
