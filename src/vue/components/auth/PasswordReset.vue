<template>
  <div class="password-reset">
    <div class="mode-toggle">
      <button
        type="button"
        class="toggle-btn"
        :class="{ active: mode === 'request' }"
        data-testid="password-reset-mode-request"
        @click="mode = 'request'"
      >
        Solicitar reset
      </button>
      <button
        type="button"
        class="toggle-btn"
        :class="{ active: mode === 'reset' }"
        data-testid="password-reset-mode-reset"
        @click="mode = 'reset'"
      >
        Cambiar contraseña
      </button>
    </div>

    <form v-if="mode === 'request'" @submit.prevent="requestReset" class="form">
      <div class="form-group">
        <label>Email</label>
        <input v-model="email" type="email" required :disabled="isLoading" data-testid="password-reset-email" />
      </div>
      <button type="submit" class="btn-primary" :disabled="isLoading" data-testid="password-reset-request-submit">
        {{ isLoading ? 'Enviando...' : 'Enviar instrucciones' }}
      </button>
    </form>

    <form v-else @submit.prevent="confirmReset" class="form">
      <div class="form-group">
        <label>Token</label>
        <input v-model="token" type="text" required :disabled="isLoading" data-testid="password-reset-token" />
      </div>
      <div class="form-group">
        <label>Nueva contraseña</label>
        <div class="password-field">
          <input v-model="newPassword" :type="showPassword ? 'text' : 'password'" required minlength="8" :disabled="isLoading" data-testid="password-reset-new" />
          <button type="button" class="toggle-password" @click="showPassword = !showPassword">
            {{ showPassword ? 'Ocultar' : 'Mostrar' }}
          </button>
        </div>
      </div>
      <div class="form-group">
        <label>Confirmar contraseña</label>
        <div class="password-field">
          <input v-model="confirmPassword" :type="showPassword ? 'text' : 'password'" required minlength="8" :disabled="isLoading" data-testid="password-reset-confirm" />
          <button type="button" class="toggle-password" @click="showPassword = !showPassword">
            {{ showPassword ? 'Ocultar' : 'Mostrar' }}
          </button>
        </div>
      </div>
      <button type="submit" class="btn-primary" :disabled="isLoading" data-testid="password-reset-confirm-submit">
        {{ isLoading ? 'Actualizando...' : 'Actualizar contraseña' }}
      </button>
    </form>

    <router-link class="back-link" to="/login">Volver al inicio de sesión</router-link>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '@/services/api'
import { showError, showSuccess } from '@/services/toastService'

const route = useRoute()
const mode = ref('request')
const email = ref('')
const token = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const isLoading = ref(false)
const showPassword = ref(false)

const requestReset = async () => {
  isLoading.value = true
  try {
    const { data } = await api.post('/auth/forgot-password', { email: email.value })
    showSuccess(data?.message || 'Revisa tu correo para continuar')
    if (data?.reset_token) {
      token.value = data.reset_token
      mode.value = 'reset'
    }
  } catch (err) {
    showError(err.response?.data?.detail || 'No se pudo enviar el correo')
  } finally {
    isLoading.value = false
  }
}

const confirmReset = async () => {
  if (newPassword.value !== confirmPassword.value) {
    showError('Las contraseñas no coinciden')
    return
  }
  isLoading.value = true
  try {
    const { data } = await api.post('/auth/reset-password', {
      token: token.value,
      new_password: newPassword.value
    })
    showSuccess(data?.message || 'Contraseña actualizada')
  } catch (err) {
    showError(err.response?.data?.detail || 'No se pudo actualizar la contraseña')
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
</script>

<style scoped lang="scss">
@use "@/scss/_core.scss" as *;

.password-reset {
  display: grid;
  gap: var(--spacer-md);
}

.mode-toggle {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--spacer-sm);
}

.toggle-btn,
.btn-primary,
.toggle-password {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 42px;
  padding: 0.7rem 1rem;
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
  font-weight: 700;
  cursor: pointer;
  transition: var(--transition-base);
}

.toggle-btn {
  border: 1px solid var(--color-light);
  background: transparent;
  color: var(--color-dark);
}

.toggle-btn.active,
.btn-primary {
  border: 0;
  background: var(--color-primary);
  color: var(--color-white);
}

.toggle-btn:hover,
.btn-primary:hover:not(:disabled),
.toggle-password:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.form {
  display: grid;
  gap: var(--spacer-md);
}

.form-group {
  display: grid;
  gap: 0.45rem;
}

label {
  color: var(--color-dark);
  font-size: var(--text-sm);
  font-weight: 700;
}

input {
  width: 100%;
  min-height: 46px;
  padding: 0.75rem 0.9rem;
  border: 1px solid var(--color-light);
  border-radius: var(--radius-sm);
  background: var(--color-white);
  color: var(--color-dark);
  font-size: var(--text-sm);
}

.password-field {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 0.55rem;
  align-items: center;
}

.toggle-password {
  border: 1px solid var(--color-light);
  background: var(--color-white);
  color: var(--color-dark);
}

.btn-primary:disabled {
  opacity: 0.65;
  cursor: wait;
}

.back-link {
  color: var(--color-primary);
  font-size: var(--text-sm);
  font-weight: 700;
  text-align: center;
  text-decoration: none;
}

.back-link:hover {
  text-decoration: underline;
}

@include media-breakpoint-down(md) {
  .mode-toggle,
  .password-field {
    grid-template-columns: 1fr;
  }

  .toggle-btn,
  .btn-primary,
  .toggle-password {
    width: 100%;
  }
}
</style>
