<template>
  <section class="repair-manager">
    <article v-for="repair in repairs" :key="repair.id" class="repair">
      <h4>{{ repair.title || repair.problem_reported || 'Reparacion' }}</h4>
      <RepairStatusEditor
        :model-value="repair.status"
        :options="statusOptions"
        @update:modelValue="$emit('update-status', { repair, status: $event })"
      />
    </article>
  </section>
</template>

<script setup>
import RepairStatusEditor from './RepairStatusEditor.vue'

defineProps({
  repairs: { type: Array, default: () => [] },
  statusOptions: { type: Array, default: () => [] }
})

defineEmits(['update-status'])
</script>

<style lang="scss" scoped>
@use "@/scss/_core.scss" as *;

.repair-manager {
  display: grid;
  gap: $spacer-md;
}

.repair {
  border: 1px solid $color-gray-200-legacy;
  border-radius: $border-radius-lg;
  padding: $spacer-md;
}
</style>
