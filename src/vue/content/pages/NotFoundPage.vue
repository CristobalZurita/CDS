<template>
  <section class="not-found container py-5 text-center">
    <p class="not-found__code mb-2">404</p>
    <h1 class="h3 mb-3">Página no encontrada</h1>
    <p class="text-muted mb-4">
      La ruta solicitada no existe o fue movida.
    </p>
    <router-link class="btn btn-primary" to="/">
      Volver al inicio
    </router-link>
  </section>
</template>

<script setup>
</script>

<style scoped>
.not-found__code {
  font-size: 3rem;
  font-weight: 700;
  color: var(--cds-primary, #ec6b00);
  line-height: 1;
}
</style>
