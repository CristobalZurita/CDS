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
