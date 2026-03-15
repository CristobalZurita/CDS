<template>
  <main class="admin-page">
    <header class="admin-header">
      <div>
        <h1>Categorias</h1>
        <p>Gestion de categorias de inventario y servicios.</p>
      </div>
      <div class="header-actions">
        <button class="btn-secondary" :disabled="loading" @click="loadCategories">
          {{ loading ? 'Actualizando...' : 'Actualizar' }}
        </button>
        <button class="btn-primary" data-testid="categories-new" :disabled="loading" @click="showForm ? toggleForm() : startCreate()">
          {{ showForm ? 'Cancelar' : 'Nueva categoria' }}
        </button>
      </div>
    </header>

    <p v-if="error" class="admin-error">{{ error }}</p>

    <section v-if="showForm" class="panel-card">
      <h2>{{ hasEditingCategory ? 'Editar categoria' : 'Crear categoria' }}</h2>
      <div class="form-grid">
        <label>
          <span>Nombre</span>
          <input v-model.trim="form.name" type="text" minlength="2" maxlength="255" />
        </label>
        <label>
          <span>Descripcion</span>
          <textarea v-model.trim="form.description" rows="3" maxlength="1000"></textarea>
        </label>
      </div>
      <div class="panel-actions">
        <button class="btn-primary" :disabled="loading" @click="saveCategory">
          {{ loading ? 'Guardando...' : (hasEditingCategory ? 'Guardar cambios' : 'Crear categoria') }}
        </button>
      </div>
    </section>

    <section class="panel-card">
      <h2>Listado</h2>
      <div v-if="categories.length === 0" class="empty-state">No hay categorias registradas.</div>
      <div v-else class="table-wrap">
        <table data-testid="categories-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Nombre</th>
              <th>Descripcion</th>
              <th>Actualizado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="category in categories" :key="category.id">
              <td>{{ category.id }}</td>
              <td>{{ category.name }}</td>
              <td>{{ category.description || '—' }}</td>
              <td>{{ formatDate(category.updated_at) }}</td>
              <td>
                <div class="row-actions">
                  <button class="btn-secondary" :disabled="loading" @click="startEdit(category)">Editar</button>
                  <button class="btn-danger" :disabled="loading" @click="removeCategory(category)">Eliminar</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </main>
</template>

<script setup>
import { useCategoriesPage } from '@/composables/useCategoriesPage'

const {
  categories,
  loading,
  error,
  showForm,
  hasEditingCategory,
  form,
  formatDate,
  loadCategories,
  toggleForm,
  startCreate,
  startEdit,
  saveCategory,
  removeCategory
} = useCategoriesPage()
</script>

<style scoped src="./commonAdminPage.css"></style>
