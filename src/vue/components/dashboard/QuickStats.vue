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

<style lang="scss" scoped>
@use '@/scss/core' as *;

.stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: $spacer-md;
}

.stat {
  border: 1px solid $color-gray-200-legacy;
  border-radius: $border-radius-lg;
  padding: 0.75rem;
  text-align: center;
}

.label {
  margin: 0;
  color: $color-gray-500-legacy;
  font-size: $text-2xs;
}

.value {
  margin: 0.3rem 0 0;
  font-size: $text-xl;
  font-weight: $fw-bold;
}
</style>
