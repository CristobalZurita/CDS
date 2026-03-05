<template>
  <div class="stats">
    <div class="card">
      <p class="label">Usuarios</p>
      <strong class="value">{{ stats.users || 0 }}</strong>
    </div>
    <div class="card">
      <p class="label">Clientes</p>
      <strong class="value">{{ stats.clients || 0 }}</strong>
    </div>
    <div class="card">
      <p class="label">Reparaciones</p>
      <strong class="value">{{ stats.repairs || 0 }}</strong>
    </div>
  </div>
</template>

<script setup>
defineProps({
  stats: { type: Object, default: () => ({}) }
})
</script>
