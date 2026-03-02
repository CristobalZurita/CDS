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
