<template>
  <form @submit.prevent="onSubmit" class="user-form" data-testid="user-form">
    <div class="form-row">
      <div class="form-group">
        <label>Email *</label>
        <input v-model="form.email" required type="email" data-testid="user-email" />
      </div>
      <div class="form-group">
        <label>Nombre completo *</label>
        <input v-model="form.full_name" required data-testid="user-full-name" />
      </div>
    </div>
    
    <div class="form-row">
      <div class="form-group">
        <label>Usuario *</label>
        <input v-model="form.username" required data-testid="user-username" />
      </div>
      <div class="form-group">
        <label>Rol</label>
        <select v-model="form.role" data-testid="user-role">
          <option value="client">Cliente</option>
          <option value="technician">Técnico</option>
          <option value="admin">Admin</option>
        </select>
      </div>
    </div>
    
    <div class="form-group">
      <label>Contraseña {{ isEditing ? '(dejar vacío para mantener)' : '*' }}</label>
      <div class="password-field">
        <input
          v-model="form.password"
          :required="!isEditing"
          :type="showPassword ? 'text' : 'password'"
          data-testid="user-password"
        />
        <button type="button" class="toggle-password" @click="showPassword = !showPassword">
          {{ showPassword ? '🙈' : '👁️' }}
        </button>
      </div>
    </div>
    
    <div class="form-actions">
      <button type="submit" class="btn-submit" data-testid="user-save">
        {{ isEditing ? 'Actualizar' : 'Guardar' }}
      </button>
    </div>
  </form>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useUsers } from '@/composables/useUsers'

const { createUser, updateUser } = useUsers()
const emit = defineEmits(['saved'])

const props = defineProps({
  user: { type: Object, default: null }
})

const emptyForm = () => ({ 
  email: '', 
  full_name: '', 
  username: '', 
  role: 'client', 
  password: '' 
})

const form = ref(emptyForm())
const showPassword = ref(false)
const isEditing = computed(() => Boolean(props.user?.id))

watch(
  () => props.user,
  (user) => {
    form.value = {
      email: user?.email || '',
      full_name: user?.full_name || user?.firstName + ' ' + user?.lastName || '',
      username: user?.username || '',
      role: user?.role || 'client',
      password: ''
    }
  },
  { immediate: true }
)

const onSubmit = async () => {
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

<style scoped>
.user-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.form-group label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-dark, #1a1a2e);
}

.form-group input,
.form-group select {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-light, #e0e0e0);
  border-radius: 6px;
  font-size: 1rem;
  min-height: 40px;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: var(--color-primary, #ff6b35);
  box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.1);
}

.password-field {
  display: flex;
  gap: 0.5rem;
}

.password-field input {
  flex: 1;
}

.toggle-password {
  padding: 0.5rem 0.75rem;
  background: var(--color-light, #e0e0e0);
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
}

.form-actions {
  margin-top: 0.5rem;
}

.btn-submit {
  padding: 0.75rem 1.5rem;
  background: var(--color-primary, #ff6b35);
  color: var(--color-white, #fff);
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}

.btn-submit:hover {
  opacity: 0.9;
}
</style>
