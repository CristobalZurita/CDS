<template>
  <span class="marker">{{ label || code }}</span>
</template>

<script setup>
defineProps({
  code: { type: String, default: '' },
  label: { type: String, default: '' }
})
</script>

<style scoped>
.marker {
  display: inline-flex;
  align-items: center;
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
  background: #e0f2fe;
  color: #0369a1;
  font-size: 0.75rem;
}
</style>
