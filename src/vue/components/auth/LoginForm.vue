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
        <p>
          <router-link to="/password-reset" class="link">¿Olvidaste tu contraseña?</router-link>
        </p>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
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
    const redirect = route.query.redirect
    if (redirect) {
      router.push(redirect)
      return
    }

    router.push(authStore.isAdmin ? '/admin' : '/dashboard')
  } catch (error) {
    apiError.value = authStore.error || 'Error al iniciar sesión'
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped lang="scss">
/* ===========================================
   LOGINFORM - Manual de Identidad Visual
   Paleta: Vintage Black #3e3c38, Orange #ec6b00,
           Vintage Orange #cc7d43, Vintage Beige #d3d0c3,
           Black #000000, Fluor Green #d9ff4e
   Tipografía: Cervo Neue, Steelfish
   =========================================== */

.login-form-container {
  max-width: 400px;
  margin: 0 auto;
  padding: 0;
  background: transparent; /* Hereda de LoginPage */
  border-radius: 8px;
}

.login-form {
  .form-group {
    margin-bottom: 1.5rem;
  }

  .form-label {
    display: block;
    margin-bottom: 0.5rem;
    font-family: 'Cervo Neue Semibold', 'Cervo Neue', sans-serif;
    font-weight: 600;
    color: #3e3c38; /* Vintage Black */
    text-transform: uppercase;
    font-size: 0.85rem;
    letter-spacing: 0.05em;
  }

  .form-control {
    width: 100%;
    padding: 0.75rem;
    border: 2px solid #3e3c38; /* Vintage Black */
    border-radius: 4px;
    font-family: 'Cervo Neue', sans-serif;
    font-size: 1rem;
    background: #ffffff;
    color: #3e3c38; /* Vintage Black */
    transition: border-color 0.2s, box-shadow 0.2s;

    &::placeholder {
      color: #cc7d43; /* Vintage Orange */
      opacity: 0.6;
    }

    &:focus {
      outline: none;
      border-color: #ec6b00; /* Orange - Paleta Web */
      box-shadow: 0 0 0 3px rgba(236, 107, 0, 0.2);
    }

    &:disabled {
      background-color: #d3d0c3; /* Vintage Beige */
      cursor: not-allowed;
      opacity: 0.7;
    }
  }

  .error-text {
    display: block;
    color: #ec6b00; /* Orange - Paleta Web */
    font-family: 'Cervo Neue', sans-serif;
    font-size: 0.875rem;
    margin-top: 0.25rem;
  }

  .btn-block {
    width: 100%;
    margin-top: 1rem;
  }

  /* Botón principal - estilo de marca */
  .btn-primary {
    background-color: #ec6b00; /* Orange - Paleta Web */
    border: 2px solid #ec6b00;
    color: #000000; /* Black */
    font-family: 'Cervo Extrabold', 'Cervo Neue', sans-serif;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    padding: 0.75rem 1.5rem;
    font-size: 1rem;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s;

    &:hover {
      background-color: #cc7d43; /* Vintage Orange */
      border-color: #cc7d43;
    }

    &:disabled {
      background-color: #d3d0c3; /* Vintage Beige */
      border-color: #3e3c38;
      color: #3e3c38;
      cursor: not-allowed;
    }
  }

  .link {
    color: #ec6b00; /* Orange - Paleta Web */
    text-decoration: none;
    font-family: 'Cervo Neue Semibold', 'Cervo Neue', sans-serif;
    font-weight: 600;

    &:hover {
      color: #cc7d43; /* Vintage Orange */
      text-decoration: underline;
    }
  }
}

.text-center {
  color: #3e3c38; /* Vintage Black */
  font-family: 'Cervo Neue', sans-serif;
}

.alert {
  padding: 0.75rem;
  border-radius: 4px;
  margin-bottom: 1rem;
  font-family: 'Cervo Neue', sans-serif;

  &.alert-danger {
    background-color: rgba(236, 107, 0, 0.15); /* Orange con transparencia */
    color: #3e3c38; /* Vintage Black */
    border: 2px solid #ec6b00; /* Orange */
  }
}

/* Spinner con colores de marca */
.spinner-border {
  border-color: #3e3c38;
  border-right-color: transparent;
}
</style>
