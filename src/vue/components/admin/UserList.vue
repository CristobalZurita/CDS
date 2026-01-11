<template>
  <div>
    <h2>Usuarios</h2>
    <button @click="fetchUsers">Actualizar</button>
    <table>
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
            <button @click="editUser(user)">Editar</button>
            <button @click="deleteUser(user.id)">Borrar</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
<script setup>
import { useUsers } from '@/composables/useUsers'
const { users, fetchUsers, deleteUser } = useUsers()
function editUser(user) {
  // Implementar navegación o modal de edición
}
</script>
