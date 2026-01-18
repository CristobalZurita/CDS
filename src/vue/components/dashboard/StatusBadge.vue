<template>
  <span class="status-badge" :class="statusClass">
    {{ label || status }}
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: { type: String, default: 'unknown' },
  label: { type: String, default: '' }
})

const statusClass = computed(() => `status-${props.status || 'unknown'}`)
</script>

<style scoped>
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
  font-size: 0.75rem;
  background: #f3f4f6;
  color: #111827;
}
.status-pending {
  background: #fef3c7;
  color: #92400e;
}
.status-in_progress {
  background: #dbeafe;
  color: #1e40af;
}
.status-completed {
  background: #d1fae5;
  color: #065f46;
}
.status-cancelled {
  background: #fee2e2;
  color: #991b1b;
}
</style>
