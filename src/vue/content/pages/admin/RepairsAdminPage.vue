<template>
	<AdminLayout title="Reparaciones" subtitle="Flujo y estados del taller">
		<div class="d-flex justify-content-between align-items-center mb-3">
			<h1 class="h4">Reparaciones</h1>
			<div>
				<button class="btn btn-sm btn-success me-2" @click="showForm = !showForm">
					{{ showForm ? 'Cancelar' : 'Nueva Reparación' }}
				</button>
			</div>
		</div>

		<div v-if="showForm" class="card p-3 mb-3">
			<h5 class="mb-3">Crear reparación</h5>
			<RepairForm @saved="onSaved" />
		</div>

		<RepairsList :key="refreshKey" />
	</AdminLayout>
</template>

<script setup>
import { ref } from 'vue'
import RepairsList from '@/vue/components/admin/RepairsList.vue'
import RepairForm from '@/vue/components/admin/RepairForm.vue'
import AdminLayout from '@/vue/components/admin/layout/AdminLayout.vue'

const showForm = ref(false)
const refreshKey = ref(0)

function onSaved() {
	showForm.value = false
	refreshKey.value += 1
}
</script>

<style scoped>
</style>
