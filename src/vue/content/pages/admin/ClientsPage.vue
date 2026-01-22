
<template>
	<AdminLayout title="Clientes" subtitle="Gestión de clientes y perfil">
		<div class="d-flex justify-content-between align-items-center mb-3">
			<h1 class="h4">Clientes</h1>
			<div>
				<button class="btn btn-sm btn-success me-2" @click="showForm = !showForm">
					{{ showForm ? 'Cancelar' : 'Nuevo Cliente' }}
				</button>
				<button class="btn btn-sm btn-primary me-2" @click="showIntake = !showIntake">
					{{ showIntake ? 'Cerrar ingreso' : 'Ingreso completo' }}
				</button>
				<button class="btn btn-sm btn-outline-secondary" @click="load">Actualizar</button>
			</div>
		</div>

		<div v-if="showIntake" class="mb-3">
			<IntakeForm @completed="onIntakeCompleted" />
		</div>

		<div v-if="showForm" class="card p-3 mb-3">
			<h5 class="mb-3">Crear cliente</h5>
			<div class="row g-2">
				<div class="col-md-6">
					<label class="form-label">Nombre</label>
					<input v-model="newClient.name" class="form-control" />
				</div>
				<div class="col-md-6">
					<label class="form-label">Email</label>
					<input v-model="newClient.email" type="email" class="form-control" />
				</div>
				<div class="col-md-6">
					<label class="form-label">Teléfono</label>
					<input v-model="newClient.phone" class="form-control" />
				</div>
				<div class="col-md-6">
					<label class="form-label">Dirección</label>
					<input v-model="newClient.address" class="form-control" />
				</div>
				<div class="col-12">
					<label class="form-label">Notas</label>
					<textarea v-model="newClient.notes" class="form-control" rows="2"></textarea>
				</div>
			</div>
			<div class="mt-3 d-flex gap-2 justify-content-end">
				<button class="btn btn-secondary btn-sm" @click="resetForm">Limpiar</button>
				<button class="btn btn-primary btn-sm" :disabled="saving" @click="createClient">
					{{ saving ? 'Guardando...' : 'Guardar' }}
				</button>
			</div>
		</div>

		<div class="clients-page">
			<div class="clients-grid">
				<ClientList :clients="clients" @select="onSelect" />
				<ClientDetail :client="selected || {}" />
			</div>
		</div>
	</AdminLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '@/services/api'
import ClientList from '@/vue/components/admin/ClientList.vue'
import ClientDetail from '@/vue/components/admin/ClientDetail.vue'
import IntakeForm from '@/vue/components/admin/IntakeForm.vue'
import AdminLayout from '@/vue/components/admin/layout/AdminLayout.vue'

const clients = ref([])
const selected = ref(null)
const showForm = ref(false)
const showIntake = ref(false)
const saving = ref(false)
const newClient = ref({
	name: '',
	email: '',
	phone: '',
	address: '',
	notes: ''
})

async function load() {
	try {
		const res = await api.get('/clients')
		clients.value = res.data
		selected.value = clients.value[0] || null
	} catch (e) {
		clients.value = []
	}
}

function resetForm() {
	newClient.value = { name: '', email: '', phone: '', address: '', notes: '' }
}

async function createClient() {
	if (!newClient.value.name || !newClient.value.email) {
		alert('Nombre y email son obligatorios')
		return
	}
	saving.value = true
	try {
		await api.post('/clients', newClient.value)
		await load()
		resetForm()
		showForm.value = false
	} catch (e) {
		console.error(e)
		alert('Error creando cliente')
	} finally {
		saving.value = false
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
