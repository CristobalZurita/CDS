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
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: var(--admin-space-lg, 1.8rem);
  margin-bottom: var(--admin-space-xl, 2.4rem);
}

.stat-card {
  background: var(--cds-white);
  border-radius: var(--cds-radius-lg);
  padding: var(--admin-space-xl, 2.4rem);
  display: flex;
  align-items: center;
  gap: var(--admin-space-md, 1.2rem);
  box-shadow: var(--cds-shadow-sm);
  border: 1px solid var(--cds-border-card);
}

.stat-icon {
  font-size: var(--cds-text-3xl);
  width: 6rem;
  height: 6rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--cds-primary) 0%, var(--cds-orange-pastel) 100%);
  border-radius: var(--cds-radius-lg);
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  display: block;
  font-size: var(--cds-text-4xl);
  font-weight: 700;
  color: var(--cds-text-normal);
  line-height: 1;
}

.stat-label {
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0;
}
</style>
