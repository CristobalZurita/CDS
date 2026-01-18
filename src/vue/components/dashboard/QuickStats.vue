<template>
  <div class="stats">
    <div class="stat">
      <p class="label">Pendientes</p>
      <p class="value">{{ stats.pending || 0 }}</p>
    </div>
    <div class="stat">
      <p class="label">En Proceso</p>
      <p class="value">{{ stats.active || 0 }}</p>
    </div>
    <div class="stat">
      <p class="label">Completadas</p>
      <p class="value">{{ stats.completed || 0 }}</p>
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
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 1rem;
}
.stat {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 0.75rem;
  text-align: center;
}
.label {
  margin: 0;
  color: #6b7280;
  font-size: 0.8rem;
}
.value {
  margin: 0.3rem 0 0;
  font-size: 1.4rem;
  font-weight: 700;
}
</style>
