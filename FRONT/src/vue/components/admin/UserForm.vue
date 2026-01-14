<template>
  <form @submit.prevent="onSubmit">
    <div>
      <label>Email</label>
      <input v-model="form.email" required type="email" />
    </div>
    <div>
      <label>Nombre completo</label>
      <input v-model="form.full_name" required />
    </div>
    <div>
      <label>Usuario</label>
      <input v-model="form.username" required />
    </div>
    <div>
      <label>Rol</label>
      <select v-model="form.role">
        <option value="client">Cliente</option>
        <option value="technician">Técnico</option>
        <option value="admin">Admin</option>
      </select>
    </div>
    <div>
      <label>Contraseña</label>
      <input v-model="form.password" required type="password" />
    </div>
    <button type="submit">Guardar</button>
  </form>
</template>
<script setup>
import { ref } from 'vue'
import { useUsers } from '@/composables/useUsers'
const { createUser, updateUser } = useUsers()
const form = ref({ email: '', full_name: '', username: '', role: 'client', password: '' })
function onSubmit() {
  // Si es edición, usar updateUser, si es nuevo, usar createUser
  createUser(form.value)
}
</script>
