<template>
  <section class="admin-section">
    <div class="admin-section-header">
      <h2 class="admin-section-title">Usuarios</h2>
      <button class="admin-btn admin-btn-outline" @click="fetchUsers">Actualizar</button>
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
        <tr v-for="user in users" :key="user.id">
          <td data-label="Email">{{ user.email }}</td>
          <td data-label="Nombre">{{ user.full_name }}</td>
          <td data-label="Rol">{{ user.role }}</td>
          <td data-label="Acciones">
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
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 8px 16px rgba(62, 60, 56, 0.12);
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
