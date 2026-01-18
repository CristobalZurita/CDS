<template>
  <article class="repair-card">
    <header class="card-header">
      <div>
        <h4 class="card-title">{{ repair.title || repair.instrument || 'Reparacion' }}</h4>
        <p class="card-sub">Ticket {{ repair.id || repair.repair_number || '—' }}</p>
      </div>
      <StatusBadge :status="repair.status" :label="repair.status_label" />
    </header>

    <p class="card-desc">{{ repair.description || repair.problem_reported || 'Sin descripcion' }}</p>

    <footer class="card-footer">
      <span>Ingreso: {{ formatDate(repair.created_at) }}</span>
      <button class="link" type="button" @click="$emit('open', repair)">Ver</button>
    </footer>
  </article>
</template>

<script setup>
import StatusBadge from './StatusBadge.vue'

defineProps({
  repair: { type: Object, required: true }
})

defineEmits(['open'])

const formatDate = (value) => {
  if (!value) return '—'
  return new Intl.DateTimeFormat('es-CL').format(new Date(value))
}
</script>

<style scoped>
.repair-card {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 1rem;
  background: #fff;
}
.card-header {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
}
.card-title {
  margin: 0;
}
.card-sub {
  margin: 0.2rem 0 0;
  color: #6b7280;
  font-size: 0.85rem;
}
.card-desc {
  margin: 0.8rem 0 1rem;
  color: #374151;
}
.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
  color: #6b7280;
}
.link {
  background: transparent;
  border: none;
  color: #2563eb;
  cursor: pointer;
}
</style>
