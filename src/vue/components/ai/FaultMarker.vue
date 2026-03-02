<template>
  <span class="marker">{{ label || code }}</span>
</template>

<script setup>
defineProps({
  code: { type: String, default: '' },
  label: { type: String, default: '' }
})
</script>
