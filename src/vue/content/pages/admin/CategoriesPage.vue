<template>
	<AdminLayout title="Categorías" subtitle="Servicios y clasificaciones">
		<div class="d-flex justify-content-between align-items-center mb-3">
			<h1 class="h4">Categorías</h1>
			<div>
				<button class="btn btn-sm btn-success me-2" data-testid="categories-new" @click="toggleForm">
					{{ showForm ? 'Cancelar' : 'Nueva Categoría' }}
				</button>
			</div>
		</div>

		<div v-if="showForm" class="card p-3 mb-3">
			<h5 class="mb-3">{{ selectedCategory ? 'Editar categoría' : 'Crear categoría' }}</h5>
			<CategoryForm :category="selectedCategory" @saved="onSaved" />
		</div>

		<CategoryList :key="refreshKey" @edit="onEdit" />
	</AdminLayout>
</template>

<script setup>
import { ref } from 'vue'
import CategoryList from '@/vue/components/admin/CategoryList.vue'
import CategoryForm from '@/vue/components/admin/CategoryForm.vue'
import AdminLayout from '@/vue/components/admin/layout/AdminLayout.vue'

const showForm = ref(false)
const selectedCategory = ref(null)
const refreshKey = ref(0)

function onSaved() {
	showForm.value = false
	selectedCategory.value = null
	refreshKey.value += 1
}

function toggleForm() {
	if (showForm.value) {
		showForm.value = false
		selectedCategory.value = null
		return
	}
	selectedCategory.value = null
	showForm.value = true
}

function onEdit(category) {
	selectedCategory.value = category
	showForm.value = true
}
</script>
