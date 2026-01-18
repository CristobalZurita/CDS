<template>
  <section class="admin-section">
    <div class="admin-section-header">
      <h2 class="admin-section-title">Usuarios</h2>
      <button class="admin-btn admin-btn-outline" @click="fetchUsers">Actualizar</button>
    </div>
    <table class="admin-table">
      <thead>
        <tr>
          <th>Email</th>
          <th>Nombre</th>
          <th>Rol</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in users" :key="user.id">
          <td>{{ user.email }}</td>
          <td>{{ user.full_name }}</td>
          <td>{{ user.role }}</td>
          <td>
            <button class="admin-btn admin-btn-outline" @click="editUser(user)">Editar</button>
            <button class="admin-btn admin-btn-primary" @click="deleteUser(user.id)">Borrar</button>
          </td>
        </tr>
      </tbody>
    </table>
  </section>
</template>
<script setup>
import { useUsers } from '@/composables/useUsers'
import { onMounted } from 'vue'
const { users, fetchUsers, deleteUser } = useUsers()
function editUser(user) {
  // Implementar navegación o modal de edición
}

onMounted(() => {
  fetchUsers()
})
</script>
