<template>
  <div class="stats-cards">
    <div class="stat-card">
      <p class="stat-label">Usuarios</p>
      <strong class="stat-value">{{ formatNumber(stats.users) }}</strong>
    </div>
    <div class="stat-card">
      <p class="stat-label">Clientes</p>
      <strong class="stat-value">{{ formatNumber(stats.clients) }}</strong>
    </div>
    <div class="stat-card">
      <p class="stat-label">Reparaciones</p>
      <strong class="stat-value">{{ formatNumber(stats.repairs) }}</strong>
    </div>
  </div>
</template>

<script setup>
defineProps({
  stats: { type: Object, default: () => ({}) }
})

const formatNumber = (val) => {
  const num = Number(val)
  return Number.isFinite(num) ? num.toLocaleString('es-CL') : '0'
}
</script>

<style scoped>
.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  background: var(--cds-white);
  border-radius: var(--cds-radius-md);
  padding: var(--cds-space-lg);
  text-align: center;
  box-shadow: var(--cds-shadow-sm);
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--cds-shadow-md);
}

.stat-value {
  display: block;
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--cds-primary);
  line-height: 1;
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--cds-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0;
}

@media (max-width: 768px) {
  .stat-value {
    font-size: 2rem;
  }
}
</style>
