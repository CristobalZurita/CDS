<template>
  <form @submit.prevent="onSubmit" data-testid="user-form">
    <div>
      <label>Email</label>
      <input v-model="form.email" required type="email" data-testid="user-email" />
    </div>
    <div>
      <label>Nombre completo</label>
      <input v-model="form.full_name" required data-testid="user-full-name" />
    </div>
    <div>
      <label>Usuario</label>
      <input v-model="form.username" required data-testid="user-username" />
    </div>
    <div>
      <label>Rol</label>
      <select v-model="form.role" data-testid="user-role">
        <option value="client">Cliente</option>
        <option value="technician">Técnico</option>
        <option value="admin">Admin</option>
      </select>
    </div>
    <div>
      <label>Contraseña</label>
      <div class="password-field">
        <input
          v-model="form.password"
          :required="!isEditing"
          :type="showPassword ? 'text' : 'password'"
          data-testid="user-password"
        />
        <button type="button" class="toggle-password" @click="showPassword = !showPassword">
          {{ showPassword ? 'Ocultar' : 'Mostrar' }}
        </button>
      </div>
    </div>
    <button type="submit" data-testid="user-save">{{ isEditing ? 'Actualizar' : 'Guardar' }}</button>
  </form>
</template>
<script setup>
import { computed, ref, watch } from 'vue'
import { useUsers } from '@/composables/useUsers'
const { createUser, updateUser } = useUsers()
const emit = defineEmits(['saved'])
const props = defineProps({
  user: {
    type: Object,
    default: null
  }
})
const emptyForm = () => ({ email: '', full_name: '', username: '', role: 'client', password: '' })
const form = ref(emptyForm())
const showPassword = ref(false)
const isEditing = computed(() => Boolean(props.user?.id))

watch(
  () => props.user,
  (user) => {
    form.value = {
      email: user?.email || '',
      full_name: user?.full_name || '',
      username: user?.username || '',
      role: user?.role || 'client',
      password: ''
    }
  },
  { immediate: true }
)

async function onSubmit() {
  try {
    const payload = { ...form.value }
    if (isEditing.value) {
      if (!payload.password) {
        delete payload.password
      }
      await updateUser(props.user.id, payload)
    } else {
      await createUser(payload)
    }
    emit('saved')
    form.value = emptyForm()
  } catch (e) {
    console.error('Error guardando usuario:', e)
    alert('Error guardando usuario')
  }
}
</script>
<style lang="scss" scoped>
@use "@/scss/_core.scss" as *;

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
