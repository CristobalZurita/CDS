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
<style scoped lang="scss">
@import "/src/scss/_theming.scss";

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
