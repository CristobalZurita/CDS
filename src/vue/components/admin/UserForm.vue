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
      <div class="password-field">
        <input v-model="form.password" required :type="showPassword ? 'text' : 'password'" />
        <button type="button" class="toggle-password" @click="showPassword = !showPassword">
          {{ showPassword ? 'Ocultar' : 'Mostrar' }}
        </button>
      </div>
    </div>
    <button type="submit">Guardar</button>
  </form>
</template>
<script setup>
import { ref } from 'vue'
import { useUsers } from '@/composables/useUsers'
const { createUser, updateUser } = useUsers()
const emit = defineEmits(['saved'])
const form = ref({ email: '', full_name: '', username: '', role: 'client', password: '' })
const showPassword = ref(false)
async function onSubmit() {
  // Si es edición, usar updateUser, si es nuevo, usar createUser
  try {
    await createUser(form.value)
    emit('saved')
    form.value = { email: '', full_name: '', username: '', role: 'client', password: '' }
  } catch (e) {
    console.error('Error creando usuario:', e)
    alert('Error creando usuario')
  }
}
</script>
<style lang="scss" scoped>
@import '@/scss/_core.scss';

.password-field {
  display: flex;
  gap: $spacer-sm;
  align-items: center;
}

.toggle-password {
  border: 1px solid $color-gray-300-legacy;
  background: $color-gray-100-legacy;
  padding: 0.35rem 0.6rem;
  border-radius: $border-radius-sm;
  font-size: $text-sm;
}
</style>
