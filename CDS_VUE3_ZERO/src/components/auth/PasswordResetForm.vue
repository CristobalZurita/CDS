<template>
  <section class="reset-form">
    <div class="mode-toggle">
      <button type="button" class="mode-toggle__btn" :class="{ active: mode === 'request' }" @click="mode = 'request'">Solicitar reset</button>
      <button type="button" class="mode-toggle__btn" :class="{ active: mode === 'reset' }" @click="mode = 'reset'">Cambiar contraseña</button>
    </div>

    <form v-if="mode === 'request'" class="flow" @submit.prevent="requestReset">
      <BaseInput id="reset-email" v-model.trim="email" label="Email" type="email" autocomplete="email" :disabled="isLoading" :error="errors.email" required />
      <BaseButton type="submit" :loading="isLoading" :disabled="submitDisabled" loading-text="Enviando...">Enviar instrucciones</BaseButton>
    </form>

    <form v-else class="flow" @submit.prevent="confirmReset">
      <BaseInput id="reset-token" v-model.trim="token" label="Token" type="text" :disabled="isLoading" :error="errors.token" required />
      <BaseInput id="reset-new-password" v-model="newPassword" :type="showPassword ? 'text' : 'password'" label="Nueva contraseña" autocomplete="new-password" :disabled="isLoading" :error="errors.newPassword" required />
      <BaseInput id="reset-confirm-password" v-model="confirmPassword" :type="showPassword ? 'text' : 'password'" label="Confirmar contraseña" autocomplete="new-password" :disabled="isLoading" :error="errors.confirmPassword" required />

      <button type="button" class="show-btn" @click="showPassword = !showPassword">
        {{ showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña' }}
      </button>

      <BaseButton type="submit" :loading="isLoading" :disabled="submitDisabled" loading-text="Actualizando...">Actualizar contraseña</BaseButton>
    </form>

    <p v-if="message" class="feedback" :class="`feedback--${messageType}`">{{ message }}</p>

    <p class="back-link">
      <router-link to="/login">Volver a iniciar sesión</router-link>
    </p>
  </section>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { usePasswordResetValidation } from '@/composables/useAuthForms'
import { BaseInput, BaseButton } from '@/components/ui'

const route = useRoute()
const authStore = useAuthStore()

const mode = ref('request')
const email = ref('')
const token = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const showPassword = ref(false)
const isLoading = ref(false)
const message = ref('')
const messageType = ref('ok')
const { errors, canSubmit, validateRequest, validateReset } = usePasswordResetValidation({
  mode,
  email,
  token,
  newPassword,
  confirmPassword
})

const submitDisabled = computed(() => isLoading.value || !canSubmit.value)

function setMessage(text, type = 'ok') {
  message.value = text
  messageType.value = type
}

async function requestReset() {
  setMessage('')

  if (!validateRequest()) {
    return
  }

  isLoading.value = true
  try {
    await authStore.requestPasswordReset(email.value.trim())
    setMessage('Revisa tu correo para continuar', 'ok')
  } catch {
    setMessage(authStore.error || 'No se pudo enviar el correo', 'error')
  } finally {
    isLoading.value = false
  }
}

async function confirmReset() {
  setMessage('')

  if (!validateReset()) {
    setMessage('Revisa los campos del formulario', 'error')
    return
  }

  isLoading.value = true
  try {
    await authStore.confirmPasswordReset(token.value.trim(), newPassword.value)
    setMessage('Contraseña actualizada correctamente', 'ok')
  } catch {
    setMessage(authStore.error || 'No se pudo actualizar la contraseña', 'error')
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  const queryToken = route.query?.token
  if (typeof queryToken === 'string' && queryToken.length) {
    token.value = queryToken
    mode.value = 'reset'
  }
})

watch(mode, () => {
  setMessage('')
  errors.email = ''
  errors.token = ''
  errors.newPassword = ''
  errors.confirmPassword = ''
})

watch([email, token, newPassword, confirmPassword], () => {
  setMessage('')
})
</script>

<style scoped src="./commonAuthForm.css"></style>
