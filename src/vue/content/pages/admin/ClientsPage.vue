
<template>
	<div class="clients-page">
		<AdminToolbar title="Clientes" subtitle="Gestión de clientes y perfil" />
		<div class="clients-grid">
			<ClientList :clients="clients" @select="onSelect" />
			<ClientDetail :client="selected || {}" />
		</div>
	</div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '@/services/api'
import ClientList from '@/vue/components/admin/ClientList.vue'
import ClientDetail from '@/vue/components/admin/ClientDetail.vue'
import AdminToolbar from '@/vue/components/admin/AdminToolbar.vue'

const clients = ref([])
const selected = ref(null)

async function load() {
	try {
		const res = await api.get('/clients')
		clients.value = res.data
		selected.value = clients.value[0] || null
	} catch (e) {
		clients.value = []
	}
}

function onSelect(client) {
	selected.value = client
}

onMounted(load)
</script>

<style scoped>
.clients-page {
	padding: 1rem;
}
.clients-grid {
	display: grid;
	grid-template-columns: 1fr 1fr;
	gap: 1rem;
}
</style>
