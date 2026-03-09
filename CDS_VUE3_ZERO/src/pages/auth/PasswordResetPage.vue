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

<style scoped>
.auth-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 1rem;
  background: linear-gradient(180deg, var(--cds-dark) 0%, #2f2b27 100%);
}

.auth-card {
  width: min(100%, 620px);
  padding: 1.25rem;
  border-radius: 1rem;
  background: color-mix(in srgb, var(--cds-white) 94%, transparent);
  border: 1px solid color-mix(in srgb, var(--cds-light) 70%, white);
}

.auth-title {
  margin: 0 0 1rem;
  font-size: var(--cds-text-2xl);
  line-height: var(--cds-leading-tight);
  color: var(--cds-text-normal);
}
</style>
