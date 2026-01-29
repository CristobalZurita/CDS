<template>
	<AdminLayout title="Categorías" subtitle="Servicios y clasificaciones">
		<div class="d-flex justify-content-between align-items-center mb-3">
			<h1 class="h4">Categorías</h1>
			<div>
				<button class="btn btn-sm btn-success me-2" @click="showForm = !showForm">
					{{ showForm ? 'Cancelar' : 'Nueva Categoría' }}
				</button>
			</div>
		</div>

		<div v-if="showForm" class="card p-3 mb-3">
			<h5 class="mb-3">Crear categoría</h5>
			<CategoryForm @saved="onSaved" />
		</div>

		<CategoryList :key="refreshKey" />
	</AdminLayout>
</template>

<script setup>
import { ref } from 'vue'
import CategoryList from '@/vue/components/admin/CategoryList.vue'
import CategoryForm from '@/vue/components/admin/CategoryForm.vue'
import AdminLayout from '@/vue/components/admin/layout/AdminLayout.vue'

const showForm = ref(false)
const refreshKey = ref(0)

function onSaved() {
	showForm.value = false
	refreshKey.value += 1
}
</script>

<style scoped lang="scss">
</style>
