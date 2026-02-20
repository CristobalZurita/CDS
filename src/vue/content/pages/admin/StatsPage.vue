<template>
	<AdminLayout title="Estadísticas" subtitle="Indicadores y métricas">
		<StatsCards :stats="stats" />
		<KpiZones
			:summary="kpiSummary"
			:dashboard="kpiDashboard"
			:revenue="kpiRevenue"
			:inventory="kpiInventory"
			:clients="kpiClients"
			:warranty="kpiWarranty"
		/>
	</AdminLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '@/services/api'
import StatsCards from '@/vue/components/admin/StatsCards.vue'
import KpiZones from '@/vue/components/admin/KpiZones.vue'
import AdminLayout from '@/vue/components/admin/layout/AdminLayout.vue'

const stats = ref({})
const kpiSummary = ref({})
const kpiDashboard = ref({})
const kpiRevenue = ref({})
const kpiInventory = ref({})
const kpiClients = ref({})
const kpiWarranty = ref({})

const safeData = (result, fallback = {}) => {
	if (result.status !== 'fulfilled') return fallback
	return result.value?.data || fallback
}

async function load() {
	const [
		statsRes,
		summaryRes,
		dashboardRes,
		revenueRes,
		inventoryRes,
		clientsRes,
		warrantyRes
	] = await Promise.allSettled([
		api.get('/stats', { params: { extended: true } }),
		api.get('/analytics/kpis/summary'),
		api.get('/analytics/dashboard'),
		api.get('/analytics/revenue'),
		api.get('/analytics/inventory'),
		api.get('/analytics/clients'),
		api.get('/analytics/warranties')
	])

	stats.value = safeData(statsRes, {})
	kpiSummary.value = safeData(summaryRes, {})
	kpiDashboard.value = safeData(dashboardRes, {})
	kpiRevenue.value = safeData(revenueRes, {})
	kpiInventory.value = safeData(inventoryRes, {})
	kpiClients.value = safeData(clientsRes, {})
	kpiWarranty.value = safeData(warrantyRes, {})
}

onMounted(load)
</script>

<style scoped lang="scss">
</style>
