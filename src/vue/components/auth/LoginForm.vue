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

<style scoped lang="scss">
@import "/src/scss/_theming.scss";

/* ===========================================
   LOGINFORM - Manual de Identidad Visual
   Paleta: Vintage Black ($color-dark), Orange ($color-primary),
           Vintage Orange ($vintage-orange), Vintage Beige ($color-light),
           Black ($color-black), Fluor Green ($fluor-green)
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
    color: $brand-text; /* Vintage Black */
    text-transform: uppercase;
    font-size: 0.85rem;
    letter-spacing: 0.05em;
  }

  .form-control {
    width: 100%;
    padding: 0.75rem;
    border: 2px solid $brand-text; /* Vintage Black */
    border-radius: 4px;
    font-family: 'Cervo Neue', sans-serif;
    font-size: 1rem;
    background: $white;
    color: $brand-text; /* Vintage Black */
    transition: border-color 0.2s, box-shadow 0.2s;

    &::placeholder {
      color: $vintage-orange; /* Vintage Orange */
      opacity: 0.6;
    }

    &:focus {
      outline: none;
      border-color: $brand-primary; /* Orange - Paleta Web */
      box-shadow: 0 0 0 3px rgba($brand-primary, 0.2);
    }

    &:disabled {
      background-color: $vintage-beige; /* Vintage Beige */
      cursor: not-allowed;
      opacity: 0.7;
    }
  }

  .password-field {
    display: flex;
    gap: 0.5rem;
  }

  .toggle-password {
    border: 2px solid $brand-text;
    background: $brand-paper;
    color: $brand-text;
    padding: 0 0.8rem;
    border-radius: 4px;
    font-size: 0.85rem;
    font-weight: 600;
  }

  .error-text {
    display: block;
    color: $brand-primary; /* Orange - Paleta Web */
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
    background-color: $brand-primary; /* Orange - Paleta Web */
    border: 2px solid $brand-primary;
    color: $black; /* Black */
    font-family: 'Cervo Extrabold', 'Cervo Neue', sans-serif;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    padding: 0.75rem 1.5rem;
    font-size: 1rem;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s;

    &:hover {
      background-color: $vintage-orange; /* Vintage Orange */
      border-color: $vintage-orange;
    }

    &:disabled {
      background-color: $vintage-beige; /* Vintage Beige */
      border-color: $brand-text;
      color: $brand-text;
      cursor: not-allowed;
    }
  }

  .link {
    color: $brand-primary; /* Orange - Paleta Web */
    text-decoration: none;
    font-family: 'Cervo Neue Semibold', 'Cervo Neue', sans-serif;
    font-weight: 600;

    &:hover {
      color: $vintage-orange; /* Vintage Orange */
      text-decoration: underline;
    }
  }
}

.text-center {
  color: $brand-text; /* Vintage Black */
  font-family: 'Cervo Neue', sans-serif;
}

.alert {
  padding: 0.75rem;
  border-radius: 4px;
  margin-bottom: 1rem;
  font-family: 'Cervo Neue', sans-serif;

  &.alert-danger {
    background-color: rgba($brand-primary, 0.15); /* Orange con transparencia */
    color: $brand-text; /* Vintage Black */
    border: 2px solid $brand-primary; /* Orange */
  }
}

/* Spinner con colores de marca */
.spinner-border {
  border-color: $brand-text;
  border-right-color: transparent;
}
</style>
