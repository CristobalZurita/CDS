<template>
  <main class="auth-page">
    <section class="auth-card">
      <h1 class="auth-title">Crear cuenta</h1>
      <RegisterForm />
      <p class="auth-back"><router-link to="/">Volver al inicio</router-link></p>
    </section>
  </main>
</template>

<script setup>
import RegisterForm from '@/components/auth/RegisterForm.vue'
</script>

<style scoped src="./commonAuthPage.css"></style>
