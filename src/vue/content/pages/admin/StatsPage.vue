<template>
	<div>
		<h1>Estadísticas</h1>
		<StatsCards :stats="stats" />
	</div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '@/services/api'
import StatsCards from '@/vue/components/admin/StatsCards.vue'

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

<style scoped>
</style>
