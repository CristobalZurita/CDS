<template>
	<AdminLayout title="Admin - Dashboard" subtitle="Panel de control administrativo">
		<StatsCards :stats="stats" />
		<KpiZones
			:summary="kpiSummary"
			:dashboard="kpiDashboard"
			:revenue="kpiRevenue"
			:inventory="kpiInventory"
			:clients="kpiClients"
			:warranty="kpiWarranty"
		/>
		<section>
			<h3>Últimas reparaciones</h3>
			<RepairsList />
		</section>
		<section>
			<div class="d-flex justify-content-between align-items-center mb-2">
				<h3 class="mb-0">Usuarios</h3>
				<button class="btn btn-sm btn-success" data-testid="users-new" @click="toggleUserForm">
					{{ showUserForm ? 'Cancelar' : 'Nuevo Usuario' }}
				</button>
			</div>
			<div v-if="showUserForm" class="card p-3 mb-3">
				<h5 class="mb-3">{{ selectedUser ? 'Editar usuario' : 'Crear usuario' }}</h5>
				<UserForm :user="selectedUser" @saved="onUserSaved" />
			</div>
			<UserList :key="userRefreshKey" @edit="onEditUser" />
		</section>
	</AdminLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '@/services/api'
import RepairsList from '@/vue/components/admin/RepairsList.vue'
import UserList from '@/vue/components/admin/UserList.vue'
import StatsCards from '@/vue/components/admin/StatsCards.vue'
import KpiZones from '@/vue/components/admin/KpiZones.vue'
import AdminLayout from '@/vue/components/admin/layout/AdminLayout.vue'
import UserForm from '@/vue/components/admin/UserForm.vue'

const stats = ref({})
const kpiSummary = ref({})
const kpiDashboard = ref({})
const kpiRevenue = ref({})
const kpiInventory = ref({})
const kpiClients = ref({})
const kpiWarranty = ref({})
const showUserForm = ref(false)
const selectedUser = ref(null)
const userRefreshKey = ref(0)

const safeData = (result, fallback = {}) => {
	if (result.status !== 'fulfilled') return fallback
	return result.value?.data || fallback
}

async function loadStats() {
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

onMounted(loadStats)

function onUserSaved() {
	showUserForm.value = false
	selectedUser.value = null
	userRefreshKey.value += 1
}

function toggleUserForm() {
	if (showUserForm.value) {
		showUserForm.value = false
		selectedUser.value = null
		return
	}
	selectedUser.value = null
	showUserForm.value = true
}

function onEditUser(user) {
	selectedUser.value = user
	showUserForm.value = true
}
</script>

<style scoped lang="scss">
</style>
