<template>
	<div>
		<h1>Admin - Dashboard</h1>
		<DashboardPanel />
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
import DashboardPanel from '@/vue/components/dashboard/DashboardPanel.vue'
import RepairsList from '@/vue/components/admin/RepairsList.vue'
import UserList from '@/vue/components/admin/UserList.vue'
</script>

<style scoped>
h1 { margin-bottom: 12px; }
</style>
