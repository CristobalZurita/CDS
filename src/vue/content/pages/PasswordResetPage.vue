<template>
  <div class="password-reset-page">
    <div class="reset-container">
      <div class="reset-header">
        <img
          :src="useCloudinaryImage('/images/logo/NUEVO_cirujano.webp')"
          alt="Cirujano de Sintetizadores"
          class="reset-logo"
        />
        <h1>Recuperar contraseña</h1>
      </div>
      <PasswordReset />
      <p class="muted">
        ¿Recordaste tu clave? <router-link to="/login">Volver a iniciar sesión</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import PasswordReset from '@/vue/components/auth/PasswordReset.vue'
import { useCloudinaryImage } from '@/composables/useCloudinary'
</script>

<style scoped lang="scss">
@use "@/scss/_core.scss" as *;

.password-reset-page {
  min-height: 100vh;
  padding: clamp(1.5rem, 4vw, 3rem);
  display: grid;
  place-items: center;
  background:
    radial-gradient(circle at top center, color-mix(in srgb, var(--color-primary) 18%, transparent) 0, transparent 36%),
    linear-gradient(180deg, #23201c 0%, #3e3c38 100%);
}

.reset-container {
  width: min(100%, 560px);
  padding: clamp(1.5rem, 3vw, 2.4rem);
  background: rgba(255, 255, 255, 0.97);
  border: 1px solid rgba(211, 208, 195, 0.8);
  border-radius: 24px;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.22);
}

.reset-header {
  display: grid;
  justify-items: center;
  gap: 0.8rem;
  margin-bottom: 1.5rem;
  text-align: center;
}

.reset-logo {
  width: min(220px, 55vw);
  height: auto;
}

.reset-header h1 {
  margin: 0;
  color: var(--color-dark);
  font-size: clamp(1.75rem, 3vw, 2.2rem);
  font-weight: 700;
}

.muted {
  margin: 1.5rem 0 0;
  color: var(--color-dark);
  opacity: 0.8;
  font-size: var(--text-sm);
  text-align: center;
}

.muted a {
  color: var(--color-primary);
  font-weight: 700;
  text-decoration: none;
}

.muted a:hover {
  text-decoration: underline;
}
</style>
