<template>
	<div>
		<AdminToolbar title="Admin - Dashboard" subtitle="Panel de control administrativo" />
		<StatsCards :stats="stats" />
		<section>
			<h3>Últimas reparaciones</h3>
			<RepairsList />
		</section>
		<section>
			<h3>Usuarios</h3>
			<UserList />
		</section>
	</div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '@/services/api'
import RepairsList from '@/vue/components/admin/RepairsList.vue'
import UserList from '@/vue/components/admin/UserList.vue'
import StatsCards from '@/vue/components/admin/StatsCards.vue'
import AdminToolbar from '@/vue/components/admin/AdminToolbar.vue'

const stats = ref({})

async function loadStats() {
	try {
		const res = await api.get('/stats')
		stats.value = res.data
	} catch (e) {
		stats.value = {}
	}
}

onMounted(loadStats)
</script>

<style scoped>
</style>
