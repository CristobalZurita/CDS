<template>
  <form @submit.prevent="handleRegister" class="register-form">
    <div class="form-group">
      <label>Email</label>
      <input v-model="form.email" type="email" required />
    </div>

    <div class="form-group">
      <label>Usuario</label>
      <input v-model="form.username" type="text" required />
    </div>

    <div class="form-group">
      <label>Nombre completo</label>
      <input v-model="form.full_name" type="text" required />
    </div>

    <div class="form-group">
      <label>Teléfono (opcional)</label>
      <input v-model="form.phone" type="text" />
    </div>

    <div class="form-group">
      <label>Contraseña</label>
      <input v-model="form.password" type="password" required minlength="8" />
    </div>

    <div v-if="apiError" class="alert alert-danger">{{ apiError }}</div>

    <button type="submit" class="btn btn-primary" :disabled="loading">
      {{ loading ? 'Creando...' : 'Crear cuenta' }}
    </button>
  </form>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()

const form = reactive({ email: '', username: '', full_name: '', password: '', phone: '' })
const loading = ref(false)
const apiError = ref('')

async function handleRegister() {
  apiError.value = ''
  loading.value = true
  try {
    await auth.register(form)
    router.push('/login')
  } catch (err) {
    apiError.value = auth.error || err?.response?.data?.detail || 'Error en el registro'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-form { width: 100%; }
.form-group { margin-bottom: 1rem; }
.form-group input { width: 100%; padding: 0.6rem; border: 1px solid #ddd; border-radius: 4px; }
</style>
