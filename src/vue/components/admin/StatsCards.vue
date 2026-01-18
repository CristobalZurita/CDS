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

<style scoped lang="scss">
@import "/src/scss/_theming.scss";

.stats {
  display: grid;
  gap: 1.25rem;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  margin-bottom: 1.5rem;
}
.card {
  background: #fff;
  border: 1px solid rgba(62, 60, 56, 0.18);
  border-radius: 14px;
  padding: 1.35rem;
  text-align: center;
  box-shadow: 0 8px 18px rgba(62, 60, 56, 0.12);
}

.label {
  margin: 0 0 0.5rem;
  color: $text-muted;
  font-weight: 600;
  letter-spacing: 0.02em;
}

.value {
  font-size: 1.8rem;
  color: $brand-text;
}
</style>
