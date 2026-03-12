<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-header">
        <!-- Logo oficial desde /public/images/logo/ -->
        <img
          :src="useCloudinaryImage('/images/logo/NUEVO_cirujano.webp')"
          alt="Cirujano de Sintetizadores"
          class="login-logo"
        />
        <h1>Iniciar Sesión</h1>
      </div>

      <LoginForm />

      <div class="login-back">
        <router-link to="/" class="login-back-link">VOLVER AL INICIO</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import LoginForm from '@/vue/components/auth/LoginForm.vue'
import { useCloudinaryImage } from '@/composables/useCloudinary'
</script>

<style scoped lang="scss">
@use "@/scss/_core.scss" as *;

.login-page {
  min-height: 100vh;
  padding: clamp(1.5rem, 4vw, 3rem);
  display: grid;
  place-items: center;
  background:
    radial-gradient(circle at top left, color-mix(in srgb, var(--color-primary) 18%, transparent) 0, transparent 32%),
    linear-gradient(160deg, #201d1a 0%, #2f2b27 45%, #3e3c38 100%);
}

.login-container {
  width: min(100%, 520px);
  padding: clamp(1.4rem, 3vw, 2.25rem);
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid rgba(211, 208, 195, 0.75);
  border-radius: 24px;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.22);
}

.login-header {
  display: grid;
  justify-items: center;
  gap: 0.85rem;
  margin-bottom: 1.5rem;
  text-align: center;
}

.login-logo {
  width: min(220px, 55vw);
  height: auto;
}

.login-header h1 {
  margin: 0;
  color: var(--color-dark);
  font-size: clamp(1.75rem, 3vw, 2.25rem);
  font-weight: 700;
}

.login-back {
  margin-top: 1.5rem;
  text-align: center;
}

.login-back-link {
  color: var(--color-primary);
  font-size: var(--text-sm);
  font-weight: 700;
  letter-spacing: 0.08em;
  text-decoration: none;
}

.login-back-link:hover {
  text-decoration: underline;
}
</style>
