<template>
  <form class="auth-form" @submit.prevent="handleRegister">
    <BaseInput id="register-email" v-model.trim="form.email" label="Email" type="email" autocomplete="email" :disabled="loading" :error="errors.email" required />
    <BaseInput id="register-username" v-model.trim="form.username" label="Usuario" type="text" autocomplete="username" :disabled="loading" :error="errors.username" required />
    <BaseInput id="register-fullname" v-model.trim="form.full_name" label="Nombre completo" type="text" :disabled="loading" :error="errors.full_name" required />
    <BaseInput id="register-phone" v-model.trim="form.phone" label="Teléfono (opcional)" type="text" autocomplete="tel" :disabled="loading" />
    <BaseInput id="register-password" v-model="form.password" :type="showPassword ? 'text' : 'password'" label="Contraseña" autocomplete="new-password" :disabled="loading" :error="errors.password" required />

    <button type="button" class="auth-toggle" @click="showPassword = !showPassword">
      {{ showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña' }}
    </button>

    <TurnstileWidget @verify="onVerify" />

    <p v-if="apiError" class="auth-error">{{ apiError }}</p>

    <BaseButton type="submit" :loading="loading" :disabled="submitDisabled" loading-text="Creando...">Crear cuenta</BaseButton>

    <p class="auth-link">¿Ya tienes cuenta? <router-link to="/login">Inicia sesión</router-link></p>
  </form>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { BaseInput, BaseButton } from '@/components/base'
import { useRegisterValidation } from '@/composables/useAuthForms'
import TurnstileWidget from '@/components/widgets/TurnstileWidget.vue'

const authStore = useAuthStore()
const router = useRouter()

const form = reactive({
  email: '',
  username: '',
  full_name: '',
  password: '',
  phone: '',
  turnstile_token: ''
})

const loading = ref(false)
const apiError = ref('')
const showPassword = ref(false)
const { errors, canSubmit, validate } = useRegisterValidation(form)

const submitDisabled = computed(() => {
  if (loading.value) return true
  if (!canSubmit.value) return true
  if (!form.turnstile_token) return true
  return false
})

function onVerify(token) {
  form.turnstile_token = token
  apiError.value = ''
}

async function handleRegister() {
  apiError.value = ''
  loading.value = true

  try {
    if (!validate()) {
      return
    }

    if (!form.turnstile_token) {
      apiError.value = 'Captcha requerido'
      return
    }
    await authStore.register(form)
    router.push('/login')
  } catch {
    apiError.value = authStore.error || 'Error en el registro'
  } finally {
    loading.value = false
  }
}

watch(() => form.email, () => {
  errors.email = ''
  apiError.value = ''
})

watch(() => form.username, () => {
  errors.username = ''
  apiError.value = ''
})

watch(() => form.full_name, () => {
  errors.full_name = ''
  apiError.value = ''
})

watch(() => form.password, () => {
  errors.password = ''
  apiError.value = ''
})

watch(() => form.turnstile_token, () => {
  apiError.value = ''
})
</script>

<style scoped src="./commonAuthForm.css"></style>
