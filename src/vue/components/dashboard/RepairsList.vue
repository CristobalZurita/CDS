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

<style lang="scss" scoped>
@use "@/scss/_core.scss" as *;

.repairs-list {
  display: grid;
  gap: $spacer-md;
}

.empty {
  color: $color-gray-500-legacy;
}
</style>
