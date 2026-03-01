<template>
  <section class="analysis">
    <h4>Resultado IA</h4>
    <pre>{{ formatted }}</pre>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  result: { type: Object, default: () => ({}) }
})

const formatted = computed(() => JSON.stringify(props.result, null, 2))
</script>

<style lang="scss" scoped>
@use '@/scss/core' as *;

.analysis {
  border: 1px solid $color-gray-200-legacy;
  border-radius: $border-radius-lg;
  padding: $spacer-md;
  background: $color-gray-25-legacy;
}

pre {
  margin: $spacer-sm 0 0;
  white-space: pre-wrap;
  word-break: break-word;
}
</style>
