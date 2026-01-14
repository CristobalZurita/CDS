<template>
  <div>
    <h2>Categorías</h2>
    <button @click="fetchCategories">Actualizar</button>
    <table>
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
            <button @click="editCategory(cat)">Editar</button>
            <button @click="deleteCategory(cat.id)">Borrar</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
<script setup>
import { useCategories } from '@/composables/useCategories'
const { categories, fetchCategories, deleteCategory } = useCategories()
function editCategory(cat) {
  // Implementar edición
}
</script>
