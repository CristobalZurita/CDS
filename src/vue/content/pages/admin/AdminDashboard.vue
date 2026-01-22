<template>
	<AdminLayout title="Admin - Dashboard" subtitle="Panel de control administrativo">
		<StatsCards :stats="stats" />
		<section>
			<h3>Últimas reparaciones</h3>
			<RepairsList />
		</section>
		<section>
			<div class="d-flex justify-content-between align-items-center mb-2">
				<h3 class="mb-0">Usuarios</h3>
				<button class="btn btn-sm btn-success" @click="showUserForm = !showUserForm">
					{{ showUserForm ? 'Cancelar' : 'Nuevo Usuario' }}
				</button>
			</div>
			<div v-if="showUserForm" class="card p-3 mb-3">
				<UserForm @saved="onUserSaved" />
			</div>
			<UserList :key="userRefreshKey" />
		</section>
	</AdminLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '@/services/api'
import RepairsList from '@/vue/components/admin/RepairsList.vue'
import UserList from '@/vue/components/admin/UserList.vue'
import StatsCards from '@/vue/components/admin/StatsCards.vue'
import AdminLayout from '@/vue/components/admin/layout/AdminLayout.vue'
import UserForm from '@/vue/components/admin/UserForm.vue'

const stats = ref({})
const showUserForm = ref(false)
const userRefreshKey = ref(0)

async function loadStats() {
	try {
		const res = await api.get('/stats')
		stats.value = res.data
	} catch (e) {
		stats.value = {}
	}
}

onMounted(loadStats)

function onUserSaved() {
	showUserForm.value = false
	userRefreshKey.value += 1
}
</script>

<style scoped>
</style>
