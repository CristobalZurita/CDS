<template>
  <AdminLayout title="Categorías" subtitle="Servicios y clasificaciones">
    <section class="admin-page">
      <header class="admin-page__header">
        <h1 class="admin-page__title">Categorías</h1>
        <div class="admin-page__actions">
          <button
            type="button"
            class="admin-page__button admin-page__button--success"
            data-testid="categories-new"
            @click="toggleForm"
          >
            {{ showForm ? 'Cancelar' : 'Nueva Categoría' }}
          </button>
        </div>
      </header>

      <section v-if="showForm" class="admin-page__panel">
        <h2 class="admin-page__panel-title">{{ selectedCategory ? 'Editar categoría' : 'Crear categoría' }}</h2>
        <CategoryForm :category="selectedCategory" @saved="onSaved" />
      </section>

      <section class="admin-page__content">
        <CategoryList :key="refreshKey" @edit="onEdit" />
      </section>
    </section>
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

<style scoped lang="scss">
.admin-page__panel-title {
  margin: 0;
  color: var(--color-dark);
  font-weight: 700;
  font-size: var(--text-lg);
  margin-bottom: var(--spacer-md);
}
</style>
