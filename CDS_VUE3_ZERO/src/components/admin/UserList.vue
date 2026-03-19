<template>
  <div class="users-list">
    <div class="list-toolbar">
      <span class="list-count">{{ users.length }} usuarios</span>
      <button class="btn-refresh" @click="fetchUsers">↻ Actualizar</button>
    </div>

    <p v-if="error" class="list-error">{{ error }}</p>
    
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

    <BaseConfirmDialog
      :open="Boolean(userPendingDelete)"
      title="Eliminar usuario"
      :message="userPendingDelete ? `¿Eliminar usuario ${userPendingDelete.email}?` : ''"
      confirm-label="Eliminar"
      :confirm-loading="isDeleting"
      @cancel="cancelDelete"
      @confirm="confirmDelete"
    />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { BaseConfirmDialog } from '@/components/base'
import { useUsers } from '@/composables/useUsers'

const { users, fetchUsers, deleteUser, error } = useUsers()
const emit = defineEmits(['edit'])
const userPendingDelete = ref(null)
const isDeleting = ref(false)

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

const removeUser = (user) => {
  userPendingDelete.value = user
}

const cancelDelete = () => {
  if (isDeleting.value) return
  userPendingDelete.value = null
}

const confirmDelete = async () => {
  if (!userPendingDelete.value || isDeleting.value) return
  isDeleting.value = true
  try {
    await deleteUser(userPendingDelete.value.id)
    userPendingDelete.value = null
  } catch {
    // El mensaje ya queda expuesto en error
  } finally {
    isDeleting.value = false
  }
}

onMounted(fetchUsers)
</script>

<style scoped src="./commonAdminTable.css"></style>
<style scoped src="./userListShared.css"></style>
