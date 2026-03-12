<template>
  <main class="auth-page">
    <section class="auth-card">
      <h1 class="auth-title">Recuperar contraseña</h1>
      <PasswordResetForm />
    </section>
  </main>
</template>

<script setup>
import PasswordResetForm from '@/components/auth/PasswordResetForm.vue'
</script>

<style scoped src="./commonAuthPage.css"></style>
