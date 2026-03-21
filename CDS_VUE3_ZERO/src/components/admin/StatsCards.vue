<template>
  <div class="stats-cards">
    <article v-for="card in cards" :key="card.key" class="stat-card">
      <div class="stat-icon" aria-hidden="true">{{ card.icon }}</div>
      <div class="stat-info">
        <strong class="stat-value">{{ formatNumber(card.value) }}</strong>
        <p class="stat-label">{{ card.label }}</p>
      </div>
    </article>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  stats: { type: Object, default: () => ({}) }
})

const cards = computed(() => ([
  { key: 'users', label: 'Usuarios', icon: '👤', value: props.stats?.users },
  { key: 'clients', label: 'Clientes', icon: '🏢', value: props.stats?.clients },
  { key: 'repairs', label: 'Reparaciones', icon: '🔧', value: props.stats?.repairs }
]))

const formatNumber = (val) => {
  const num = Number(val)
  return Number.isFinite(num) ? num.toLocaleString('es-CL') : '0'
}
</script>

<style scoped>
.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(var(--admin-dashboard-stats-card-min, 320px), 1fr));
  gap: var(--admin-space-lg, 1.8rem);
}

.stat-card {
  background: var(--cds-surface-1);
  border-radius: var(--cds-radius-lg);
  padding: var(--admin-space-xl, 2.4rem);
  display: flex;
  align-items: center;
  gap: var(--admin-space-md, 1.2rem);
  box-shadow: var(--cds-shadow-sm);
  border: 1px solid var(--cds-border-card);
}

.stat-icon {
  font-size: var(--admin-text-3xl, var(--cds-text-3xl));
  width: calc(6rem * var(--admin-dashboard-scale, 1));
  height: calc(6rem * var(--admin-dashboard-scale, 1));
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--cds-surface-2);
  border-radius: var(--cds-radius-lg);
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.stat-value {
  display: block;
  font-size: var(--admin-text-4xl, var(--cds-text-4xl));
  font-weight: 700;
  color: var(--cds-text-normal);
  line-height: 1;
}

.stat-label {
  font-size: var(--admin-text-sm, var(--cds-text-sm));
  color: var(--cds-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.09em;
  margin: 0;
  font-weight: 700;
}
</style>
