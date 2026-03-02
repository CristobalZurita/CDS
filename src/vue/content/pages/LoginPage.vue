<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-header">
        <!-- Logo oficial desde /public/images/logo/ -->
        <img
          src="/images/logo/NUEVO_cirujano.webp"
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
</script>
