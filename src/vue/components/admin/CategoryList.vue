<template>
  <section class="admin-section">
    <div class="admin-section-header">
      <h2 class="admin-section-title">Categorías</h2>
      <button class="admin-btn admin-btn-outline" data-testid="categories-refresh" @click="fetchCategories">Actualizar</button>
    </div>
    <table class="admin-table admin-table--stack">
      <thead>
        <tr>
          <th>Nombre</th>
          <th>Descripción</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="cat in categories" :key="cat.id" data-testid="category-row">
          <td data-label="Nombre">{{ cat.name }}</td>
          <td data-label="Descripción">{{ cat.description }}</td>
          <td data-label="Acciones">
            <button class="admin-btn admin-btn-outline" data-testid="category-edit" @click="editCategory(cat)">Editar</button>
            <button class="admin-btn admin-btn-primary" data-testid="category-delete" @click="removeCategory(cat)">Borrar</button>
          </td>
        </tr>
      </tbody>
    </table>
  </section>
</template>
<script setup>
import { useCategories } from '@/composables/useCategories'
import { onMounted } from 'vue'
const { categories, fetchCategories, deleteCategory } = useCategories()
const emit = defineEmits(['edit'])
function editCategory(cat) {
  emit('edit', cat)
}

async function removeCategory(cat) {
  if (!window.confirm(`Eliminar categoría "${cat.name}"?`)) return
  await deleteCategory(cat.id)
}

onMounted(() => {
  fetchCategories()
})
</script>
<style scoped lang="scss">
@use "@/scss/_theming.scss" as *;

@include media-breakpoint-down(md) {
  .admin-table--stack,
  .admin-table--stack thead,
  .admin-table--stack tbody,
  .admin-table--stack tr,
  .admin-table--stack th,
  .admin-table--stack td {
    display: block;
    width: 100%;
  }

  .admin-table--stack thead {
    display: none;
  }

  .admin-table--stack tr {
    padding: 1rem;
    margin-bottom: 0.75rem;
    background: $color-white;
    border-radius: 12px;
    box-shadow: 0 8px 16px rgba($color-dark, 0.12);
  }

  .admin-table--stack td {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
    padding: 0.35rem 0;
    font-size: 1rem;
  }

  .admin-table--stack td::before {
    content: attr(data-label);
    font-weight: 600;
    color: $text-muted;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    font-size: 0.8rem;
  }
}
</style>
