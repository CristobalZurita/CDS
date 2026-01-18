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

<style scoped>
.analysis {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 1rem;
  background: #f9fafb;
}
pre {
  margin: 0.5rem 0 0;
  white-space: pre-wrap;
  word-break: break-word;
}
</style>
