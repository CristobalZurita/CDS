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
@use "@/scss/_core.scss" as *;

.admin-page {
  display: flex;
  flex-direction: column;
  gap: var(--spacer-md);
}

.admin-page__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacer-md);
  flex-wrap: wrap;
}

.admin-page__title,
.admin-page__panel-title {
  margin: 0;
  color: var(--color-dark);
  font-weight: 700;
}

.admin-page__title {
  font-size: var(--text-xl);
}

.admin-page__panel-title {
  font-size: var(--text-lg);
  margin-bottom: var(--spacer-md);
}

.admin-page__actions {
  display: flex;
  gap: var(--spacer-sm);
  flex-wrap: wrap;
}

.admin-page__panel,
.admin-page__content {
  padding: var(--spacer-md);
  background: var(--color-white);
  border: 1px solid var(--color-light);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
}

.admin-page__button {
  min-height: 40px;
  padding: 0.65rem 0.9rem;
  border: 0;
  border-radius: var(--radius-sm);
  color: var(--color-white);
  font-size: var(--text-sm);
  font-weight: 700;
  cursor: pointer;
  transition: var(--transition-base);
}

.admin-page__button:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.admin-page__button--success {
  background: var(--color-primary);
}

@include media-breakpoint-down(md) {
  .admin-page__header,
  .admin-page__actions {
    flex-direction: column;
    align-items: stretch;
  }

  .admin-page__button {
    width: 100%;
  }
}
</style>
