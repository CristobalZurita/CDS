<template>
	<AdminLayout title="Estadísticas" subtitle="Indicadores y métricas">
		<StatsCards :stats="stats" />
	</AdminLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '@/services/api'
import StatsCards from '@/vue/components/admin/StatsCards.vue'
import AdminLayout from '@/vue/components/admin/layout/AdminLayout.vue'

const stats = ref({})

async function load() {
	try {
		const res = await api.get('/stats')
		stats.value = res.data
	} catch (e) {
		stats.value = {}
	}
}

onMounted(load)
</script>

<style scoped lang="scss">
</style>
