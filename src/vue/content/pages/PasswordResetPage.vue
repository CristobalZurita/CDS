<template>
  <div class="password-reset-page">
    <div class="reset-container">
      <div class="reset-header">
        <img
          src="/images/logo/NUEVO_cirujano.webp"
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
