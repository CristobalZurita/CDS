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

.auth-back {
  margin: 1rem 0 0;
  text-align: center;
}

.auth-back a {
  color: var(--cds-primary);
  text-decoration: none;
  font-size: var(--cds-text-sm);
}

.auth-back a:hover {
  text-decoration: underline;
}
</style>
