<template>
  <div class="login-form-container">
    <form @submit.prevent="handleLogin" class="login-form">
      <div class="form-group">
        <label for="email" class="form-label">Email</label>
        <input
          id="email"
          v-model="formData.email"
          type="email"
          class="form-control"
          placeholder="tu@email.com"
          required
          :disabled="isLoading"
        />
        <span v-if="errors.email" class="error-text">{{ errors.email }}</span>
      </div>

      <div class="form-group">
        <label for="password" class="form-label">Contraseña</label>
        <input
          id="password"
          v-model="formData.password"
          type="password"
          class="form-control"
          placeholder="••••••••"
          required
          :disabled="isLoading"
        />
        <span v-if="errors.password" class="error-text">{{ errors.password }}</span>
      </div>

      <div v-if="apiError" class="alert alert-danger">
        {{ apiError }}
      </div>

      <button
        type="submit"
        class="btn btn-primary btn-block"
        :disabled="isLoading"
      >
        <span v-if="isLoading" class="spinner-border spinner-border-sm me-2"></span>
        {{ isLoading ? 'Iniciando sesión...' : 'Iniciar Sesión' }}
      </button>

      <div class="text-center mt-3">
        <p>¿No tienes cuenta? 
          <router-link to="/register" class="link">Regístrate aquí</router-link>
        </p>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const formData = reactive({
  email: '',
  password: ''
})

const errors = reactive({
  email: '',
  password: ''
})

const isLoading = ref(false)
const apiError = ref('')

/**
 * Validar formulario
 */
function validateForm() {
  errors.email = ''
  errors.password = ''

  if (!formData.email) {
    errors.email = 'El email es requerido'
  } else if (!isValidEmail(formData.email)) {
    errors.email = 'Email inválido'
  }

  if (!formData.password) {
    errors.password = 'La contraseña es requerida'
  } else if (formData.password.length < 6) {
    errors.password = 'La contraseña debe tener al menos 6 caracteres'
  }

  return !errors.email && !errors.password
}

/**
 * Validar formato de email
 */
function isValidEmail(email) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return re.test(email)
}

/**
 * Manejar submit del formulario
 */
async function handleLogin() {
  apiError.value = ''

  if (!validateForm()) {
    return
  }

  isLoading.value = true

  try {
    await authStore.login(formData.email, formData.password)
    router.push('/dashboard')
  } catch (error) {
    apiError.value = authStore.error || 'Error al iniciar sesión'
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped lang="scss">
.login-form-container {
  max-width: 400px;
  margin: 2rem auto;
  padding: 2rem;
  background: #f8f9fa;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.login-form {
  .form-group {
    margin-bottom: 1.5rem;
  }

  .form-label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 600;
    color: #333;
  }

  .form-control {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
    transition: border-color 0.2s;

    &:focus {
      outline: none;
      border-color: #ff8c00;
      box-shadow: 0 0 0 3px rgba(255, 140, 0, 0.1);
    }

    &:disabled {
      background-color: #e9ecef;
      cursor: not-allowed;
    }
  }

  .error-text {
    display: block;
    color: #dc3545;
    font-size: 0.875rem;
    margin-top: 0.25rem;
  }

  .btn-block {
    width: 100%;
    margin-top: 1rem;
  }

  .link {
    color: #ff8c00;
    text-decoration: none;
    font-weight: 600;

    &:hover {
      text-decoration: underline;
    }
  }
}

.alert {
  padding: 0.75rem;
  border-radius: 4px;
  margin-bottom: 1rem;

  &.alert-danger {
    background-color: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
  }
}
</style>
