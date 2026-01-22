<template>
  <section class="admin-section">
    <div class="admin-section-header">
      <h2 class="admin-section-title">Categorías</h2>
      <button class="admin-btn admin-btn-outline" @click="fetchCategories">Actualizar</button>
    </div>
    <table class="admin-table">
      <thead>
        <tr>
          <th>Nombre</th>
          <th>Descripción</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="cat in categories" :key="cat.id">
          <td>{{ cat.name }}</td>
          <td>{{ cat.description }}</td>
          <td>
            <button class="admin-btn admin-btn-outline" @click="editCategory(cat)">Editar</button>
            <button class="admin-btn admin-btn-primary" @click="deleteCategory(cat.id)">Borrar</button>
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
function editCategory(cat) {
  // Implementar edición
}

onMounted(() => {
  fetchCategories()
})
</script>
