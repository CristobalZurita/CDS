<template>
  <span class="status-badge" :class="statusClass">
    {{ label || status }}
  </span>
</template>

<script setup>
import { computed } from 'vue'
import { normalizeRepairStatus } from '@/utils/repairStatus'

const props = defineProps({
  status: { type: String, default: 'unknown' },
  label: { type: String, default: '' }
})

const statusClass = computed(() => `status-${normalizeRepairStatus(props.status || 'unknown')}`)
</script>

<style scoped lang="scss">
@use "@/scss/_core.scss" as *;

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
  font-size: 0.75rem;
  background: $color-gray-100-legacy;
  color: $color-gray-900-legacy;
}
.status-pending {
  background: $color-amber-100-legacy;
  color: $color-amber-700-legacy;
}
.status-in_progress {
  background: $color-blue-200-legacy;
  color: $color-blue-700-legacy;
}
.status-completed {
  background: $color-green-100-legacy;
  color: $color-green-800-legacy;
}
.status-cancelled {
  background: $color-red-100-legacy;
  color: $color-red-800-legacy;
}
.status-ingreso,
.status-diagnostico,
.status-presupuesto,
.status-aprobado {
  background: $color-amber-100-legacy;
  color: $color-amber-700-legacy;
}
.status-en_trabajo,
.status-listo {
  background: $color-blue-200-legacy;
  color: $color-blue-700-legacy;
}
.status-entregado,
.status-noventena,
.status-archivado {
  background: $color-green-100-legacy;
  color: $color-green-800-legacy;
}
.status-rechazado {
  background: $color-red-100-legacy;
  color: $color-red-800-legacy;
}
</style>
