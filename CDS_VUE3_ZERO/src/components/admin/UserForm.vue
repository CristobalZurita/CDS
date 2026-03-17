<template>
  <form @submit.prevent="onSubmit" class="user-form" data-testid="user-form">
    <p v-if="error" class="form-error">{{ error }}</p>

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

const { createUser, updateUser, error } = useUsers()
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
  }
}
</script>

<style scoped>
.user-form {
  display: flex;
  flex-direction: column;
  gap: var(--admin-space-md, 1.2rem);
}

.form-error {
  margin: 0;
  padding: var(--admin-space-sm, 0.96rem) var(--cds-space-md);
  border-radius: var(--cds-radius-sm);
  border: 1px solid var(--cds-invalid-border);
  background: var(--cds-invalid-bg);
  color: var(--cds-invalid-text);
  font-size: var(--cds-text-sm);
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: var(--admin-space-md, 1.2rem);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.form-group label {
  font-size: var(--cds-text-sm);
  font-weight: 600;
  color: var(--cds-dark);
}

.form-group input,
.form-group select {
  min-height: var(--admin-control-min-height, 52px);
  padding: var(--cds-space-sm) var(--cds-space-md);
  border: 1px solid var(--cds-border-input);
  border-radius: var(--cds-radius-sm);
  font-size: var(--cds-text-base);
  color: var(--cds-text-normal);
  background: var(--cds-white);
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: var(--cds-primary);
  box-shadow: var(--cds-focus-ring);
}

.password-field {
  display: flex;
  gap: var(--admin-space-xs, 0.66rem);
}

.password-field input {
  flex: 1;
}

.toggle-password {
  min-height: var(--admin-control-min-height, 52px);
  padding: var(--cds-space-sm) var(--cds-space-md);
  background: var(--cds-light-2);
  border: none;
  border-radius: var(--cds-radius-sm);
  cursor: pointer;
  font-size: var(--cds-text-base);
}

.form-actions {
  margin-top: var(--admin-space-xs, 0.66rem);
}

.btn-submit {
  min-height: var(--admin-control-min-height, 52px);
  padding: var(--cds-space-md) var(--cds-space-xl);
  background: var(--cds-primary);
  color: var(--cds-white);
  border: none;
  border-radius: var(--cds-radius-sm);
  font-size: var(--cds-text-base);
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}

.btn-submit:hover {
  opacity: 0.9;
}
</style>
