<template>
	<div>
		<AdminToolbar title="Reparaciones" subtitle="Flujo y estados del taller" />
		<RepairsList />
	</div>
</template>

<script setup>
import RepairsList from '@/vue/components/admin/RepairsList.vue'
import AdminToolbar from '@/vue/components/admin/AdminToolbar.vue'
</script>

<style scoped>
</style>
