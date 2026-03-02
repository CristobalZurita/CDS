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
          data-testid="login-email"
          placeholder="tu@email.com"
          required
          :disabled="isLoading"
        />
        <span v-if="errors.email" class="error-text">{{ errors.email }}</span>
      </div>

      <div class="form-group">
        <label for="password" class="form-label">Contraseña</label>
        <div class="password-field">
          <input
            id="password"
            v-model="formData.password"
            :type="showPassword ? 'text' : 'password'"
            class="form-control"
            data-testid="login-password"
            placeholder="••••••••"
            required
            :disabled="isLoading"
          />
          <button type="button" class="toggle-password" @click="showPassword = !showPassword">
            {{ showPassword ? 'Ocultar' : 'Mostrar' }}
          </button>
        </div>
        <span v-if="errors.password" class="error-text">{{ errors.password }}</span>
      </div>

      <TurnstileWidget @verify="onVerify" />

      <div v-if="requires2fa" class="form-group">
        <label for="twoFactor" class="form-label">Código de verificación</label>
        <input
          id="twoFactor"
          v-model="twoFactorCode"
          type="text"
          class="form-control"
          placeholder="123456"
          :disabled="isLoading"
        />
      </div>

      <div v-if="apiError" class="alert alert-danger" data-testid="login-error">
        {{ apiError }}
      </div>

      <button
        type="submit"
        class="btn btn-primary btn-block"
        data-testid="login-submit"
        :disabled="isLoading"
      >
        <span v-if="isLoading" class="spinner-border spinner-border-sm me-2"></span>
        {{ isLoading ? 'Procesando...' : (requires2fa ? 'Verificar código' : 'Iniciar Sesión') }}
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
import TurnstileWidget from '@/vue/components/widgets/TurnstileWidget.vue'

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
const turnstileToken = ref('')
const showPassword = ref(false)
const requires2fa = ref(false)
const challengeId = ref(null)
const twoFactorCode = ref('')

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
  if (!turnstileToken.value) {
    apiError.value = 'Captcha requerido'
    return
  }

  isLoading.value = true

  try {
    if (!requires2fa.value) {
      const res = await authStore.login(formData.email, formData.password, turnstileToken.value)
      if (res?.requires_2fa) {
        requires2fa.value = true
        challengeId.value = res.challenge_id
        return
      }
    } else {
      await authStore.verifyTwoFactor(challengeId.value, twoFactorCode.value)
    }
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

function onVerify(token) {
  turnstileToken.value = token
}
</script>
