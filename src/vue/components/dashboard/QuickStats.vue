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
