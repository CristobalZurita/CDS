<template>
  <div class="password-reset">
    <div class="mode-toggle">
      <button
        type="button"
        class="toggle-btn"
        :class="{ active: mode === 'request' }"
        @click="mode = 'request'"
      >
        Solicitar reset
      </button>
      <button
        type="button"
        class="toggle-btn"
        :class="{ active: mode === 'reset' }"
        @click="mode = 'reset'"
      >
        Cambiar contraseña
      </button>
    </div>

    <form v-if="mode === 'request'" @submit.prevent="requestReset" class="form">
      <div class="form-group">
        <label>Email</label>
        <input v-model="email" type="email" required :disabled="isLoading" />
      </div>
      <button type="submit" class="btn-primary" :disabled="isLoading">
        {{ isLoading ? 'Enviando...' : 'Enviar instrucciones' }}
      </button>
    </form>

    <form v-else @submit.prevent="confirmReset" class="form">
      <div class="form-group">
        <label>Token</label>
        <input v-model="token" type="text" required :disabled="isLoading" />
      </div>
      <div class="form-group">
        <label>Nueva contraseña</label>
        <div class="password-field">
          <input v-model="newPassword" :type="showPassword ? 'text' : 'password'" required minlength="8" :disabled="isLoading" />
          <button type="button" class="toggle-password" @click="showPassword = !showPassword">
            {{ showPassword ? 'Ocultar' : 'Mostrar' }}
          </button>
        </div>
      </div>
      <div class="form-group">
        <label>Confirmar contraseña</label>
        <div class="password-field">
          <input v-model="confirmPassword" :type="showPassword ? 'text' : 'password'" required minlength="8" :disabled="isLoading" />
          <button type="button" class="toggle-password" @click="showPassword = !showPassword">
            {{ showPassword ? 'Ocultar' : 'Mostrar' }}
          </button>
        </div>
      </div>
      <button type="submit" class="btn-primary" :disabled="isLoading">
        {{ isLoading ? 'Actualizando...' : 'Actualizar contraseña' }}
      </button>
    </form>
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

<style scoped>
.password-reset {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.mode-toggle {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.password-field {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.toggle-password {
  border: 1px solid #d1d5db;
  background: #f3f4f6;
  padding: 0.35rem 0.6rem;
  border-radius: 4px;
  font-size: 0.85rem;
}

.toggle-btn {
  background: #f1f1f1;
  border: 1px solid #ccc;
  padding: 0.4rem 0.8rem;
  border-radius: 6px;
  cursor: pointer;
}

.toggle-btn.active {
  background: #ec6b00;
  color: #000;
  border-color: #ec6b00;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.4rem;
  font-weight: 600;
}

.form-group input {
  width: 100%;
  padding: 0.6rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.btn-primary {
  background: #ec6b00;
  color: #000;
  border: none;
  padding: 0.7rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}

.btn-primary:disabled {
  background: #d3d0c3;
  cursor: not-allowed;
}
</style>
