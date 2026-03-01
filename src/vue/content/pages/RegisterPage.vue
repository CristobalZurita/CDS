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
@import "@/scss/_core.scss";

.register-page { padding: 2rem; display:flex; justify-content:center }
.register-container { width: 100%; max-width: 560px; background: $color-white; padding: 2rem; border-radius: 8px }
.form-group { margin-bottom: 1rem }
.form-group input { width: 100%; padding: 0.6rem; border: 1px solid $color-gray-180-legacy; border-radius: 4px }
.password-field { display: flex; gap: 0.5rem; align-items: center; }
.toggle-password { border: 1px solid $color-gray-180-legacy; background: $color-gray-100-legacy; padding: 0.35rem 0.6rem; border-radius: 4px; font-size: 0.85rem; }
.muted { color:$color-gray-666-legacy; margin-top:1rem }
.alert { margin: 1rem 0 }
.back-link { display:inline-block; margin-bottom: 1rem; color:$color-dark; text-decoration:none; font-weight:600; }
</style>
