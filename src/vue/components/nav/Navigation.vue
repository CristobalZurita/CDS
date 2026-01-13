<template>
  <nav class="navigation">
    <div class="nav-logo">
      <img v-if="logo" :src="logo" :alt="label" class="logo-img">
      <span class="logo-label">{{ label }}</span>
    </div>
    <ul class="nav-menu">
      <li><router-link to="/">Inicio</router-link></li>
      <li><router-link to="/agendar">Agendar</router-link></li>
      <li><router-link to="/login">Ingresar</router-link></li>
    </ul>
  </nav>
</template>

<script setup>
defineProps({
  logo: { type: String, default: null },
  label: { type: String, default: 'Navigation' }
})
</script>

<style scoped>
.navigation {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background: #f5f5f5;
  border-bottom: 1px solid #e0e0e0;
}

.nav-logo {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.logo-img {
  max-height: 40px;
  width: auto;
}

.nav-menu {
  display: flex;
  list-style: none;
  gap: 2rem;
  margin: 0;
  padding: 0;
}

.nav-menu a {
  text-decoration: none;
  color: #333;
  font-weight: 500;
}

.nav-menu a:hover {
  color: #007bff;
}
</style>
