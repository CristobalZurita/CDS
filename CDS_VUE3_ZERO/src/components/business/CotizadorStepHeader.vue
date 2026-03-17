<template>
  <header class="step-header">
    <span class="step-badge">{{ badge }}</span>
    <h1>{{ title }}</h1>
    <p>
      <slot name="description" />
    </p>
  </header>
</template>

<script setup>
defineProps({
  badge: {
    type: String,
    required: true
  },
  title: {
    type: String,
    required: true
  }
})
</script>

<style scoped>
.step-badge {
  font-size: var(--cds-text-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--cds-primary);
}

.step-header {
  display: grid;
  gap: 0.25rem;
}

.step-header h1 {
  margin: 0;
  font-size: var(--cds-text-2xl);
  line-height: 1.2;
}

.step-header p {
  margin: 0;
  color: var(--cds-text-muted);
  font-size: var(--cds-text-sm);
}
</style>
