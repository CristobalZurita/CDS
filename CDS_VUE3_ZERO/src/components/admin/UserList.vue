<template>
  <div class="users-list">
    <div class="list-toolbar">
      <span class="list-count">{{ users.length }} usuarios</span>
      <button class="btn-refresh" @click="fetchUsers">↻ Actualizar</button>
    </div>
    
    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>Email</th>
            <th>Nombre</th>
            <th>Rol</th>
            <th class="actions">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>{{ user.email }}</td>
            <td>{{ user.full_name || user.firstName + ' ' + user.lastName }}</td>
            <td>
              <span :class="['role-pill', user.role]">
                {{ formatRole(user.role) }}
              </span>
            </td>
            <td class="actions">
              <button class="btn-icon" @click="editUser(user)" title="Editar">✏️</button>
              <button class="btn-icon danger" @click="removeUser(user)" title="Eliminar">🗑️</button>
            </td>
          </tr>
          <tr v-if="!users?.length">
            <td colspan="4" class="empty-cell">No hay usuarios registrados</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useUsers } from '@/composables/useUsers'

const { users, fetchUsers, deleteUser } = useUsers()
const emit = defineEmits(['edit'])

const formatRole = (role) => {
  const map = {
    'admin': 'Admin',
    'technician': 'Técnico',
    'client': 'Cliente'
  }
  return map[role] || role
}

const editUser = (user) => {
  emit('edit', user)
}

const removeUser = async (user) => {
  if (!confirm(`¿Eliminar usuario "${user.email}"?`)) return
  await deleteUser(user.id)
}

onMounted(fetchUsers)
</script>

<style scoped>
/* 35% larger */
.users-list {
  width: 100%;
}

.list-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.35rem;
}

.list-count {
  font-size: 1.2rem;
  color: #6b7280;
}

.btn-refresh {
  padding: 0.7rem 1.35rem;
  background: #f8fafc;
  border: 1px solid #e8ecf1;
  border-radius: 11px;
  cursor: pointer;
  font-size: 1.2rem;
  color: #374151;
}

.btn-refresh:hover {
  background: #e8ecf1;
}

.table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 1.4rem;
}

.data-table th {
  text-align: left;
  padding: 1rem;
  font-weight: 600;
  color: #6b7280;
  border-bottom: 1px solid #e8ecf1;
  font-size: 1.15rem;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.data-table td {
  padding: 1.2rem 1rem;
  border-bottom: 1px solid #f3f4f6;
  color: #374151;
}

.data-table tr:hover td {
  background: #f8fafc;
}

.role-pill {
  display: inline-block;
  padding: 0.4rem 1rem;
  border-radius: 999px;
  font-size: 1.1rem;
  font-weight: 600;
  text-transform: uppercase;
}

.role-pill.admin {
  background: #ffedd5;
  color: #9a3412;
}

.role-pill.technician {
  background: #dbeafe;
  color: #1e40af;
}

.role-pill.client {
  background: #f3f4f6;
  color: #374151;
}

.actions {
  text-align: right;
}

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
  font-size: 1.35rem;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.btn-icon:hover {
  opacity: 1;
}

.btn-icon.danger:hover {
  color: #dc2626;
}

.empty-cell {
  text-align: center;
  color: #6b7280;
  padding: 2.7rem;
}
</style>
