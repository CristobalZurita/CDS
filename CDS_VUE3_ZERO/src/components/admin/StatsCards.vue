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
  background: var(--color-white, #fff);
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.stat-value {
  display: block;
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--color-primary, #ff6b35);
  line-height: 1;
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--color-gray-600, #666);
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
