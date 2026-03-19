<template>
  <div v-if="message" class="error-banner" role="alert">
    <span class="error-icon">⚠️</span>
    <span>{{ message }}</span>
    <button class="error-close" @click="$emit('close')">×</button>
  </div>
</template>

<script setup>
defineProps({
  message: {
    type: String,
    default: ''
  }
})

defineEmits(['close'])
</script>

<style scoped>
.error-banner {
  display: flex;
  align-items: center;
  gap: var(--intake-error-gap, 0.75rem);
  padding: var(--intake-error-padding, 1rem);
  margin-bottom: var(--intake-error-margin-bottom, 1rem);
  background: var(--cds-invalid-bg);
  border: 1px solid var(--cds-invalid-border);
  border-radius: var(--cds-radius-md);
  color: var(--cds-invalid-text);
}

.error-close {
  margin-left: auto;
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0 0.25rem;
}
</style>
