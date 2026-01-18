<template>
  <div class="password-reset-page">
    <div class="reset-container">
      <div class="reset-header">
        <img
          src="/images/logo/NUEVO_cirujano.png"
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
</script>

<style scoped>
.password-reset-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #000;
  padding: 2rem;
}

.reset-container {
  background: #d3d0c3;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
  padding: 3rem 2rem;
  max-width: 520px;
  width: 100%;
  border: 2px solid #3e3c38;
}

.reset-header {
  text-align: center;
  margin-bottom: 2rem;
}

.reset-logo {
  max-width: 260px;
  width: 100%;
  margin-bottom: 1rem;
}

.reset-header h1 {
  font-family: 'Cervo Extrabold', 'Cervo Neue', sans-serif;
  font-size: 1.4rem;
  font-weight: 800;
  color: #3e3c38;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.muted {
  margin-top: 1.5rem;
  text-align: center;
  color: #3e3c38;
}

.muted a {
  color: #ec6b00;
  font-weight: 600;
  text-decoration: none;
}

.muted a:hover {
  text-decoration: underline;
}
</style>
