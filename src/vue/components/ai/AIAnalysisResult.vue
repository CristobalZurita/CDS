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
