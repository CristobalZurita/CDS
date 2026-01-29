<template>
  <div class="status-editor">
    <label>Estado</label>
    <select :value="modelValue" @change="$emit('update:modelValue', $event.target.value)">
      <option v-for="opt in options" :key="opt.value" :value="opt.value">
        {{ opt.label }}
      </option>
    </select>
  </div>
</template>

<script setup>
defineProps({
  modelValue: { type: String, default: '' },
  options: { type: Array, default: () => [] }
})

defineEmits(['update:modelValue'])
</script>

<style lang="scss" scoped>
@import '@/scss/_core.scss';

.status-editor {
  display: grid;
  gap: 0.35rem;
}

select {
  padding: 0.4rem 0.6rem;
  border-radius: $border-radius-md;
  border: 1px solid $color-gray-200-legacy;
}
</style>
