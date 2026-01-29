<template>
  <span class="marker">{{ label || code }}</span>
</template>

<script setup>
defineProps({
  code: { type: String, default: '' },
  label: { type: String, default: '' }
})
</script>

<style lang="scss" scoped>
@import '@/scss/_core.scss';

.marker {
  display: inline-flex;
  align-items: center;
  padding: 0.2rem 0.6rem;
  border-radius: $border-radius-pill;
  background: $color-sky-100-legacy;
  color: $color-sky-700-legacy;
  font-size: $text-2xs;
}
</style>
