<template>
  <section class="admin-section">
    <div class="admin-section-header">
      <h2 class="admin-section-title">Usuarios</h2>
      <button class="admin-btn admin-btn-outline" data-testid="users-refresh" @click="fetchUsers">Actualizar</button>
    </div>
    <table class="admin-table admin-table--stack">
      <thead>
        <tr>
          <th>Email</th>
          <th>Nombre</th>
          <th>Rol</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in users" :key="user.id" data-testid="user-row">
          <td data-label="Email">{{ user.email }}</td>
          <td data-label="Nombre">{{ user.full_name }}</td>
          <td data-label="Rol">{{ user.role }}</td>
          <td data-label="Acciones">
            <button class="admin-btn admin-btn-outline" data-testid="user-edit" @click="editUser(user)">Editar</button>
            <button class="admin-btn admin-btn-primary" data-testid="user-delete" @click="removeUser(user)">Borrar</button>
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
const emit = defineEmits(['edit'])

function editUser(user) {
  emit('edit', user)
}

async function removeUser(user) {
  if (!window.confirm(`Eliminar usuario "${user.email}"?`)) return
  await deleteUser(user.id)
}

onMounted(() => {
  fetchUsers()
})
</script>
