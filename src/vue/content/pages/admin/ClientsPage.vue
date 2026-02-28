
<template>
	<AdminLayout title="Clientes" subtitle="Gestión de clientes y perfil" :context="contextHeader">
		<div class="d-flex justify-content-between align-items-center mb-3">
			<h1 class="h4">Clientes</h1>
			<div>
				<button class="btn btn-sm btn-primary me-2" data-testid="clients-intake-toggle" @click="showIntake = !showIntake">
					{{ showIntake ? 'Cerrar ingreso' : 'Ingreso completo' }}
				</button>
				<button class="btn btn-sm btn-outline-secondary" data-testid="clients-refresh" @click="load">Actualizar</button>
			</div>
		</div>

		<div v-if="showIntake" class="mb-3" data-testid="clients-intake">
			<UnifiedIntakeForm @completed="onIntakeCompleted" />
		</div>

		<div class="clients-page">
			<div class="clients-toolbar mb-3">
				<input
					v-model="searchQuery"
					type="search"
					class="form-control"
					data-testid="clients-search"
					placeholder="Buscar por nombre, email, código o teléfono..."
				/>
			</div>
			<div class="clients-grid">
				<ClientList :clients="filteredClients" @select="onSelect" />
				<ClientDetail :client="selected || {}" />
			</div>
		</div>
	</AdminLayout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '@/services/api'
import ClientList from '@/vue/components/admin/ClientList.vue'
import ClientDetail from '@/vue/components/admin/ClientDetail.vue'
import UnifiedIntakeForm from '@/vue/components/admin/UnifiedIntakeForm.vue'
import AdminLayout from '@/vue/components/admin/layout/AdminLayout.vue'

const clients = ref([])
const selected = ref(null)
const showIntake = ref(true)
const searchQuery = ref('')
const route = useRoute()
const contextHeader = computed(() => {
	if (!selected.value) return null
	return {
		clientName: selected.value.name,
		clientCode: selected.value.client_code,
		instrument: '—'
	}
})

const filteredClients = computed(() => {
	const q = searchQuery.value.trim().toLowerCase()
	if (!q) return clients.value
	return clients.value.filter((client) => {
		const haystack = [
			client.name,
			client.email,
			client.phone,
			client.client_code
		].filter(Boolean).join(' ').toLowerCase()
		return haystack.includes(q)
	})
})

async function load() {
	try {
		const res = await api.get('/clients')
		clients.value = res.data
		if (route.query.client_id) {
			const found = clients.value.find(c => String(c.id) === String(route.query.client_id))
			selected.value = found || clients.value[0] || null
		} else {
			selected.value = clients.value[0] || null
		}
	} catch (e) {
		clients.value = []
	}
}

function onSelect(client) {
	selected.value = client
}

function onIntakeCompleted(payload) {
	showIntake.value = false
	load()
	if (payload?.client_id) {
		const found = clients.value.find(c => String(c.id) === String(payload.client_id))
		if (found) selected.value = found
	}
}

onMounted(load)
</script>

<style scoped lang="scss">
@import '@/scss/_core.scss';

.clients-page {
	padding: 1rem;
}
.clients-grid {
	display: grid;
	grid-template-columns: 1fr 1fr;
	gap: 1rem;
}
.clients-toolbar {
	max-width: 420px;
}
</style>
