<template>
  <section class="content-section">
    <div class="section-header">
      <h2>Gestión de Usuarios</h2>
      <button class="btn-primary" @click="toggleUserForm">
        {{ showUserForm ? 'Cancelar' : '+ Nuevo Usuario' }}
      </button>
    </div>

    <div v-if="showUserForm" class="form-panel">
      <h3>{{ selectedUser ? 'Editar usuario' : 'Crear usuario' }}</h3>
      <UserForm :user="selectedUser" @saved="onUserSaved" />
    </div>

    <UserList :key="userRefreshKey" @edit="onEditUser" />
  </section>
</template>

<script setup>
import { ref } from 'vue'
import UserForm from '@/components/admin/UserForm.vue'
import UserList from '@/components/admin/UserList.vue'

const showUserForm = ref(false)
const selectedUser = ref(null)
const userRefreshKey = ref(0)

function onUserSaved() {
  showUserForm.value = false
  selectedUser.value = null
  userRefreshKey.value += 1
}

function toggleUserForm() {
  if (showUserForm.value) {
    showUserForm.value = false
    selectedUser.value = null
    return
  }
  selectedUser.value = null
  showUserForm.value = true
}

function onEditUser(user) {
  selectedUser.value = user
  showUserForm.value = true
}
</script>

<style scoped src="../../pages/admin/commonAdminPage.css"></style>
<style scoped src="../../pages/admin/adminDashboardShared.css"></style>
