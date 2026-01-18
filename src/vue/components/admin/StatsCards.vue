<template>
  <div class="stats">
    <div class="card">
      <p>Usuarios</p>
      <strong>{{ stats.users || 0 }}</strong>
    </div>
    <div class="card">
      <p>Clientes</p>
      <strong>{{ stats.clients || 0 }}</strong>
    </div>
    <div class="card">
      <p>Reparaciones</p>
      <strong>{{ stats.repairs || 0 }}</strong>
    </div>
  </div>
</template>

<script setup>
defineProps({
  stats: { type: Object, default: () => ({}) }
})
</script>

<style scoped>
.stats {
  display: grid;
  gap: 1rem;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
}
.card {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 1rem;
  text-align: center;
}
</style>
