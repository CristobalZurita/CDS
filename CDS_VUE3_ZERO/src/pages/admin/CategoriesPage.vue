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
import { useCategoriesPage } from '@new/composables/useCategoriesPage'

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

<style scoped>
.admin-page { padding: 1rem; display: grid; gap: 1rem; }
.admin-header, .panel-card { border: 1px solid color-mix(in srgb, var(--cds-light) 70%, white); border-radius: .9rem; background: var(--cds-white); }
.admin-header { padding: .9rem; display: flex; flex-wrap: wrap; gap: .75rem; justify-content: space-between; align-items: center; }
.admin-header h1 { margin: 0; font-size: var(--cds-text-3xl); }
.admin-header p { margin: .3rem 0 0; color: var(--cds-text-muted); }
.header-actions { display: flex; flex-wrap: wrap; gap: .5rem; }
.btn-primary, .btn-secondary, .btn-danger { min-height: 44px; padding: .65rem .9rem; border-radius: .55rem; font-size: var(--cds-text-base); border: 1px solid transparent; }
.btn-primary { border-color: var(--cds-primary); background: var(--cds-primary); color: var(--cds-white); }
.btn-secondary { border-color: color-mix(in srgb, var(--cds-light) 65%, white); background: var(--cds-white); color: var(--cds-text-normal); }
.btn-danger { border-color: #dc2626; background: #dc2626; color: #fff; }
.admin-error { margin: 0; border: 1px solid #f4c7c3; background: #fef3f2; color: #b42318; border-radius: .6rem; padding: .75rem; }
.panel-card { padding: .9rem; display: grid; gap: .6rem; }
.panel-card h2 { margin: 0; font-size: var(--cds-text-xl); }
.form-grid { display: grid; gap: .6rem; }
.form-grid label { display: grid; gap: .35rem; }
.form-grid span { font-size: var(--cds-text-sm); color: var(--cds-text-muted); }
.form-grid input, .form-grid textarea { min-height: 44px; border-radius: .55rem; border: 1px solid color-mix(in srgb, var(--cds-light) 65%, white); padding: .65rem .75rem; font-size: var(--cds-text-base); }
.form-grid textarea { min-height: 92px; resize: vertical; }
.panel-actions { display: flex; justify-content: flex-end; }
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
th, td { text-align: left; padding: .6rem; border-bottom: 1px solid color-mix(in srgb, var(--cds-light) 70%, white); vertical-align: top; }
th { font-size: var(--cds-text-sm); color: var(--cds-text-muted); }
.row-actions { display: flex; flex-wrap: wrap; gap: .45rem; }
.empty-state { border: 1px dashed color-mix(in srgb, var(--cds-light) 70%, white); border-radius: .7rem; padding: .8rem; }
</style>
