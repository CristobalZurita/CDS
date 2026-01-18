<template>
	<AdminLayout title="Reparaciones" subtitle="Flujo y estados del taller">
		<RepairsList />
	</AdminLayout>
</template>

<script setup>
import RepairsList from '@/vue/components/admin/RepairsList.vue'
import AdminLayout from '@/vue/components/admin/layout/AdminLayout.vue'
</script>

<style scoped>
</style>
