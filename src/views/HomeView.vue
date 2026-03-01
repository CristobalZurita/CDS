<template>
  <section class="home-view">
    <div class="home-card">
      <h1>Cirujano de Sintetizadores</h1>
      <p>Este es un contenedor base para vistas nuevas.</p>
      <router-link to="/" class="btn">Ir al Inicio</router-link>
    </div>
  </section>
</template>

<script setup>
</script>

<style scoped lang="scss">
@import "@/scss/_core.scss";

.home-view {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3rem 1.5rem;
}
.home-card {
  max-width: 520px;
  padding: 2rem;
  border: 1px solid $color-gray-200-legacy;
  border-radius: 16px;
  background: $color-white;
}
.btn {
  display: inline-block;
  margin-top: 1rem;
  padding: 0.6rem 1rem;
  background: $color-gray-900-legacy;
  color: $color-white;
  border-radius: 8px;
  text-decoration: none;
}
</style>
