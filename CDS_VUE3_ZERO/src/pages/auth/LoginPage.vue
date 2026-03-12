<template>
  <main class="auth-page">
    <section class="auth-card auth-card--narrow">
      <h1 class="auth-title">Iniciar sesión</h1>
      <LoginForm />
      <p class="auth-back"><router-link to="/">Volver al inicio</router-link></p>
    </section>
  </main>
</template>

<script setup>
import LoginForm from '@/components/auth/LoginForm.vue'
</script>

<style scoped src="./commonAuthPage.css"></style>
