<template>
  <section class="repairs-list">
    <RepairCard
      v-for="repair in repairs"
      :key="repair.id || repair.repair_number"
      :repair="repair"
      @open="$emit('open', $event)"
    />
    <p v-if="!repairs.length" class="empty">No hay reparaciones.</p>
  </section>
</template>

<script setup>
import RepairCard from './RepairCard.vue'

defineProps({
  repairs: { type: Array, default: () => [] }
})

defineEmits(['open'])
</script>

<style scoped>
.repairs-list {
  display: grid;
  gap: 1rem;
}
.empty {
  color: #6b7280;
}
</style>
