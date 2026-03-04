<template>
	<div class="register-page">
		<div class="register-container">
			<router-link to="/" class="back-link">Volver al inicio</router-link>
			<h1>Crear cuenta</h1>

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
					<div class="password-field">
						<input v-model="form.password" :type="showPassword ? 'text' : 'password'" required minlength="8" />
						<button type="button" class="toggle-password" @click="showPassword = !showPassword">
							{{ showPassword ? 'Ocultar' : 'Mostrar' }}
						</button>
					</div>
				</div>

				<TurnstileWidget @verify="onVerify" />

				<div v-if="apiError" class="alert alert-danger">{{ apiError }}</div>

				<button type="submit" class="btn btn-primary" :disabled="loading">{{ loading ? 'Creando...' : 'Crear cuenta' }}</button>
			</form>

			<p class="muted">¿Ya tienes cuenta? <router-link to="/login">Inicia sesión</router-link></p>
		</div>
	</div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import TurnstileWidget from '@/vue/components/widgets/TurnstileWidget.vue'

const auth = useAuthStore()
const router = useRouter()

const form = reactive({ email: '', username: '', full_name: '', password: '', phone: '', turnstile_token: '' })
const loading = ref(false)
const apiError = ref('')
const showPassword = ref(false)

async function handleRegister() {
	apiError.value = ''
	loading.value = true
	try {
		if (!form.turnstile_token) {
			apiError.value = 'Captcha requerido'
			return
		}
		await auth.register(form)
		// after registration, redirect to login or dashboard
		router.push('/login')
	} catch (err) {
		apiError.value = auth.error || err?.response?.data?.detail || 'Error en el registro'
	} finally {
		loading.value = false
	}
}

function onVerify(token) {
	form.turnstile_token = token
}
</script>

<style scoped lang="scss">
@use "@/scss/_core.scss" as *;

.register-page {
  min-height: 100vh;
  padding: clamp(1.5rem, 4vw, 3rem);
  display: grid;
  place-items: center;
  background:
    radial-gradient(circle at top right, color-mix(in srgb, var(--color-primary) 18%, transparent) 0, transparent 34%),
    linear-gradient(180deg, #23201c 0%, #3e3c38 100%);
}

.register-container {
  width: min(100%, 620px);
  padding: clamp(1.5rem, 3vw, 2.4rem);
  background: rgba(255, 255, 255, 0.97);
  border: 1px solid rgba(211, 208, 195, 0.8);
  border-radius: 24px;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.22);
}

.back-link,
.muted a {
  color: var(--color-primary);
  font-weight: 700;
  text-decoration: none;
}

.back-link:hover,
.muted a:hover {
  text-decoration: underline;
}

h1 {
  margin: 1rem 0 1.5rem;
  color: var(--color-dark);
  font-size: clamp(1.8rem, 3vw, 2.3rem);
  font-weight: 700;
}

.register-form {
  display: grid;
  gap: var(--spacer-md);
}

.form-group {
  display: grid;
  gap: 0.4rem;
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

.toggle-password,
.btn {
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

.toggle-password {
  border: 1px solid var(--color-light);
  background: var(--color-white);
  color: var(--color-dark);
}

.btn {
  border: 0;
}

.toggle-password:hover,
.btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.btn:disabled {
  opacity: 0.65;
  cursor: wait;
}

.btn-primary {
  background: var(--color-primary);
  color: var(--color-white);
}

.alert {
  padding: 0.85rem 1rem;
  border-radius: var(--radius-sm);
  background: color-mix(in srgb, var(--color-white) 86%, var(--color-danger) 14%);
  color: var(--color-dark);
}

.muted {
  margin: 1.5rem 0 0;
  color: var(--color-dark);
  opacity: 0.8;
  font-size: var(--text-sm);
  text-align: center;
}

@include media-breakpoint-down(md) {
  .password-field {
    grid-template-columns: 1fr;
  }

  .toggle-password,
  .btn {
    width: 100%;
  }
}
</style>
