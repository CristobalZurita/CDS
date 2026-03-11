<template>
  <section class="admin-section">
    <div class="section-header">
      <h2 class="section-title">👤 Usuarios</h2>
      <button class="btn-refresh" @click="fetchUsers">Actualizar</button>
    </div>
    <div class="table-wrap">
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
          <tr v-for="user in users" :key="user.id" data-testid="user-row">
            <td data-label="Email">{{ user.email }}</td>
            <td data-label="Nombre">{{ user.full_name || user.firstName + ' ' + user.lastName }}</td>
            <td data-label="Rol">
              <span :class="['role-badge', `role-${user.role}`]">
                {{ formatRole(user.role) }}
              </span>
            </td>
            <td data-label="Acciones">
              <button class="btn-action" @click="editUser(user)">Editar</button>
              <button class="btn-action danger" @click="removeUser(user)">Borrar</button>
            </td>
          </tr>
          <tr v-if="!users?.length">
            <td colspan="4" class="empty-row">No hay usuarios registrados</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<script setup>
import { onMounted } from 'vue'
import { useUsers } from '@/composables/useUsers'

const { users, fetchUsers, deleteUser } = useUsers()
const emit = defineEmits(['edit'])

const formatRole = (role) => {
  const roleMap = {
    'admin': 'Administrador',
    'technician': 'Técnico',
    'client': 'Cliente'
  }
  return roleMap[role] || role
}

const editUser = (user) => {
  emit('edit', user)
}

const removeUser = async (user) => {
  if (!window.confirm(`¿Eliminar usuario "${user.email}"?`)) return
  await deleteUser(user.id)
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.admin-section {
  background: var(--color-white, #fff);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.section-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-dark, #1a1a2e);
}

.btn-refresh {
  padding: 0.5rem 1rem;
  background: var(--color-primary, #ff6b35);
  color: var(--color-white, #fff);
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.btn-refresh:hover {
  opacity: 0.9;
}

.table-wrap {
  overflow-x: auto;
}

.admin-table {
  width: 100%;
  border-collapse: collapse;
}

.admin-table th,
.admin-table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid var(--color-light, #e0e0e0);
}

.admin-table th {
  font-weight: 600;
  background: var(--color-bg, #f5f5f5);
  color: var(--color-dark, #1a1a2e);
}

.admin-table tr:hover td {
  background: var(--color-bg, #f5f5f5);
}

.role-badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.role-admin {
  background: rgba(255, 107, 53, 0.2);
  color: #d84315;
}

.role-technician {
  background: rgba(23, 162, 184, 0.2);
  color: #0c5460;
}

.role-client {
  background: rgba(108, 117, 125, 0.2);
  color: #383d41;
}

.btn-action {
  padding: 0.35rem 0.75rem;
  margin-right: 0.25rem;
  background: transparent;
  border: 1px solid var(--color-primary, #ff6b35);
  color: var(--color-primary, #ff6b35);
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.2s;
}

.btn-action:hover {
  background: var(--color-primary, #ff6b35);
  color: var(--color-white, #fff);
}

.btn-action.danger {
  border-color: var(--color-danger, #dc3545);
  color: var(--color-danger, #dc3545);
}

.btn-action.danger:hover {
  background: var(--color-danger, #dc3545);
  color: var(--color-white, #fff);
}

.empty-row {
  text-align: center;
  color: var(--color-gray-600, #666);
  padding: 2rem;
}
</style>
