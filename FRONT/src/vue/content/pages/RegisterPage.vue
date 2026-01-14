<template>
	<div class="register-page">
		<div class="register-container">
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
					<input v-model="form.password" type="password" required minlength="8" />
				</div>

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

const auth = useAuthStore()
const router = useRouter()

const form = reactive({ email: '', username: '', full_name: '', password: '', phone: '' })
const loading = ref(false)
const apiError = ref('')

async function handleRegister() {
	apiError.value = ''
	loading.value = true
	try {
		await auth.register(form)
		// after registration, redirect to login or dashboard
		router.push('/login')
	} catch (err) {
		apiError.value = auth.error || err?.response?.data?.detail || 'Error en el registro'
	} finally {
		loading.value = false
	}
}
</script>

<style scoped>
.register-page { padding: 2rem; display:flex; justify-content:center }
.register-container { width: 100%; max-width: 560px; background: #fff; padding: 2rem; border-radius: 8px }
.form-group { margin-bottom: 1rem }
.form-group input { width: 100%; padding: 0.6rem; border: 1px solid #ddd; border-radius: 4px }
.muted { color:#666; margin-top:1rem }
.alert { margin: 1rem 0 }
</style>
