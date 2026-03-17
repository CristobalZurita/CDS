<template>
  <form class="auth-form" @submit.prevent="handleSubmit">
    <BaseInput
      id="login-email"
      v-model.trim="email"
      label="Email"
      type="email"
      autocomplete="email"
      placeholder="tu@email.com"
      :disabled="isLoading"
      :error="errors.email"
      required
    />

    <BaseInput
      id="login-password"
      v-model="password"
      label="Contraseña"
      :type="showPassword ? 'text' : 'password'"
      autocomplete="current-password"
      placeholder="••••••••"
      :disabled="isLoading"
      :error="errors.password"
      required
    />

    <button type="button" class="auth-toggle" @click="showPassword = !showPassword">
      {{ showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña' }}
    </button>

    <TurnstileWidget @verify="onVerify" />

    <BaseInput
      v-if="requires2fa"
      id="login-2fa"
      v-model.trim="twoFactorCode"
      label="Código 2FA"
      type="text"
      placeholder="123456"
      :disabled="isLoading"
      :error="errors.twoFactorCode"
      required
    />

    <p v-if="apiError" class="auth-error">{{ apiError }}</p>

    <BaseButton
      type="submit"
      :loading="isLoading"
      :loading-text="requires2fa ? 'Verificando...' : 'Iniciando...'"
      :disabled="submitDisabled"
    >
      {{ requires2fa ? 'Verificar código' : 'Iniciar sesión' }}
    </BaseButton>

    <div class="auth-links">
      <router-link to="/register">Crear cuenta</router-link>
      <router-link to="/password-reset">Recuperar contraseña</router-link>
    </div>
  </form>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { BaseInput, BaseButton } from '@/components/base'
import { useLoginValidation } from '@/composables/useAuthForms'
import TurnstileWidget from '@/components/widgets/TurnstileWidget.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const showPassword = ref(false)
const turnstileToken = ref('')
const apiError = ref('')
const isLoading = ref(false)
const requires2fa = ref(false)
const challengeId = ref('')
const twoFactorCode = ref('')

const { errors, canSubmit, validate } = useLoginValidation({
  email,
  password,
  requires2fa,
  twoFactorCode
})

const submitDisabled = computed(() => {
  if (isLoading.value) return true
  if (!canSubmit.value) return true
  if (!requires2fa.value && !turnstileToken.value) return true
  return false
})

function onVerify(token) {
  turnstileToken.value = token
  apiError.value = ''
}

async function handleSubmit() {
  apiError.value = ''

  if (!validate()) return

  if (!requires2fa.value && !turnstileToken.value) {
    apiError.value = 'Captcha requerido'
    return
  }

  isLoading.value = true

  try {
    if (!requires2fa.value) {
      const result = await authStore.login(email.value.trim(), password.value, turnstileToken.value)
      if (result?.requires_2fa) {
        requires2fa.value = true
        challengeId.value = String(result.challenge_id || '')
        return
      }
    } else {
      await authStore.verifyTwoFactor(challengeId.value, twoFactorCode.value.trim())
    }

    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : ''
    if (redirect) {
      router.push(redirect)
      return
    }

    router.push(authStore.isAdmin ? '/admin' : '/dashboard')
  } catch {
    apiError.value = authStore.error || 'Error al iniciar sesión'
  } finally {
    isLoading.value = false
  }
}

watch(email, () => {
  errors.email = ''
  apiError.value = ''
})

watch(password, () => {
  errors.password = ''
  apiError.value = ''
})

watch(twoFactorCode, () => {
  errors.twoFactorCode = ''
  apiError.value = ''
})

watch(requires2fa, (enabled) => {
  if (!enabled) {
    twoFactorCode.value = ''
    errors.twoFactorCode = ''
  }
})
</script>

<style scoped src="./commonAuthForm.css"></style>
