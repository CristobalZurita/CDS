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

<style lang="scss" scoped>
@use "@/scss/_core.scss" as *;

.repair-card {
  border: 1px solid $color-gray-200-legacy;
  border-radius: $border-radius-lg;
  padding: $spacer-md;
  background: $color-white;
}

.card-header {
  display: flex;
  justify-content: space-between;
  gap: $spacer-md;
  align-items: center;
}

.card-title {
  margin: 0;
}

.card-sub {
  margin: 0.2rem 0 0;
  color: $color-gray-500-legacy;
  font-size: $text-sm;
}

.card-desc {
  margin: 0.8rem 0 $spacer-md;
  color: $color-gray-700-legacy;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: $text-sm;
  color: $color-gray-500-legacy;
}

.link {
  background: transparent;
  border: none;
  color: $color-link-blue-legacy;
  cursor: pointer;
}
</style>
